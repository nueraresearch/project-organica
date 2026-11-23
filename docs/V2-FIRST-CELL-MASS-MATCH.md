# Mass- and key-matched frozen membership — mass, allocation, or recency?

**Status:** `DIAGNOSTIC — TWO MATCHED FROZEN CONTROLS ON THE NULL WORLDS, NOT A CELL AND NOT A VERDICT`

**Question:** is the revision rule's −0.000465 offset explained by total mass, by how that mass is allocated across composites, or by a recency/selection advantage?

## 1. The two controls

The maintained arm holds **98.8** member edges in **39.0**
non-empty composites per null world; frozen holds **324.6** edges in
**126.2**. It differs in total mass *and* in which composites survive.

**Control 1, total mass.** Draw the maintained arm's total edge count at random from the whole frozen pool. Total mass is
equal; allocation across composites is free. Mean: **98.8** edges in
**73.0** composites.

**Control 2, mass and key count.** Draw the same total edge count, confined to a random subset of frozen composites of the
same non-empty size as maintained, at least one edge each. The chosen keys cannot always hold the full mass: the residual
shortfall is **1.80** edges per world. Mean: **97.0**
edges in **39.0** composites.

Both matched arms select their own β on the calibration band. `Δ = d_matched − d_maintained`; positive means maintained
is better than the control. The reading was fixed before the run: an interval including zero means the control
reproduces the maintained cost; above zero means the randomised dimension adds value; below zero means the random
control is better.

## 2. Per-seed result

| Seed | d maintained | d mass-matched | d key-matched | Δ mass | Δ keys |
|---|---|---|---|---|---|---|
| `20920101` | 0.000817000 | 0.000266000 | 0.000250000 | -0.000551000 | -0.000567000 |
| `20920102` | 0.000890000 | 0.000003000 | 0.000415000 | -0.000887000 | -0.000475000 |
| `20920103` | 0.001118000 | 0.000866000 | 0.000367000 | -0.000252000 | -0.000751000 |
| `20920104` | 0.001905000 | 0.001047000 | 0.001475000 | -0.000858000 | -0.000430000 |
| `20920105` | 0.000888000 | 0.000416000 | 0.000662000 | -0.000472000 | -0.000226000 |
| `20920106` | 0.001113000 | 0.000243000 | 0.000722000 | -0.000870000 | -0.000391000 |
| `20920107` | 0.001439000 | 0.002316000 | 0.000731000 | 0.000877000 | -0.000708000 |
| `20920108` | -0.000190000 | -0.000587000 | -0.000338000 | -0.000397000 | -0.000148000 |
| `20920109` | 0.001622000 | 0.001695000 | -0.000188000 | 0.000073000 | -0.001810000 |
| `20920110` | 0.001461000 | 0.000734000 | 0.001379000 | -0.000727000 | -0.000082000 |
| `20920111` | 0.000538000 | 0.000019000 | -0.000291000 | -0.000519000 | -0.000829000 |
| `20920112` | 0.000692000 | -0.000010000 | -0.000096000 | -0.000702000 | -0.000788000 |
| `20920113` | 0.000882000 | -0.000028000 | -0.000012000 | -0.000910000 | -0.000894000 |
| `20920114` | 0.000880000 | -0.000147000 | 0.000229000 | -0.001027000 | -0.000651000 |
| `20920115` | 0.001302000 | 0.001225000 | 0.000463000 | -0.000077000 | -0.000839000 |
| `20920116` | 0.001114000 | 0.000028000 | 0.000318000 | -0.001086000 | -0.000796000 |
| `20920117` | 0.000291000 | 0.000432000 | 0.000172000 | 0.000141000 | -0.000119000 |
| `20920118` | -0.000926000 | -0.000332000 | 0.000425000 | 0.000594000 | 0.001351000 |
| `20920119` | 0.000232000 | -0.000028000 | 0.000497000 | -0.000260000 | 0.000265000 |
| `20920120` | 0.000871000 | -0.000414000 | -0.000186000 | -0.001285000 | -0.001057000 |

## 3. Summary

| Quantity | Mass-matched | Key-matched |
|---|---|---|
| Mean `d` | **0.000387200** | **0.000349700** |
| Mean member edges | 98.8 | 97.0 (shortfall 1.80) |
| Mean Δ | **-0.000459750** | **-0.000497250** |
| sd Δ | 0.000563111 | 0.000617994 |
| Positive Δ | 4 of 20 | 2 of 20 |
| 99% interval on Δ | `[-0.000752950, -0.000133800]` | `[-0.000811500, -0.000133300]` |
| Reading | **A MASS-MATCHED RANDOM ALLOCATION BEATS MAINTAINED** | **MAINTAINED SELECTION IS WORSE THAN RANDOM AT EQUAL MASS AND KEY COUNT** |

Mean `d` for maintained: **0.000846950**.

**Conclusion.** maintained selection is worse than random at equal mass and key count, so the offset is not a selection benefit at all.

## 4. What this establishes, and what it does not

It locates the revision offset between three candidates. If the mass-matched control reproduces maintained, the offset is
mass alone. If it does not but the key-matched control does, the difference is allocation — how the surviving mass is
spread across composites. If neither does, the retained selection itself carries the difference.

The key-matched arm is slightly lighter than maintained (the residual shortfall above), which would bias *in favour* of
the random control; the mass-matched arm has no such shortfall and reaches the same sign, so the conclusion does not rest
on it.

On the planted motif world the key-matched sign reverses: maintained selection beats the random control by
**0.002091** nats at equal mass and key count ([`V2-FIRST-CELL-PLANTED-SELECTION`](V2-FIRST-CELL-PLANTED-SELECTION.md)),
so the null result describes selection under noise, not an inherent inability to select signal.

It does not establish that random thinning is the right counterfactual, and a random subset discards any structure the
frozen set had. On a structureless world there is no structure to discard, which is why this is the right place to ask
the question; on a structured world the same controls would be weaker tests. It also says nothing about the cell's world.

## 5. Reproduction

```bash
python -m benchmarks.v2_first_cell_mass_match --write
python -m benchmarks.v2_first_cell_mass_match --check
```

Artifact: [`v2_first_cell_mass_match.json`](v2_first_cell_mass_match.json).
