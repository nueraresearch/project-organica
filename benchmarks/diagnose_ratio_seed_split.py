"""Exploratory diagnosis of the 20/5 split in block 2: does candidate-pool structure moderate the effect?

**Exploratory, not confirmatory.** The groups are defined by the outcome they are compared on, so this is a
hypothesis-generating diagnostic, not a test. Nothing here re-scores block 2's verdict or changes a criterion.

For each seed it pairs the cap-20 diagnostics already stored in the two block artifacts -- the count tie block, the
distinct-value counts under both orderings, the top-20 world-edge density under each ordering (their difference is the
"uplift"), asserted-set sizes -- against the paired coverage delta. It reports group comparisons across block 2's
20 improving and 5 non-improving seeds, correlations within each block and pooled, and the pooled block-2 correlation
replicated on block 1's independent 25 seeds where it can be. Writes `docs/gate13_ratio_seed_split.json`.
"""
from __future__ import annotations

import json
import math
import random
import statistics as st
from pathlib import Path

VARS = ["delta", "uplift", "C_top20", "R_top20", "count_tie_share", "count_tie_rows", "ratio_tie_share",
        "C_distinct", "R_distinct", "distinct_ratio", "C_prec", "C_asserted", "R_asserted"]


def load(path: str, block: str) -> list[dict]:
    art = json.loads(Path(path).read_text())
    cells = {(r["arm"], r["cap"], r["seed"]): r for r in art["raw"]}
    out = []
    for s in art["seeds"]:
        c, r = cells[("C", 20, s)], cells[("R", 20, s)]
        out.append({
            "block": block, "seed": s,
            "C_cov": c["coverage"], "R_cov": r["coverage"], "delta": round(r["coverage"] - c["coverage"], 4),
            "uplift": round(r["top_k"]["20"] - c["top_k"]["20"], 4),
            "C_top20": c["top_k"]["20"], "R_top20": r["top_k"]["20"],
            "count_tie_share": c["modal_tie_share"],
            "count_tie_rows": round(c["modal_tie_share"] * c["pool_rows"]),
            "ratio_tie_share": r["modal_tie_share"],
            "C_distinct": c["distinct_values"], "R_distinct": r["distinct_values"],
            "distinct_ratio": round(r["distinct_values"] / c["distinct_values"], 2),
            "C_prec": c["precision"], "C_asserted": c["asserted"], "R_asserted": r["asserted"],
        })
    return out


def pearson(xs, ys):
    mx, my = st.fmean(xs), st.fmean(ys)
    sx = math.sqrt(sum((x - mx) ** 2 for x in xs))
    sy = math.sqrt(sum((y - my) ** 2 for y in ys))
    if sx == 0 or sy == 0:
        return float("nan")
    return sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / (sx * sy)


def spearman(xs, ys):
    def ranks(v):
        order = sorted(range(len(v)), key=lambda i: v[i])
        r = [0.0] * len(v)
        i = 0
        while i < len(v):
            j = i
            while j + 1 < len(v) and v[order[j + 1]] == v[order[i]]:
                j += 1
            avg = (i + j) / 2 + 1
            for k in range(i, j + 1):
                r[order[k]] = avg
            i = j + 1
        return r
    return pearson(ranks(xs), ranks(ys))


def perm_p(members, var, reps=20000, seed=0):
    a = [m[var] for m in members if m["delta"] > 0]
    b = [m[var] for m in members if m["delta"] <= 0]
    if not a or not b:
        return None, None, None
    obs = st.fmean(a) - st.fmean(b)
    pool = [m[var] for m in members]
    rng, n_a, hits = random.Random(seed), len(a), 0
    for _ in range(reps):
        rng.shuffle(pool)
        if abs(st.fmean(pool[:n_a]) - st.fmean(pool[n_a:])) >= abs(obs) - 1e-12:
            hits += 1
    return round(obs, 4), round(hits / reps, 4), (len(a), len(b))


def boot_r(xs, ys, reps=10000, seed=0):
    rng, n, out = random.Random(seed), len(xs), []
    for _ in range(reps):
        idx = [rng.randrange(n) for _ in range(n)]
        out.append(pearson([xs[i] for i in idx], [ys[i] for i in idx]))
    out.sort()
    return round(out[int(0.025 * reps)], 3), round(out[int(0.975 * reps) - 1], 3)


