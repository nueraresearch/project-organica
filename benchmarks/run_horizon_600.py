import json
import sys
from pathlib import Path

REPO = Path(r"C:\Users\monte\anti\project-organica")
sys.path.insert(0, str(REPO))

from benchmarks.scale_ladder import run_rung

print("=" * 80)
print("RUNNING 600-CYCLE HORIZON: ARM 1 (BASELINE RUNG 0)")
print("=" * 80)
r0 = run_rung("0", cycles=600, seed=20261023)
print(f"Rung 0 complete! Inventory: {r0['inventory']['m5_total']}")

print("\n" + "=" * 80)
print("RUNNING 600-CYCLE HORIZON: ARM 2 (BURST ASSIMILATION _burst_30)")
print("=" * 80)
rb = run_rung("_burst_30", cycles=600, seed=20261023)
print(f"Burst complete! Inventory: {rb['inventory']['m5_total']}")

cum0 = r0["discovery_curve"]["cumulative"]
cumb = rb["discovery_curve"]["cumulative"]

print("\n" + "=" * 80)
print("600-CYCLE DISCOVERY EPOCHS (50 CYCLES EACH)")
print("=" * 80)
print(f"{'Epoch':<18}{'Base_Cum':<12}{'Base_New':<12}{'Burst_Cum':<12}{'Burst_New':<12}")

epochs_data = []
for ep in range(1, 13):
    c_idx = ep * 50 - 1
    prev_idx = (ep - 1) * 50 - 1
    b_cum = cum0[c_idx]
    b_new = cum0[c_idx] - (cum0[prev_idx] if ep > 1 else 0)
    u_cum = cumb[c_idx]
    u_new = cumb[c_idx] - (cumb[prev_idx] if ep > 1 else 0)
    print(f"Cycles {ep*50-49:03d}-{ep*50:03d}   {b_cum:<12}{b_new:<12}{u_cum:<12}{u_new:<12}")
    epochs_data.append({
        "epoch": ep,
        "cycles": f"{ep*50-49:03d}-{ep*50:03d}",
        "base_cum": b_cum,
        "base_new": b_new,
        "burst_cum": u_cum,
        "burst_new": u_new,
    })

inv0 = r0["inventory"]["m5_total"]
invb = rb["inventory"]["m5_total"]
delta_inv = invb - inv0
bursts_delivered = (600 - 1) // 30  # novelty arrives at cycles 30..570: 19 bursts
eff = round(delta_inv / bursts_delivered, 3)

print("\n" + "=" * 80)
print(f"SUMMARY: Baseline={inv0}, Burst={invb}, Delta=+{delta_inv}")
print(f"Assimilation Efficiency: {delta_inv} / {bursts_delivered} = {eff} items/burst")
reading = "Possibility B (Progressive Expansion)" if invb >= 135 else "Possibility A (Higher Attractor Saturation)"
print(f"VERDICT: {reading}")
print("=" * 80)

out_file = REPO / "docs" / "scale_horizon_600.json"
out_file.write_text(json.dumps({
    "cycles": 600,
    "seed": 20261023,
    "baseline": r0,
    "burst": rb,
    "epochs": epochs_data,
    "assimilation_efficiency": eff,
    "reading": reading,
}, indent=2), encoding="utf-8")
print(f"Wrote artifact to {out_file}")
