# Zenodo deposit package

**Status: both papers' packages prepared, decided, not deposited.** Every field below is filled in,
every bundle is built and checksummed, and every decision the checklist used
to leave open has been made — the owner's standing direction on 2026-10-31 was
*"do not deposit yet; use your best judgement on the rest"*. **Nothing here has
been uploaded.** Publishing remains the owner's action alone: Zenodo mints a
DOI when a record is published, and a DOI is public.

**Why Zenodo and not arXiv.** The owner's decision of 2026-10-30 was arXiv
first; the later decision superseded it, and Zenodo is the current venue. The
two are not exclusive — a Zenodo preprint DOI and an arXiv identifier can
co-exist on the same manuscript, and this package is written so that the
arXiv route can still be taken later without redoing the metadata.

## What is being deposited

| Record | Type | Version | Metadata file |
|---|---|---|---|
| The frozen Organica 1 engine and its evidence artifacts | software | **v0.11.0** | `zenodo/software-v0.11.0.json` |
| Paper 01 — Developmental structure formation | publication (preprint) | 1.0.0 | `zenodo/paper-01-preprint.json` |
| Paper 02 — Persistent structural provenance | publication (preprint) | 1.0.0 | `zenodo/paper-02-preprint.json` |

**The software record carries v0.11.0, archived from a commit.** It carried v0.10.0 until
2026-11-02, and that stopped being correct when Paper 01 gained §4.10: the capacity-1,000
result cites `docs/functional_structure_confirmatory.json` and
`docs/FUNCTIONAL-STRUCTURE-PREREGISTRATION.md`, both committed **after** the v0.10.0 tag, so a
v0.10.0 tree cannot carry the evidence its own manuscript cites —
`python benchmarks/deposit_bundle.py --check` reported **38 cited, 2 missing**. Cutting a
`v0.11.0` tag would fix it and is the owner's act, so the archive is taken from `HEAD` instead
and the manifest records the resolved commit SHA (`software_commit`). Nothing else about the
record changed, and the engine inside it is still frozen:
`organica/` is byte-identical to the v0.9.0 tag apart from the package
version string, and **v0.9.0 remains the archival reference for the engine
alone**. v0.10.0 is the release of the research package around that engine --
the instruments, the evidence artifacts and the two manuscripts -- and it is
the release that can carry the files a deposit needs.

`.zenodo.json` at the repository root is the file Zenodo's GitHub integration
reads when it mints a version DOI for a GitHub release. It carries the same
creator, license and community as the software record.

## The form, answered

### Every record

| Field | Value |
|---|---|
| Title | **the manuscript's own title, exactly as the PDF carries it.** A longer descriptive variant belongs in `description`: a record title that appears nowhere in the document is the drift the title guard exists to prevent, and `tests/test_pdf_titles.py` now fails if a record and its document disagree. The records for both papers carried such variants until 2026-11-02 and were reconciled. |
| Upload type | `software` for the engine; `publication` / `preprint` for the papers |
| Access right | `open` |
| Creators | Beebe, Jeremy Blain Thompson — Nuera RDL — ORCID `0009-0009-2394-9714` |
| Communities | Machine Learning — `a08bc0ac-2893-4afd-870a-a77bd348c84c` |
| Keywords | record-specific; see each metadata file |
| Related identifiers | the repository URL. The software record is identified by the archived commit SHA (`software_commit` in the deposit manifest), because no `v0.11.0` release object exists and the `v0.10.0` tag has no release URL to enter — see *The route* below. The two paper DOIs are added to the software record as `isDocumentedBy` once they exist. |
| Notes | see each metadata file — the notes carry the freeze statement and the deposit's file list |
| Version | the release tag (software) or `1.0.0` (papers) — entered in the form, not in the JSON |

### Licensing

The engine is **Apache-2.0**: `LICENSE` in the repository is Apache-2.0 and
`CITATION.cff` already declares it.

The two papers carry **CC-BY-4.0**, which is Zenodo's default for a textual
work and the usual choice for a preprint. **Decided on 2026-10-31** under the
owner's delegation: the papers are textual works, not software, and CC-BY is
the licence a reader expects of a preprint — reuse permitted, attribution
required. The engine stays **Apache-2.0**, which is what `LICENSE` and
`CITATION.cff` already declare. If the owner later prefers Apache-2.0 for the
manuscripts too, change the `license` field in both paper metadata files and
re-run `python benchmarks/zenodo_metadata.py`.

**Decided: the deposit order is the papers first.** A preprint DOI establishes
priority and can be cited in a journal submission, and the software record can
then carry `isDocumentedBy` links back to both papers. The reverse order would
leave the paper records pointing at a DOI that does not exist yet.

### The route — decided: manual deposit

