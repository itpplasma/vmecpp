# SPDX-FileCopyrightText: 2024-present Proxima Fusion GmbH <info@proximafusion.com>
#
# SPDX-License-Identifier: MIT
"""NESTOR and BIEST solve the same exterior Neumann problem, so with a converged free-
boundary equilibrium both must agree up to NESTOR's discretization error."""

from pathlib import Path

import pytest

import vmecpp
from vmecpp.cpp import _vmecpp  # type: ignore

REPO_ROOT = Path(__file__).parent.parent
TEST_DATA_DIR = REPO_ROOT / "src" / "vmecpp" / "cpp" / "vmecpp" / "test_data"


def _run_cth_like(method: str) -> vmecpp.VmecWOut:
    makegrid_params = vmecpp.MakegridParameters.from_file(
        TEST_DATA_DIR / "makegrid_parameters_cth_like.json"
    )
    makegrid_params.number_of_r_grid_points = 31
    makegrid_params.number_of_phi_grid_points = 36
    makegrid_params.number_of_z_grid_points = 20
    response = vmecpp.MagneticFieldResponseTable.from_coils_file(
        TEST_DATA_DIR / "coils.cth_like", makegrid_params
    )
    vmec_input = vmecpp.VmecInput.from_file(TEST_DATA_DIR / "cth_like_free_bdy.json")
    vmec_input.free_boundary_method = vmecpp.FreeBoundaryMethod(method)
    return vmecpp.run(vmec_input, response, verbose=False).wout


@pytest.mark.slow
def test_cth_like_free_boundary_biest_matches_nestor():
    if not _vmecpp.biest_available:
        with pytest.raises(RuntimeError, match="BIEST is unavailable in this build"):
            _run_cth_like("biest")
        return
    nestor = _run_cth_like("nestor")
    biest = _run_cth_like("biest")
    assert biest.volume == pytest.approx(nestor.volume, rel=1e-3)
    assert biest.volume == pytest.approx(0.306990, rel=2e-3)


@pytest.mark.slow
def test_axisymmetric_free_boundary_biest_matches_nestor():
    """Ntor = 0 gives nzeta = 1; BIEST lifts the boundary to a toroidal grid."""
    vmec_input = vmecpp.VmecInput.from_file(TEST_DATA_DIR / "solovev_free_bdy.json")
    vmec_input.mgrid_file = str(TEST_DATA_DIR / "mgrid_solovev.nc")
    assert vmec_input.ntor == 0

    if not _vmecpp.biest_available:
        vmec_input.free_boundary_method = vmecpp.FreeBoundaryMethod.BIEST
        with pytest.raises(RuntimeError, match="BIEST is unavailable in this build"):
            vmecpp.run(vmec_input, verbose=False)
        return
    vmec_input.free_boundary_method = vmecpp.FreeBoundaryMethod.NESTOR
    nestor = vmecpp.run(vmec_input, verbose=False).wout
    vmec_input.free_boundary_method = vmecpp.FreeBoundaryMethod.BIEST
    biest = vmecpp.run(vmec_input, verbose=False).wout

    assert biest.volume == pytest.approx(nestor.volume, rel=1e-3)
    assert biest.Rmajor_p == pytest.approx(nestor.Rmajor_p, rel=1e-3)
    assert biest.ctor == pytest.approx(nestor.ctor, rel=1e-3)
