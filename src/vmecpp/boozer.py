"""Boozer coordinates of a converged VMEC++ equilibrium, with exact derivatives.

:class:`BoozerTransform` runs the transformation of booz_xform
(https://github.com/hiddenSymmetries/booz_xform) in C++ on the spectra of a
:class:`vmecpp.VmecWOut`, so the Boozer spectra come straight from an in-memory
solve without a ``wout`` file. Nothing is computed unless it is called.

The transform also provides its exact tangent (:meth:`BoozerTransform.jvp`) and
adjoint (:meth:`BoozerTransform.vjp`) with respect to the wout spectra it reads,
``rmnc, zmns, lmns, bmnc, bsubumnc, bsubvmnc`` and ``iotas``. Through
:meth:`BoozerTransform.jax` it is a JAX function with a custom VJP, so that it
composes with the differentiable ``vmecpp.run`` (an Enzyme-enabled build): under
``jax.grad`` the wout spectra of a traced boundary come from the implicit adjoint
of the solve and the JAX output stage, and a cotangent on ``bmnc_b`` is pulled
back to the boundary coefficients.

Only stellarator-symmetric equilibria are supported. The derivatives are those of
the discrete transform, at the given ``mboz``, ``nboz`` and angle grid, and are
smooth while the Jacobian of the map from VMEC to Boozer angles keeps its sign.
booz_xform reads ``bsubumnc`` for the modes with ``m != 0`` and ``bsubvmnc`` only
for ``m = 0``, so the derivative with respect to ``bsubvmnc`` vanishes for the
other modes; for a converged equilibrium the two determine the same scalar
potential, and the exact derivative inherits this choice.
"""

from __future__ import annotations

from collections.abc import Sequence
from typing import Any

import jax
import jax.numpy as jnp
import numpy as np

from vmecpp.cpp import _vmecpp  # type: ignore

INPUT_FIELDS = ("rmnc", "zmns", "lmns", "bmnc", "bsubumnc", "bsubvmnc", "iotas")
"""The wout spectra the transform reads, in the layout of :class:`vmecpp.VmecWOut`."""

OUTPUT_FIELDS = (
    "bmnc_b",
    "rmnc_b",
    "zmns_b",
    "numns_b",
    "gmnc_b",
    "iota_b",
    "boozer_g",
    "boozer_i",
)
"""The Boozer spectra, one column per selected surface, and iota, G and I there."""


def _as_int_list(values) -> list[int]:
    return [round(float(v)) for v in np.asarray(values).ravel()]


