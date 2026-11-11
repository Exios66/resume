# Wave Laboratory gauge spectrum: data validation

## Overall assessment: share with noted caveats

The recorded data are complete and reproduce the app's own statistics exactly. The gauge
sea carries about 30 % more variance than the requested JONSWAP sea, and neither the
length of the record nor the randomness of one seed is likely to explain that. The cause is
not yet confirmed.

## Data

- Source: the deployed Wave Laboratory, preset "Moderate sea · container ship" (JONSWAP,
  Hs 2.5 m, Tp 9 s, γ 3.3, direction 0°, spreading cos-2s with s = 10, seed 20240, wind
  11 m/s). Recorded headless in Chromium (SwiftShader WebGL) at 4× speed, Graphics Low, and
  exported with the app's own "Export CSV" button.
- File: `moderate-sea-container-ship-telemetry.csv`, 13,720 rows, `time_s` 0.0 to 1,371.9 s,
  one column per instrument (`gauge-1:eta` and the ship channels).

## Quality checks

| Check | Result |
| --- | --- |
| Missing values in `gauge-1:eta` | 0 |
| Sample interval | 0.1000 s throughout; no gaps, no repeats |
| Mean elevation | −0.036 m (removed before analysis) |
| Skewness, kurtosis | −0.013, 3.10: Gaussian, as a linear sea should be |

## Cross-check against the app's Statistics tab (same record)

| Quantity | App | Recomputed here |
| --- | --- | --- |
| Hm0 | 2.84 m | 2.85 m (4σ and spectral m0 agree) |
| H1/3 | 2.78 m | 2.78 m |
| Hmax | 4.89 m | 4.89 m |
| Tz | 7.2 s | 7.19 s (zero crossings), 7.21 s (spectral) |
| Waves | 190 | 190 |
| Tp | 8.5 s | 9.3 s (Welch bin centre; the bin width is 0.0098 Hz, so 9.0 s falls between bins) |

## Finding

- Measured m0 is 1.30 × the requested (2.5/4)² m², so Hm0 is 2.85 m against 2.50 m.
- Record-length variability: 2,000 Gaussian random seas with the requested spectrum, each
  1,372 s long, give Hs between 2.27 and 2.76 m (95 %). P(Hs ≥ 2.85) ≈ 0.003.
- Seed variability: the app draws one fixed set of Gaussian amplitudes per wavenumber cell
  (`src/ocean/cascades.ts`), so a seed fixes the realised energy. An approximate model of
  its 1,024 m cascade (dk = 2π/1024, cos-2s spreading, s = 10) gives realised Hs between
  2.28 and 2.73 m (95 %) across seeds. P(≥ 2.85) ≈ 0.002.
- The app's own test (`src/ocean/ocean.validation.ts`) accepts 0.9 ≤ Hm0/Hs ≤ 1.1. This
  record gives 1.14.
- Not confirmed: whether the excess comes from this seed, from the spreading or cascade
  hand-over, or from how the gauge samples the surface. Next step: rerun the app's
  validation test with seed 20240, then repeat the recording with two or three other seeds.

## Method

Welch periodogram over the full record: Hann window, 1,024 points (102.4 s), 50 % overlap,
25 segments, about 43 equivalent degrees of freedom. The 90 % band uses the χ²
(Wilson–Hilferty) interval. The target is the JONSWAP form with σ 0.07/0.09, normalised so
that 4√m0 = 2.5 m. Script: `spectrum_figure.py` in this folder.

## Caveats for any page that shows the figure

- The figure shows one seed and one 23-minute record.
- The excess energy is reported as measured. It is not explained yet, and it is not a claim
  about the app's physics in general.
