"""The Boozer transform against booz_xform, and its tangent and adjoint."""

import subprocess
import sys
from pathlib import Path

import jax
import jax.numpy as jnp
import numpy as np
import pytest

import vmecpp
from vmecpp import boozer
from vmecpp.cpp import _vmecpp  # type: ignore

jax.config.update("jax_enable_x64", True)

REPO_ROOT = Path(__file__).parent.parent
TEST_DATA_DIR = REPO_ROOT / "src" / "vmecpp" / "cpp" / "vmecpp" / "test_data"

MBOZ = 8
NBOZ = 6


@pytest.fixture(scope="module")
def wout() -> vmecpp.VmecWOut:
    indata = vmecpp.VmecInput.from_file(TEST_DATA_DIR / "cth_like_fixed_bdy.json")
    return vmecpp.run(indata, max_threads=1, verbose=False).wout


@pytest.fixture(scope="module")
def transform(wout) -> boozer.BoozerTransform:
    surfaces = [0, 1, wout.ns // 2, wout.ns - 2]
    return boozer.BoozerTransform(wout, MBOZ, NBOZ, surfaces)


def _random_like(shapes, seed, scales=None):
    generator = np.random.default_rng(seed)
    return {
        name: generator.standard_normal(shape)
        * (1.0 if scales is None else scales[name])
        for name, shape in shapes.items()
    }


def _input_scales(wout):
    """Tangents at a relative size comparable to each field."""
    return {
        name: float(np.max(np.abs(np.asarray(value))))
        for name, value in boozer.wout_spectra(wout).items()
    }


def _perturbed(wout, tangent, step):
    spectra = boozer.wout_spectra(wout)
    return {name: np.asarray(spectra[name]) + step * tangent[name] for name in spectra}


_BOOZ_XFORM_SCRIPT = """
import sys
import booz_xform
import numpy as np

wout_path, out_path, mboz, nboz, ns = sys.argv[1:]
b = booz_xform.Booz_xform()
b.verbose = 0
b.read_wout(wout_path)
b.mboz = int(mboz)
b.nboz = int(nboz)
b.compute_surfs = list(range(int(ns) - 1))
b.run()
np.savez(
    out_path,
    xm_b=b.xm_b, xn_b=b.xn_b, s_b=b.s_b, bmnc_b=b.bmnc_b, rmnc_b=b.rmnc_b,
    zmns_b=b.zmns_b, numns_b=b.numns_b, gmnc_b=b.gmnc_b, boozer_g=b.Boozer_G,
    boozer_i=b.Boozer_I, iota_b=b.iota,
)
"""


def test_matches_booz_xform(wout, tmp_path) -> None:
    pytest.importorskip("booz_xform")
    path = tmp_path / "wout_cth.nc"
    wout.save(path)
    # booz_xform runs in its own process: its wheel bundles an OpenMP runtime that
    # can clash with the one VMEC++ is linked against.
    subprocess.run(
        [
            sys.executable,
            "-c",
            _BOOZ_XFORM_SCRIPT,
            str(path),
            str(tmp_path / "booz.npz"),
            str(MBOZ),
            str(NBOZ),
            str(wout.ns),
        ],
        check=True,
    )
    reference = np.load(tmp_path / "booz.npz")
    surfaces = list(range(wout.ns - 1))

    result = boozer.boozer_transform(wout, MBOZ, NBOZ, surfaces)
    np.testing.assert_array_equal(result["xm_b"], reference["xm_b"])
    np.testing.assert_array_equal(result["xn_b"], reference["xn_b"])
    np.testing.assert_allclose(result["s_b"], reference["s_b"], rtol=1e-14)
    for name in boozer.OUTPUT_FIELDS:
        ref = reference[name]
        scale = np.max(np.abs(ref)) if np.any(ref) else 1.0
        np.testing.assert_allclose(
            result[name], ref, rtol=0.0, atol=1e-12 * scale, err_msg=name
        )


def test_rejects_invalid_surfaces(wout) -> None:
    with pytest.raises(ValueError, match="half grid"):
        boozer.BoozerTransform(wout, MBOZ, NBOZ, [wout.ns - 1])


@pytest.mark.parametrize("seed", [0, 1])
def test_jvp_matches_central_differences(wout, transform, seed) -> None:
    tangent = _random_like(transform.input_shapes(), seed, _input_scales(wout))
    jvp = transform.jvp(wout, tangent)
    step = 1.0e-6
    plus = transform(_perturbed(wout, tangent, step))
    minus = transform(_perturbed(wout, tangent, -step))
    for name in boozer.OUTPUT_FIELDS:
        difference = (plus[name] - minus[name]) / (2.0 * step)
        scale = np.max(np.abs(difference)) + 1e-300
        np.testing.assert_allclose(
            jvp[name], difference, rtol=0.0, atol=1e-7 * scale, err_msg=name
        )


@pytest.mark.parametrize("seed", [0, 1, 2])
def test_vjp_is_the_adjoint_of_the_jvp(wout, transform, seed) -> None:
    tangent = _random_like(transform.input_shapes(), seed)
    cotangent = _random_like(transform.output_shapes(), seed + 100)
    jvp = transform.jvp(wout, tangent)
    vjp = transform.vjp(wout, cotangent)
    left = sum(float(np.sum(jvp[k] * cotangent[k])) for k in boozer.OUTPUT_FIELDS)
    right = sum(float(np.sum(vjp[k] * tangent[k])) for k in boozer.INPUT_FIELDS)
    assert abs(left - right) <= 1e-12 * max(abs(left), abs(right))


def _reference_transform(transform, wout):
    """An independent JAX implementation of the stellarator-symmetric booz_xform
    algorithm, with direct trigonometric evaluation, differentiated by JAX."""
    ns = transform.ns
    nfp = int(wout.nfp)
    xm, xn = np.asarray(wout.xm, float), np.asarray(wout.xn, float)
    xm_nyq, xn_nyq = np.asarray(wout.xm_nyq, float), np.asarray(wout.xn_nyq, float)
    xm_b, xn_b = transform.xm_b.astype(float), transform.xn_b.astype(float)
    ntheta = 2 * (2 * MBOZ + 1)
    nzeta = 2 * (2 * NBOZ + 1)
    nu2 = ntheta // 2 + 1
    theta = np.repeat(np.arange(nu2) * 2 * np.pi / ntheta, nzeta)
    zeta = np.tile(np.arange(nzeta) * 2 * np.pi / (nfp * nzeta), nu2)
    weight = np.ones(nu2 * nzeta)
    weight[:nzeta] = 0.5
    weight[-nzeta:] = 0.5
    factor = np.full(len(xm_b), 2.0 / ((nu2 - 1) * nzeta))
    factor[0] *= 0.5
    hs = 1.0 / (ns - 1)
    sqrt_full = np.sqrt(hs * np.arange(ns))
    sqrt_full[0] = 1.0
    odd = (xm % 2 == 1)[:, None]
    m1 = xm == 1
    origin = np.flatnonzero((xm_nyq == 0) & (xn_nyq == 0))[0]
    safe_m = np.where(xm_nyq == 0, 1.0, xm_nyq)
    safe_n = np.where(xn_nyq == 0, 1.0, xn_nyq)

    def basis(m, n, t, z):
        angle = np.outer(t, np.ones_like(m)) * m - np.outer(z, np.ones_like(n)) * n
        return np.cos(angle), np.sin(angle)

    cos_g, sin_g = basis(xm, xn, theta, zeta)
    cos_n, sin_n = basis(xm_nyq, xn_nyq, theta, zeta)

    def half(full, j):
        sqrt_half = np.sqrt(hs * (j + 0.5))
        even = 0.5 * (full[:, j] + full[:, j + 1])
        odd_value = (
            0.5 * (full[:, j] / sqrt_full[j] + full[:, j + 1] / sqrt_full[j + 1])
        ) * sqrt_half
        if j == 0:
            extrapolated = (
                1.5 * full[:, 1] / sqrt_full[1] - 0.5 * full[:, 2] / sqrt_full[2]
            ) * sqrt_half
            odd_value = jnp.where(m1, extrapolated, odd_value)
        return jnp.where(odd[:, 0], odd_value, even)

    def apply(spectra):
        out = {name: [] for name in boozer.OUTPUT_FIELDS}
        for j in transform.surfaces:
            c = j + 1
            rh, zh = half(spectra["rmnc"], j), half(spectra["zmns"], j)
            lam = spectra["lmns"][:, c]
            bsubu, bsubv = spectra["bsubumnc"][:, c], spectra["bsubvmnc"][:, c]
            iota = spectra["iotas"][c]
            big_i, big_g = bsubu[origin], bsubv[origin]
            wmns = jnp.where(
                xm_nyq != 0,
                bsubu / safe_m,
                jnp.where(xn_nyq != 0, -bsubv / safe_n, 0.0),
            )
            r, z = cos_g @ rh, sin_g @ zh
            lam_g, lam_t, lam_z = sin_g @ lam, cos_g @ (xm * lam), -cos_g @ (xn * lam)
            w, w_t, w_z = (
                sin_n @ wmns,
                cos_n @ (xm_nyq * wmns),
                -cos_n @ (xn_nyq * wmns),
            )
            b = cos_n @ spectra["bmnc"][:, c]
            d = big_g + iota * big_i
            nu = (w - big_i * lam_g) / d
            nu_t = (w_t - big_i * lam_t) / d
            nu_z = (w_z - big_i * lam_z) / d
            theta_b = theta + lam_g + iota * nu
            zeta_b = zeta + nu
            jac = (1 + lam_t) * (1 + nu_z) + (iota - lam_z) * nu_t
            angle = jnp.outer(theta_b, xm_b) - jnp.outer(zeta_b, xn_b)
            cos_b, sin_b = jnp.cos(angle), jnp.sin(angle)
            a = weight * jac
            out["bmnc_b"].append(factor * (cos_b.T @ (a * b)))
            out["rmnc_b"].append(factor * (cos_b.T @ (a * r)))
            out["zmns_b"].append(factor * (sin_b.T @ (a * z)))
            out["numns_b"].append(factor * (sin_b.T @ (a * nu)))
            out["gmnc_b"].append(factor * (cos_b.T @ (a * d / b**2)))
            out["iota_b"].append(iota)
            out["boozer_g"].append(big_g)
            out["boozer_i"].append(big_i)
        return {
            name: jnp.stack(values, axis=-1)
            if name.endswith(("mnc_b", "mns_b"))
            else jnp.stack(values)
            for name, values in out.items()
        }

    return apply


def test_jvp_matches_jax_autodiff_of_an_independent_implementation(
    wout, transform
) -> None:
    reference = _reference_transform(transform, wout)
    spectra = {k: jnp.asarray(v) for k, v in boozer.wout_spectra(wout).items()}
    primal = reference(spectra)
    result = transform(wout)
    for name in boozer.OUTPUT_FIELDS:
        scale = np.max(np.abs(np.asarray(primal[name]))) + 1e-300
        np.testing.assert_allclose(
            result[name], primal[name], rtol=0.0, atol=1e-12 * scale, err_msg=name
        )
    tangent = _random_like(transform.input_shapes(), 7, _input_scales(wout))
    _, reference_tangent = jax.jvp(
        reference, (spectra,), ({k: jnp.asarray(v) for k, v in tangent.items()},)
    )
    jvp = transform.jvp(wout, tangent)
    for name in boozer.OUTPUT_FIELDS:
        ref = np.asarray(reference_tangent[name])
        scale = np.max(np.abs(ref)) + 1e-300
        np.testing.assert_allclose(
            jvp[name], ref, rtol=0.0, atol=1e-11 * scale, err_msg=name
        )


def test_jax_vjp_matches_the_cpp_vjp(wout, transform) -> None:
    apply = transform.jax()
    spectra = {k: jnp.asarray(v) for k, v in boozer.wout_spectra(wout).items()}
    cotangent = _random_like(transform.output_shapes(), 3)
    primal, pull_back = jax.vjp(apply, spectra)
    (bar,) = pull_back({k: jnp.asarray(v) for k, v in cotangent.items()})
    expected = transform.vjp(wout, cotangent)
    np.testing.assert_allclose(primal["bmnc_b"], transform(wout)["bmnc_b"], rtol=1e-15)
    for name in boozer.INPUT_FIELDS:
        np.testing.assert_allclose(bar[name], expected[name], rtol=1e-15, err_msg=name)

    # jax.jacrev maps the VJP over output cotangents.
    jacobian = jax.jacrev(lambda x: apply(x)["bmnc_b"][:2, 0])(spectra)
    for row in range(2):
        unit = np.zeros(transform.output_shapes()["bmnc_b"])
        unit[row, 0] = 1.0
        expected_row = transform.vjp(wout, {"bmnc_b": unit})
        np.testing.assert_allclose(
            jacobian["bmnc"][row], expected_row["bmnc"], rtol=1e-15, atol=0.0
        )


requires_enzyme = pytest.mark.skipif(
    not vmecpp.has_exact_force_jacobian(),
    reason="the VJP of run() needs an Enzyme-enabled build (VMECPP_ENABLE_ENZYME=ON)",
)


def _cth_like_input(ns: int, ftol: float, niter: int) -> vmecpp.VmecInput:
    source = vmecpp.VmecInput.from_file(
        REPO_ROOT / "examples" / "data" / "cth_like_fixed_bdy.json"
    )
    return source.model_copy(
        update={
            "ncurr": 0,
            "piota_type": "power_series",
            "ai": np.asarray([0.35, 0.15]),
            "ns_array": np.asarray([ns]),
            "ftol_array": np.asarray([ftol]),
            "niter_array": np.asarray([niter]),
        }
    )


@requires_enzyme
def test_boozer_spectrum_gradient_with_respect_to_the_boundary() -> None:
    """jax.grad of a Boozer quasi-symmetry residual through the solve, the JAX output
    stage and the Boozer adjoint, against a central difference of re-solves with the m=1
    gauge pinned as in the differentiable solve."""
    indata = _cth_like_input(ns=25, ftol=1.0e-14, niter=20000)
    ns = int(np.asarray(indata.ns_array)[-1])
    model = _vmecpp.VmecModel.create(indata._to_cpp_vmecindata(), ns)
    if not model.has_exact_force_jacobian:
        pytest.skip("needs an Enzyme-enabled build for the exact residual transpose")

    boundary = jnp.stack([jnp.asarray(indata.rbc), jnp.asarray(indata.zbs)])

    def with_boundary(value):
        return indata.model_copy(update={"rbc": value[0], "zbs": value[1]})

    reference_wout = vmecpp.run(indata, verbose=False).wout
    transform = boozer.BoozerTransform(reference_wout, MBOZ, NBOZ, [ns // 2, ns - 2])
    apply = transform.jax()
    non_symmetric = jnp.asarray(transform.xn_b != 0, dtype=jnp.float64)

    def residual(bmnc_b):
        return jnp.sum((non_symmetric[:, None] * bmnc_b) ** 2) / jnp.sum(bmnc_b[0] ** 2)

    def objective(value):
        wout = vmecpp.run(with_boundary(value), verbose=False).wout
        return residual(apply(boozer.wout_spectra(wout))["bmnc_b"])

    gradient = np.asarray(jax.grad(objective)(boundary))

    generator = np.random.default_rng(0)
    direction = np.zeros_like(np.asarray(boundary))
    low = generator.standard_normal((2, 3, 3))
    low[1, 0, 1] = 0.0  # zbs(m=0, n=0) is not a degree of freedom
    direction[:, :3, indata.ntor - 1 : indata.ntor + 2] = low
    direction *= 1.0e-3 * np.linalg.norm(boundary) / np.linalg.norm(direction)

    def pinned(value):
        cpp_input = with_boundary(value)._to_cpp_vmecindata()
        cpp_input.always_fix_m1_gauge = True
        wout = vmecpp.VmecWOut._from_cpp_wout(
            _vmecpp.run(cpp_input, verbose=_vmecpp.OutputMode.SILENT).wout
        )
        return float(residual(transform(wout)["bmnc_b"]))

    central = 0.5 * (
        pinned(np.asarray(boundary) + direction)
        - pinned(np.asarray(boundary) - direction)
    )
    directional = float(np.sum(gradient * direction))
    np.testing.assert_allclose(directional, central, rtol=2.0e-2)