class BoozerTransform:
    """The Boozer transform for one mode table, set of surfaces and resolution.

    Args:
        wout: A :class:`vmecpp.VmecWOut` that supplies ``nfp``, ``ns`` and the
            mode tables ``xm, xn, xm_nyq, xn_nyq``.
        mboz: Number of poloidal Boozer modes; ``m_B`` runs from 0 to ``mboz - 1``
            as in booz_xform.
        nboz: Maximum toroidal Boozer mode number ``n_B / nfp``.
        surfaces: 0-based indices into the half grid without the axis, as
            booz_xform's ``compute_surfs``: surface ``j`` lies at
            ``s = (j + 1/2) / (ns - 1)``. Defaults to every half-grid surface.
    """

    def __init__(
        self,
        wout: Any,
        mboz: int,
        nboz: int,
        surfaces: Sequence[int] | None = None,
    ) -> None:
        if bool(getattr(wout, "lasym", False)):
            msg = "the Boozer transform supports stellarator-symmetric equilibria only"
            raise NotImplementedError(msg)
        ns = int(wout.ns)
        if surfaces is None:
            surfaces = range(ns - 1)
        self._cpp = _vmecpp.BoozerTransform(
            nfp=int(wout.nfp),
            ns=ns,
            xm=_as_int_list(wout.xm),
            xn=_as_int_list(wout.xn),
            xm_nyq=_as_int_list(wout.xm_nyq),
            xn_nyq=_as_int_list(wout.xn_nyq),
            surfaces=[int(j) for j in surfaces],
            mboz=int(mboz),
            nboz=int(nboz),
        )
        self.ns = ns
        self.mnmax = len(np.asarray(wout.xm))
        self.mnmax_nyq = len(np.asarray(wout.xm_nyq))

    @property
    def xm_b(self) -> np.ndarray:
        return np.asarray(self._cpp.xm_b)

    @property
    def xn_b(self) -> np.ndarray:
        return np.asarray(self._cpp.xn_b)

    @property
    def surfaces(self) -> np.ndarray:
        return np.asarray(self._cpp.surfaces)

    @property
    def s_b(self) -> np.ndarray:
        """Normalized toroidal flux of the selected surfaces."""
        return np.asarray(self._cpp.s_b)

    # Conversions between dicts of arrays and the C++ structs.

    def input_shapes(self) -> dict[str, tuple[int, ...]]:
        return {
            "rmnc": (self.mnmax, self.ns),
            "zmns": (self.mnmax, self.ns),
            "lmns": (self.mnmax, self.ns),
            "bmnc": (self.mnmax_nyq, self.ns),
            "bsubumnc": (self.mnmax_nyq, self.ns),
            "bsubvmnc": (self.mnmax_nyq, self.ns),
            "iotas": (self.ns,),
        }

    def output_shapes(self) -> dict[str, tuple[int, ...]]:
        spectrum = (len(self.xm_b), len(self.surfaces))
        profile = (len(self.surfaces),)
        return {
            name: spectrum if name.endswith("_b") and name != "iota_b" else profile
            for name in OUTPUT_FIELDS
        }

    @staticmethod
    def _to_cpp(values: dict[str, Any], fields, cls, shapes):
        struct = cls()
        for name in fields:
            value = values.get(name)
            if value is None:
                array = np.zeros(shapes[name])
            else:
                array = np.asarray(value, dtype=np.float64)
                if array.shape != shapes[name]:
                    msg = f"{name} has shape {array.shape}, expected {shapes[name]}"
                    raise ValueError(msg)
            setattr(struct, name, np.ascontiguousarray(array))
        return struct

    @staticmethod
    def _from_cpp(struct, fields) -> dict[str, np.ndarray]:
        return {name: np.asarray(getattr(struct, name)) for name in fields}

    def _input(self, spectra: dict[str, Any]):
        return self._to_cpp(
            spectra, INPUT_FIELDS, _vmecpp.BoozerInputSpectra, self.input_shapes()
        )

    def _output(self, spectra: dict[str, Any]):
        return self._to_cpp(
            spectra, OUTPUT_FIELDS, _vmecpp.BoozerOutputSpectra, self.output_shapes()
        )

    # The transform and its derivatives on NumPy arrays.

    def __call__(self, spectra: Any) -> dict[str, np.ndarray]:
        """Boozer spectra of a :class:`vmecpp.VmecWOut` or a dict of its spectra."""
        result = self._cpp.forward(self._input(wout_spectra(spectra)))
        return self._from_cpp(result, OUTPUT_FIELDS)

    def jvp(self, spectra: Any, tangent: dict[str, Any]) -> dict[str, np.ndarray]:
        """Tangent of the Boozer spectra; missing tangent fields count as zero."""
        result = self._cpp.jvp(self._input(wout_spectra(spectra)), self._input(tangent))
        return self._from_cpp(result, OUTPUT_FIELDS)

    def vjp(self, spectra: Any, cotangent: dict[str, Any]) -> dict[str, np.ndarray]:
        """Cotangent of the wout spectra; missing output cotangents count as zero."""
        result = self._cpp.vjp(
            self._input(wout_spectra(spectra)), self._output(cotangent)
        )
        return self._from_cpp(result, INPUT_FIELDS)

    def jax(self):
        """The transform as a JAX function of a dict of wout spectra.

        The forward pass and the VJP run in C++ through ``jax.pure_callback``; the
        function supports reverse-mode differentiation (``jax.grad``, ``jax.vjp``,
        ``jax.jacrev``), ``jax.jit`` and ``jax.vmap``. Use :meth:`jvp` for forward-mode products.
        """
        input_structs = {
            name: jax.ShapeDtypeStruct(shape, jnp.float64)
            for name, shape in self.input_shapes().items()
        }
        output_structs = {
            name: jax.ShapeDtypeStruct(shape, jnp.float64)
            for name, shape in self.output_shapes().items()
        }

        def forward_callback(spectra):
            return self(spectra)

        def vjp_callback(spectra, cotangent):
            return self.vjp(spectra, cotangent)

        @jax.custom_vjp
        def transform(spectra):
            return jax.pure_callback(
                forward_callback, output_structs, spectra, vmap_method="sequential"
            )

        def transform_fwd(spectra):
            return transform(spectra), spectra

        def transform_bwd(spectra, cotangent):
            bar = jax.pure_callback(
                vjp_callback,
                input_structs,
                spectra,
                cotangent,
                vmap_method="sequential",
            )
            return (bar,)

        transform.defvjp(transform_fwd, transform_bwd)

        def apply(spectra):
            selected = {
                name: jnp.asarray(spectra[name], dtype=jnp.float64)
                for name in INPUT_FIELDS
            }
            return transform(selected)

        return apply


def wout_spectra(wout: Any) -> dict[str, Any]:
    """The fields of :data:`INPUT_FIELDS` from a :class:`vmecpp.VmecWOut` or dict."""
    if isinstance(wout, dict):
        return {name: wout[name] for name in INPUT_FIELDS}
    return {name: getattr(wout, name) for name in INPUT_FIELDS}


def boozer_transform(
    wout: Any,
    mboz: int,
    nboz: int,
    surfaces: Sequence[int] | None = None,
) -> dict[str, np.ndarray]:
    """Boozer spectra of a :class:`vmecpp.VmecWOut`, with the mode table and grid.

    Returns the fields of :data:`OUTPUT_FIELDS` together with ``xm_b``, ``xn_b``,
    ``surfaces`` and ``s_b``.
    """
    transform = BoozerTransform(wout, mboz, nboz, surfaces)
    result = transform(wout)
    result.update(
        xm_b=transform.xm_b,
        xn_b=transform.xn_b,
        surfaces=transform.surfaces,
        s_b=transform.s_b,
    )
    return result
