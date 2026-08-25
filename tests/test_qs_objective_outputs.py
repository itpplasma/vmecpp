# SPDX-FileCopyrightText: 2024-present Proxima Fusion GmbH
# SPDX-License-Identifier: MIT
"""Behavioral checks for the complete QS output-state cotangent."""

from pathlib import Path

import numpy as np
import pytest

from vmecpp.cpp import _vmecpp  # type: ignore

SOLOVEV = Path(__file__).resolve().parents[1] / "examples" / "data" / "solovev.json"


def _objective(model, buco_weight, bvco_weight, aspect_weight):
    outputs = model.qs_harmonics()
    return float(
        np.dot(buco_weight, np.asarray(outputs["buco"], float))
        + np.dot(bvco_weight, np.asarray(outputs["bvco"], float))
        + aspect_weight * float(model.aspect)
    )


def test_qs_profile_and_aspect_state_cotangent_matches_directional_fd():
    """The added profile/aspect chain agrees with an independent state FD."""
    indata = _vmecpp.VmecINDATA.from_file(str(SOLOVEV))
    reference = _vmecpp.run(
        indata,
        max_threads=1,
        verbose=_vmecpp.OutputMode.SILENT,
    )
    oracle_model = _vmecpp.VmecModel.create(
        indata,
        11,
        _vmecpp.HotRestartState(wout=reference.wout, indata=indata),
    )
    if not hasattr(oracle_model, "exact_qs_objective_state_gradient"):
        pytest.skip("requires an Enzyme-enabled build")

    oracle_model.evaluate(2, 2, False)
    # Independent post-processing oracle: output_quantities.cc computes aspect
    # from cross_area_p, volume_p, Rmajor_p, and Aminor_p.  A fresh solver run
    # must agree with the direct current-state binding below.
    reference_geom = reference.threed1_geometric_magnetic
    np.testing.assert_allclose(
        oracle_model.aspect,
        reference_geom.aspect,
        rtol=1.0e-10,
        atol=1.0e-10,
    )
    np.testing.assert_allclose(
        reference_geom.aspect,
        reference_geom.Rmajor_p / reference_geom.Aminor_p,
        rtol=1.0e-14,
        atol=1.0e-14,
    )
    # Use an ordinary fresh single-resolution model for the derivative MRE;
    # the output-quantity oracle above is intentionally a separate check.
    model = _vmecpp.VmecModel.create(indata, 11)
    model.evaluate(2, 2, False)
    state = np.asarray(model.get_state(), float).copy()
    outputs = model.qs_harmonics()
    buco_weight = np.linspace(0.3, 1.1, np.asarray(outputs["buco"]).size)
    bvco_weight = np.linspace(-0.8, 0.2, np.asarray(outputs["bvco"]).size)
    aspect_weight = 0.7
    harmonic_bar = {
        key: np.zeros_like(np.asarray(outputs[key], float))
        for key in (
            "gmnc",
            "bmnc",
            "bsubumnc",
            "bsubvmnc",
            "bsupumnc",
            "bsupvmnc",
        )
    }
    harmonic_bar.update(
        buco=np.ascontiguousarray(buco_weight),
        bvco=np.ascontiguousarray(bvco_weight),
        aspect=np.asarray([aspect_weight]),
        # The fixed-profile iota output is accepted and contributes zero.
        iotas=np.zeros_like(np.asarray(outputs["iotas"], float)),
    )
    gradient = np.asarray(model.exact_qs_objective_state_gradient(harmonic_bar), float)

    direction = np.random.default_rng(27).standard_normal(state.size)
    direction /= np.linalg.norm(direction)
    eps = 1.0e-6
    model.set_state(np.ascontiguousarray(state + eps * direction))
    model.evaluate(2, 2, False)
    plus = _objective(model, buco_weight, bvco_weight, aspect_weight)
    model.set_state(np.ascontiguousarray(state - eps * direction))
    model.evaluate(2, 2, False)
    minus = _objective(model, buco_weight, bvco_weight, aspect_weight)
    model.set_state(np.ascontiguousarray(state))

    fd_directional = (plus - minus) / (2.0 * eps)
    exact_directional = float(np.dot(gradient, direction))
    assert abs(exact_directional - fd_directional) < 1.0e-5 * max(
        1.0, abs(fd_directional)
    )
    np.testing.assert_array_equal(np.asarray(model.get_state(), float), state)
