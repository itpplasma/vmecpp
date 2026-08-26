"""Output-independent VMEC geometry for C++, NumPy, and JAX clients."""

from __future__ import annotations

import dataclasses

import jax
import jax.numpy as jnp
import numpy as np

from vmecpp.cpp import _vmecpp  # type: ignore


@jax.tree_util.register_pytree_node_class
@dataclasses.dataclass(frozen=True)
class Geometry:
    """The minimal VMEC equilibrium geometry in the internal product basis."""

    toroidal_flux: jax.Array
    poloidal_flux: jax.Array
    r_cc: jax.Array
    r_ss: jax.Array
    r_sc: jax.Array
    r_cs: jax.Array
    z_sc: jax.Array
    z_cs: jax.Array
    z_cc: jax.Array
    z_ss: jax.Array
    lambda_sc: jax.Array
    lambda_cs: jax.Array
    lambda_cc: jax.Array
    lambda_ss: jax.Array
    nfp: int

    def tree_flatten(self):
        children = dataclasses.astuple(self)[:-1]
        return children, self.nfp

    @classmethod
    def tree_unflatten(cls, nfp, children):
        return cls(*children, nfp)  # pyright: ignore[reportCallIssue]


def _array(values, shape):
    array = np.asarray(values)
    if array.size == 0:
        array = np.zeros(shape)
    return jnp.asarray(array.reshape(shape))


def from_cpp(geometry) -> Geometry:
    """Copy a C++ geometry snapshot into a JAX pytree."""
    dimensions = geometry.dimensions
    shape = (dimensions.ns, dimensions.mpol, dimensions.ntor + 1)
    coefficients = geometry.coefficients
    return Geometry(
        jnp.asarray(geometry.toroidal_flux),
        jnp.asarray(geometry.poloidal_flux),
        _array(coefficients.r_cc, shape),
        _array(coefficients.r_ss, shape),
        _array(coefficients.r_sc, shape),
        _array(coefficients.r_cs, shape),
        _array(coefficients.z_sc, shape),
        _array(coefficients.z_cs, shape),
        _array(coefficients.z_cc, shape),
        _array(coefficients.z_ss, shape),
        _array(coefficients.lambda_sc, shape),
        _array(coefficients.lambda_cs, shape),
        _array(coefficients.lambda_cc, shape),
        _array(coefficients.lambda_ss, shape),
        dimensions.nfp,
    )


def make(output) -> Geometry:
    """Construct geometry from the result of the low-level C++ ``run`` call."""
    return from_cpp(_vmecpp.make_geometry(output))


def _interpolate(values, s):
    ns = values.shape[0]
    scaled = s * (ns - 1)
    inner = jnp.clip(jnp.floor(scaled).astype(int), 0, ns - 2)
    weight = scaled - inner
    return (1.0 - weight) * values[inner] + weight * values[inner + 1]


def _values(geometry: Geometry, coordinates: jax.Array) -> jax.Array:
    s, theta, zeta = coordinates
    mpol = geometry.r_cc.shape[1]
    ntor = geometry.r_cc.shape[2] - 1
    m = jnp.arange(mpol)[:, None]
    n = jnp.arange(ntor + 1)[None, :] * geometry.nfp
    cos_m = jnp.cos(m * theta)
    sin_m = jnp.sin(m * theta)
    cos_n = jnp.cos(n * zeta)
    sin_n = jnp.sin(n * zeta)

    def series(cc, ss, sc, cs):
        coefficients = (
            _interpolate(cc, s) * cos_m * cos_n
            + _interpolate(ss, s) * sin_m * sin_n
            + _interpolate(sc, s) * sin_m * cos_n
            + _interpolate(cs, s) * cos_m * sin_n
        )
        return jnp.sum(coefficients)

    return jnp.asarray(
        [
            series(geometry.r_cc, geometry.r_ss, geometry.r_sc, geometry.r_cs),
            series(geometry.z_cc, geometry.z_ss, geometry.z_sc, geometry.z_cs),
            series(
                geometry.lambda_cc,
                geometry.lambda_ss,
                geometry.lambda_sc,
                geometry.lambda_cs,
            ),
            _interpolate(geometry.toroidal_flux, s),
            _interpolate(geometry.poloidal_flux, s),
        ]
    )


def evaluate(geometry: Geometry, coordinates: jax.Array) -> jax.Array:
    """Return shape ``(5, 4)``: values and derivatives in ``s, theta, zeta``.

    Rows are ``R``, ``Z``, ``lambda``, toroidal flux, and poloidal flux. Since
    this function uses only JAX operations, JAX supplies VJPs for the complete
    geometry pytree and for the evaluation coordinates.
    """
    values = _values(geometry, coordinates)
    derivatives = jax.jacfwd(_values, argnums=1)(geometry, coordinates)
    return jnp.concatenate((values[:, None], derivatives), axis=1)