def main() -> None:
    b1 = load("docs/gate13_ratio_confirm.json", "block1")
    b2 = load("docs/gate13_ratio_block2.json", "block2")
    groups = {
        "block2_improved": [m for m in b2 if m["delta"] > 0],
        "block2_not": [m for m in b2 if m["delta"] <= 0],
    }
    table = {}
    for var in VARS[1:]:
        row = {"improved_mean": round(st.fmean(m[var] for m in groups["block2_improved"]), 4),
               "improved_median": round(st.median([m[var] for m in groups["block2_improved"]]), 4),
               "not_mean": round(st.fmean(m[var] for m in groups["block2_not"]), 4),
               "not_median": round(st.median([m[var] for m in groups["block2_not"]]), 4)}
        diff, p, _ = perm_p(b2, var)
        row["mean_diff"] = diff
        row["perm_p"] = p
        table[var] = row

    corr = {}
    for name, data in (("block1", b1), ("block2", b2), ("pooled", b1 + b2)):
        xs = [m["uplift"] for m in data]
        ys = [m["delta"] for m in data]
        corr[name] = {"n": len(data), "pearson": round(pearson(xs, ys), 3),
                      "spearman": round(spearman(xs, ys), 3),
                      "pearson_ci95": boot_r(xs, ys) if len(data) >= 10 else None,
                      "r_squared": round(pearson(xs, ys) ** 2, 3)}
    var_corr = {}
    for var in ("count_tie_share", "count_tie_rows", "R_distinct", "ratio_tie_share", "distinct_ratio", "C_prec"):
        xs = [m[var] for m in b2]
        ys = [m["delta"] for m in b2]
        var_corr[var] = {"pearson": round(pearson(xs, ys), 3), "spearman": round(spearman(xs, ys), 3)}

    def spread(data):
        d = [m["delta"] for m in data]
        return {"n": len(d), "mean": round(st.fmean(d), 4), "median": round(st.median(d), 4),
                "sd": round(st.stdev(d), 4), "min": min(d), "max": max(d),
                "positive": sum(1 for x in d if x > 0), "zero": sum(1 for x in d if x == 0),
                "negative": sum(1 for x in d if x < 0), "abs_gt_0p10": sum(1 for x in d if abs(x) > 0.10)}

    art = {
        "what": "exploratory diagnosis of the 20/5 split in block 2",
        "status": "EXPLORATORY, hypothesis-generating. Groups are defined by the outcome; nothing here re-scores a verdict.",
        "source": ["docs/gate13_ratio_confirm.json", "docs/gate13_ratio_block2.json"],
        "spread": {"block1": spread(b1), "block2": spread(b2)},
        "groups": {"improved": len(groups["block2_improved"]), "not": len(groups["block2_not"])},
        "group_table": table,
        "correlation_uplift_vs_delta": corr,
        "block2_variable_correlations": var_corr,
        "failing_seeds": [{"seed": m["seed"], "delta": m["delta"], "uplift": m["uplift"],
                           "count_tie_rows": m["count_tie_rows"], "R_distinct": m["R_distinct"],
                           "C_prec": m["C_prec"]} for m in groups["block2_not"]],
        "seeds": b1 + b2,
    }
    Path("docs/gate13_ratio_seed_split.json").write_text(json.dumps(art, indent=2) + "\n")

    print("spread block1:", art["spread"]["block1"])
    print("spread block2:", art["spread"]["block2"])
    print("\ngroup table (block2: 20 improved vs 5 not):")
    for var, row in table.items():
        print(f"  {var:<18} improved {row['improved_median']:>8} | not {row['not_median']:>8} | "
              f"diff {row['mean_diff']:>8} | perm p {row['perm_p']}")
    print("\nuplift vs delta correlation:")
    for name, c in corr.items():
        print(f"  {name:<7} n={c['n']:>3} r={c['pearson']:>6} rho={c['spearman']:>6} ci={c['pearson_ci95']} r2={c['r_squared']}")
    print("\nblock2 per-variable correlation with delta:")
    for var, c in var_corr.items():
        print(f"  {var:<18} r={c['pearson']:>6} rho={c['spearman']:>6}")
    print("\nfailing seeds:")
    for f in art["failing_seeds"]:
        print("  ", f)


if __name__ == "__main__":
    main()
