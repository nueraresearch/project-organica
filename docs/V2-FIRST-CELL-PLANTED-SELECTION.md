# The matched controls on the planted motif world — does selection capture signal?

**Status:** `DIAGNOSTIC — THE MATCHED CONTROLS ON THE PLANTED MOTIF WORLD, NOT A CELL AND NOT A VERDICT`

**Question:** on a world where the composite is the only evidence for the held-out transition, does maintained selection beat random frozen membership at equal mass and key count?

## 1. The world and the controls

training repeats five three-tag motifs a->b->c; the held-out stream asks for a->c, the motif closure read forwards, which training never showed. The world and its ten measurement seeds are the positive control's, reused by
restatement; no new seed is spent. Both controls are the null diagnostic's: draw the maintained arm's total edge count at
random from the frozen pool (free allocation), and draw the same total confined to a random subset of frozen composites of
the maintained arm's non-empty size. Both select their own β on the calibration band.

`Δ = d_matched − d_maintained`; positive means maintained is better than the control. The reading was fixed before the
run: above zero means selection captures signal; including zero means no detectable advantage; below zero means selection
is worse than random even with signal.

## 2. Per-seed result

| Seed | d maintained | d mass-matched | d key-matched | Δ mass | Δ keys |
|---|---|---|---|---|---|
| `20930102` | -0.051675000 | -0.051723000 | -0.047415000 | -0.000048000 | 0.004260000 |
| `20930103` | -0.051689000 | -0.047415000 | -0.047804000 | 0.004274000 | 0.003885000 |
| `20930104` | -0.051689000 | -0.047405000 | -0.051723000 | 0.004284000 | -0.000034000 |
| `20930105` | -0.051675000 | -0.051723000 | -0.051675000 | -0.000048000 | 0.000000000 |
| `20930106` | -0.051675000 | -0.051689000 | -0.047405000 | -0.000014000 | 0.004270000 |
| `20930107` | -0.051689000 | -0.051723000 | -0.051723000 | -0.000034000 | -0.000034000 |
| `20930108` | -0.051689000 | -0.051723000 | -0.047415000 | -0.000034000 | 0.004274000 |
| `20930109` | -0.051689000 | -0.051710000 | -0.047415000 | -0.000021000 | 0.004274000 |
| `20930110` | -0.051689000 | -0.051689000 | -0.051689000 | 0.000000000 | 0.000000000 |
| `20930111` | -0.051689000 | -0.051710000 | -0.051675000 | -0.000021000 | 0.000014000 |

## 3. Summary

| Quantity | Mass-matched | Key-matched |
|---|---|---|
| Mean `d` | **-0.050851000** | **-0.049593900** |
| Mean Δ | **0.000833800** | **0.002090900** |
| sd Δ | 0.001815841 | 0.002218402 |
| Positive Δ | 2 of 10 | 6 of 10 |
| 99% interval on Δ | `[-0.000035600, 0.002555000]` | `[0.000413800, 0.003802300]` |
| Reading | **TOTAL MASS ALONE REPRODUCES THE MAINTAINED COST WITH SIGNAL** | **MAINTAINED SELECTION CAPTURES SIGNAL BEYOND MASS AND KEY COUNT** |

Mean `d` for maintained: **-0.051684800**. Mean member edges: maintained
29.0 in 19.0 composites; mass control
29.0 in 19.8; key control 28.8 in
19.0 (shortfall 0.20 edges per world).

**Compared with the null worlds:** key-matched Δ was **-0.000497250** on the null and is
**0.002090900** here; mass-matched Δ was
**-0.000459750** and is **0.000833800** here.

**Conclusion.** with a planted motif, maintained selection beats a random frozen control at equal mass and key count, unlike the null. The null's selection cost is a property of noise, not an inability to select signal.

## 4. What this establishes, and what it does not

It tests whether the maintained rule's selection has value when the world carries a signal the composite can see. The
planted world is deliberately the readout's best case — the held-out transition is the motif closure, absent from training
and bound only by the composite — so a selection advantage, if the rule has one, should show here.

It does not establish that the cell's world contains such motifs, and it does not test the engine's own selection: the
maintained membership is the readout's 20-cycle revision rule, applied to this world's detections. The positive control's
motifs are stable, so frozen and maintained membership may differ little; the key-matched control is the sharper test.

## 5. Reproduction

```bash
python -m benchmarks.v2_first_cell_planted_selection --write
python -m benchmarks.v2_first_cell_planted_selection --check
```

Artifact: [`v2_first_cell_planted_selection.json`](v2_first_cell_planted_selection.json).