Two facts were verified live on 2026-10-31, and both bear on the route:

- **The repository has zero webhooks.** Zenodo's GitHub integration installs
  a webhook on the repository it watches. There is none, so **the Zenodo
  GitHub app is not authorised**, and no release would be picked up
  automatically.
- **There is no v0.10.0 GitHub release.** `gh release list` shows releases
  only for v0.6.0, v0.7.0, v0.8.0 and v0.9.0; the `v0.10.0` *tag* is on the
  remote, but the release object was never created.

The release-based route therefore cannot mint anything today, and it would
require the owner to authorise the app — which is a step that would make
future releases mint DOIs without a further decision each time. **The manual
route is the decision:** deposit through the Zenodo web form, with the
metadata from the record files and the files from the bundles below. It
yields the same version-scoped DOI, it leaves the file list under the
owner's eyes, and it does not stand up an automatic minting pipeline that
nobody has asked for.

**A GitHub release for v0.10.0 is not cut.** Cutting one is the owner's act
and it is one step from publishing, so it was not done here. The repository's
own statements say which thing they mean, so the gap is recorded rather than
papered over: **0.10.0 is the latest cut version — dated, tagged and pushed —
and v0.9.0 is the latest published release.**

### The files

The bundles are built by one command:

```
python benchmarks/deposit_bundle.py
```

which writes `.scratch/deposit/`, one directory per record, each with its
files, a `SHA256SUMS` and a `DEPOSIT-MANIFEST.json`. The manifest is
`.scratch/deposit/MANIFEST.json`.

**Software record (v0.11.0).** the source tree at the archived commit, as one archive,
plus the checksums and the manifest:

| File | |
|---|---|
| `project-organica-v0.11.0.tar.gz` | `git archive` of the tree at the archived commit |
| `SHA256SUMS` | checksums of the record's files |
| `DEPOSIT-MANIFEST.json` | the record's metadata and its file list |

**Paper records.** Each carries the manuscript as PDF and as Markdown, its
figures as vector PDF, the checksums and the manifest. Paper 01 carries
`figure_p01_acquisition`, `figure_p01_adjacent_differences`,
`figure_p01_capacity_sweep`, `figure_p01_displacement_curve` and
`figure_p01_phase_k_families`; Paper 02 carries `figure_p02_cognition_window`,
`figure_p02_reconstruction_arms` and `figure_p02_self_sourcing`.

**The reproduction bundle is not a fourth record.** `.scratch/deposit/reproduction/`
holds `REPRODUCE.md`, `ENVIRONMENT.json`, both rendered PDFs and their `SHA256SUMS`. It
names the archived commit, the Python/pandoc/pdfLaTeX versions that built the papers, the
four commands that regenerate the figures and the PDFs in order, and each paper's expected
page count, size and hash. It is uploaded with the two paper records — it is the material a
reviewer needs in order to check one, not a deposit in its own right.

The PDF build is

```
python benchmarks/render_papers.py
```

which writes `papers/build/01_developmental_structure_formation.pdf` and
`papers/build/02_persistent_structural_provenance.pdf` (see
`docs/PDF-PIPELINE.md`); the figures are the same SVGs the repository holds,
converted to vector PDF by the same tool.

**The file list is checked against the manuscripts.** The deposit checklist
asked whether the deposit carries the artifacts the manuscript actually
cites. `benchmarks/deposit_bundle.py --check` parses both manuscripts for the
`docs/` artifacts they name and asks whether each is inside the tree the
software record carries:

```
python benchmarks/deposit_bundle.py --check
```

**38 artifacts are cited and 38 are present** in the archived tree. A
manuscript cannot cite evidence the software record does not carry.

### After the paper DOIs exist

Add each preprint DOI to the software record as `isDocumentedBy`, and add the
software record's DOI to each paper as `isSupplementedBy`. The paper metadata
files carry the repository URL for now, because the software DOI does not
exist yet and a guessed DOI is a false claim.

## Before publishing — checklist

