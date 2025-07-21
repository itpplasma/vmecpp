add_library(fourier_asymmetric
    fourier_asymmetric.cc
    fourier_asymmetric.h
)

target_link_libraries(fourier_asymmetric
    PUBLIC
    sizes
    fourier_basis_fast_poloidal
    absl::span
)

set(vmecpp_sources "${vmecpp_sources}" "${CMAKE_CURRENT_SOURCE_DIR}/fourier_asymmetric.cc" PARENT_SCOPE)
