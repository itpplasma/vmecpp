# jVMEC Fourier Transform Analysis

Based on the bytecode analysis of FourierTransformsJava$1.run(), here's what I found:

## Arrays being transformed:
1. Symmetric arrays (always present):
   - rmncc (R symmetric cos)
   - zmnsc (Z symmetric sin) 
   - lmnsc (lambda symmetric sin)

2. Asymmetric arrays (only if lthreed=true):
   - rmnss (R asymmetric sin)
   - zmncs (Z asymmetric cos)
   - lmncs (lambda asymmetric cos)

## Transform pattern from bytecode:

From the bytecode, the transform appears to accumulate terms like:

1. R[0] += rmncc * cosnv        (symmetric baseline)
2. R[1] += rmnss * sinnv        (asymmetric, if lthreed)
3. R[2] += rmncc * sinnvn       (derivative terms)
4. R[3] += rmnss * cosnvn       (asymmetric derivative)

5. Z[4] += zmncs * sinnv        (asymmetric Z)
6. Z[5] += zmnsc * cosnv        (symmetric Z baseline)
7. Z[6] += zmncs * cosnvn       (asymmetric derivative)
8. Z[7] += zmnsc * sinnvn       (symmetric derivative)

9. L[8] += lmncs * sinnv        (asymmetric lambda)
10. L[9] += lmnsc * cosnv       (symmetric lambda baseline)
11. L[10] += lmncs * cosnvn     (asymmetric derivative)
12. L[11] += lmnsc * sinnvn     (symmetric derivative)

The key pattern seems to be:
- Symmetric terms use their natural parity (R/cos, Z/sin, L/sin)
- Asymmetric terms use opposite parity (R/sin, Z/cos, L/cos)
- Both use regular and derivative basis functions
