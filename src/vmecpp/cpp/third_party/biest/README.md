# BIEST (fetched dependency)

BIEST (https://github.com/dmalhotra/BIEST, Apache-2.0) and its SCTL
dependency (https://github.com/dmalhotra/SCTL, Apache-2.0) are fetched as
pinned archives in `//third_party:non_module_deps.bzl` (Bazel) and via
`FetchContent` (CMake); only the build overlays, local patches, and our
tests live in this repository.

Local patch (`warm_start.patch`): warm-start the iterative solve in
`ExtVacuumField::ComputeBplasma` from the previous sigma solution (SCTL's
GMRES natively accepts a non-empty initial guess; upstream never passes
one). This cuts the solve cost when the boundary changes little between
calls, as in the free-boundary VMEC iteration.

The FFT provider is Intel MKL's FFTW3 interface (see
`//third_party/mkl`); FFTW itself is GPL and cannot be linked into the
MIT-licensed VMEC++.

CMake builds enable BIEST by default on Linux x86-64 and disable it on other
platforms, including Apple and Linux ARM, where the pinned MKL SDK is unavailable. Set `VMECPP_ENABLE_BIEST=ON` and `MKLROOT`
explicitly to select an installed MKL SDK. With BIEST disabled, NESTOR remains
available and choosing BIEST, including as a diagnostic shadow solver, returns
an explicit unsupported-feature error. The native extension exposes the
build feature `biest_available`; no alternative solver is selected
silently. Bazel's current Linux build includes BIEST.