**Decided and done on 2026-10-31** (the owner's delegation, *"do not deposit
yet; use your best judgement on the rest"*):

- [x] **The papers' licence: CC-BY-4.0.** Zenodo's default for a textual
      work and the expected licence for a preprint. The engine stays
      Apache-2.0.
- [x] **The route: manual deposit** through the Zenodo web form. The Zenodo
      GitHub app is **not** authorised — the repository has **zero
      webhooks**, verified live — so the release-based route could not mint
      anything, and standing the app up would create an automatic minting
      pipeline nobody asked for.
- [x] **No GitHub release is cut for v0.10.0.** It is the owner's act and
      one step from publishing. The repository now says plainly that 0.10.0
      is the latest *cut version* and v0.9.0 the latest *published release*.
- [x] **The order: the papers first**, so their DOIs exist before the
      software record links to them with `isDocumentedBy`.
- [x] **`python benchmarks/zenodo_metadata.py` passes.** All four metadata
      files conform to Zenodo's published deposit schema.
- [x] **The file list is checked against the manuscripts.**
      `python benchmarks/deposit_bundle.py --check`: **38 artifacts cited,
      38 present** in the archived tree.
- [x] **The software record is archived from the commit, not the stale tag** (2026-11-02): 38 cited artifacts, 38 present.
- [x] **The bundles are built and checksummed** by
      `python benchmarks/deposit_bundle.py`, under `.scratch/deposit/`.
- [x] **The reproduction bundle is built** (2026-11-02): commit, environment, the four
      regenerating commands and both PDFs, with checksums, under
      `.scratch/deposit/reproduction/`; `tests/test_deposit_bundle.py` asserts that the
      PDFs it carries are the same files the paper records list.

**Still the owner's, and only these:**

- [ ] **Publish.** Upload each record's bundle and the four metadata files, with the reproduction bundle's `REPRODUCE.md` and `ENVIRONMENT.json` attached to each paper
      through the Zenodo form. This is the step that mints public DOIs.
- [ ] **Update the ORCID record's GitHub URL.** It still points at
      `github.com/nuerainc`; the live organization is
      `github.com/nueraresearch`. This is an owner action in the ORCID
      interface and nothing in this repository can change it. The repository
      itself is consistent — `nuerainc` appears nowhere but in one historical
      session transcript and in this line.
- [ ] **After publishing**, record each DOI in `CITATION.cff`, in the
      manuscript's own header, and in `CHANGELOG.md`, and add the software
      record's DOI to each paper record as `isSupplementedBy` and each paper's
      DOI to the software record as `isDocumentedBy`.

**Not needed for this deposit, and therefore not done:** authorising the
Zenodo GitHub app, and cutting a GitHub release for v0.10.0. Both become
worth doing when the owner decides that releases should mint DOIs
automatically — which is a separate decision with a lasting effect.

## What was read, and how far

The metadata here is written against Zenodo's own documentation, read on
2026-10-31:

- **The deposit JSON schema**, fetched from Zenodo's repository
  (`zenodo/modules/deposit/jsonschemas/deposits/records/legacyrecord.json`).
  Read in full: the field names, the `additionalProperties: false` rule, the
  `upload_type` and `publication_type` enums, the `related_identifiers`
  `scheme` and `relation` enums, and the creator object shape. The schema
  sets `additionalProperties: false`, so a field name that is not in it is a
  field the deposit form will reject.
- **The GitHub-integration section** of Zenodo's developer documentation, read
  in full: that a `.zenodo.json` file at the repository root overrides the
  metadata Zenodo would otherwise take from the GitHub release, and the
  example `.zenodo.json` body.
- **Zenodo's general policies**, read in full: all file formats are accepted,
  the size limit is 50 GB per record, metadata is stored as JSON against a
  published schema, a licence is required for every publicly available file,
  and metadata is licensed CC0.
- **The communities API**, queried live for "machine learning". Three
  communities carry that title: `a08bc0ac-2893-4afd-870a-a77bd348c84c`,
  `f1d92ab1-327a-4b0c-be4a-6b656d06ee4b` and
  `c621d105-21f1-4ce1-98c3-750eac56d27d`. The first is used here; the owner
  may prefer another, and the identifier is a one-line change in each
  metadata file.

Nothing in this package was recalled from memory. The ORCID identifier, the
repository URL, the licence and the release list were each read from the
repository itself (`CITATION.cff`, `LICENSE`, `git tag`), and the community
identifier was read from Zenodo's API.

## Files in this package

- `.zenodo.json` — metadata for the GitHub-release integration.
- `zenodo/software-v0.11.0.json` — the software record's metadata.
- `zenodo/paper-01-preprint.json` — Paper 01's record metadata.
- `zenodo/paper-02-preprint.json` — Paper 02's record metadata.
- `benchmarks/zenodo_metadata.py` — validates every metadata file against
  Zenodo's published schema, fetching the schema from Zenodo's repository and
  caching it under `.scratch/`.
- `benchmarks/deposit_bundle.py` — builds the three bundles, their checksums
  and their manifests, and checks the deposit's file list against the
  artifacts the manuscripts cite.
- `docs/PDF-PIPELINE.md` — how the PDFs are built.
- `.scratch/deposit/reproduction/` — the reproduction bundle (generated, not versioned).

→ `.zenodo.json`; `zenodo/`; `benchmarks/zenodo_metadata.py`;
`docs/PDF-PIPELINE.md`; `CITATION.cff`; `LICENSE`.
