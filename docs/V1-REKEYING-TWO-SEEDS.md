# Does a direction-free identity help in more than one world?

**Status:** `OFFLINE COUNTERFACTUAL, TWO SEEDS. Rules simulated, not run. Authorises no code, no arm, no freeze.`

**Answer: yes, in both worlds.** The direction is the same at seed 20740101 and
seed 20900101: a direction-free key creates fewer identities, records fewer retirements, and converts orientation flips into
reinforcements. Both runs reproduce their store's identities and retirement rows before the key is swapped.

| Seed | Identities | Saved | Retirement rows | Saved | Flips | Mean live strength | Stable (count) | Validation |
|---|---|---|---|---|---|---|---|---|
| 20740101 | 177 | 19 | 186 | 16 | 55 | 0.8043 → 0.816 | 29 → 27 | pass |
| 20900101 | 138 | 13 | 128 | 11 | 18 | 1.2408 → 1.224 | 19 → 18 | pass |

## What this does and does not establish

- **Does:** the sign of the effect is not an accident of seed 20740101. The mechanism is the same one the specification's
  `cycle3` key is designed for: two orientations of one triangle stop being two alternating carriers.
- **Does not:** two seeds are not a distribution, and the stable column is a count, not a share: 177 and 138 carriers are
  different denominators. The magnitudes differ because the worlds differ (177 and
  138 carriers), and nothing here estimates a spread or a confidence interval. Read the table as a
  replication of the direction, not of the size.
- **Unchanged:** the two real gaps — no consumer of a carrier's cycle, no membership mutation. Re-keying gives an object a
  longer life, not a use.

## Provenance

Each column comes from its own artifact: [`docs/v1_rekeying_study.json`](docs/v1_rekeying_study.json) and
[`docs/v1_rekeying_study_20900101.json`](docs/v1_rekeying_study_20900101.json). The pages for the individual runs are
[`V1-REKEYING-STUDY`](docs/V1-REKEYING-STUDY.md) and [`V1-REKEYING-STUDY-20900101`](docs/V1-REKEYING-STUDY-20900101.md).
