# Zenodo deposit package

**Status: prepared, not deposited.** Every field below is filled in and every
file is staged, but publishing is the owner's action: Zenodo mints a DOI when a
record is published, and a DOI is public. Nothing here has been uploaded.

**Why Zenodo and not arXiv.** The owner's decision of 2026-10-30 was arXiv
first; the later decision superseded it, and Zenodo is the current venue. The
two are not exclusive — a Zenodo preprint DOI and an arXiv identifier can
co-exist on the same manuscript, and this package is written so that the
arXiv route can still be taken later without redoing the metadata.

## What is being deposited

| Record | Type | Version | Metadata file |
|---|---|---|---|
| The frozen Organica 1 engine and its evidence artifacts | software | **v0.10.0** | `zenodo/software-v0.10.0.json` |
| Paper 01 — Developmental structure formation | publication (preprint) | 1.0.0 | `zenodo/paper-01-preprint.json` |
| Paper 02 — Persistent structural provenance | publication (preprint) | 1.0.0 | `zenodo/paper-02-preprint.json` |

**The software record carries v0.10.0.** The engine inside it is frozen:
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
| Upload type | `software` for the engine; `publication` / `preprint` for the papers |
| Access right | `open` |
| Creators | Beebe, Jeremy Blain Thompson — Nuera RDL — ORCID `0009-0009-2394-9714` |
| Communities | Machine Learning — `a08bc0ac-2893-4afd-870a-a77bd348c84c` |
| Keywords | record-specific; see each metadata file |
| Related identifiers | the repository URL; for the software record, the v0.10.0 release URL |
| Notes | see each metadata file — the notes carry the freeze statement and the deposit's file list |
| Version | the release tag (software) or `1.0.0` (papers) — entered in the form, not in the JSON |

### Licensing

The engine is **Apache-2.0**: `LICENSE` in the repository is Apache-2.0 and
`CITATION.cff` already declares it.

The two papers are pre-filled with **CC-BY-4.0**, which is Zenodo's default for
a textual work and the usual choice for a preprint. **This one is not yet the
owner's decision** — it is a stated assumption, and it must be confirmed
before the papers are deposited. If the owner prefers the repository's
Apache-2.0 for the papers too, change the `license` field in both paper
metadata files and re-run `python benchmarks/zenodo_metadata.py`.

### Files

**Software record (v0.10.0).** The earlier GitHub releases carry **no
assets** — `gh release view v0.9.0` reports zero — so a deposit made from
one of them would have no file of its own. The v0.10.0 release is the one
that can carry them. Two ways forward, both the owner's:

1. **Attach assets to the release, then let the integration mint the DOI.**
   The minimum is the source tree at the tag plus the evidence artifacts the
   paper cites. This is the better route: the release already exists, and the
   minted DOI is version-scoped for free.
2. **Deposit manually** through the Zenodo web form and paste the metadata
   from `zenodo/software-v0.10.0.json`. Use this when the record must carry
   files that are not in the release.

**Paper records.** Each carries the manuscript as PDF, the manuscript source
as Markdown, and its figures as PDF. The PDF build is

```
python benchmarks/render_papers.py
```

which writes `papers/build/01_developmental_structure_formation.pdf` and
`papers/build/02_persistent_structural_provenance.pdf` (see
`docs/PDF-PIPELINE.md`); the figures are the same SVGs the repository holds,
converted to vector PDF by the same tool.

### After the paper DOIs exist

Add each preprint DOI to the software record as `isDocumentedBy`, and add the
software record's DOI to each paper as `isSupplementedBy`. The paper metadata
files carry the repository URL for now, because the software DOI does not
exist yet and a guessed DOI is a false claim.

## Before publishing — checklist

- [ ] Confirm the papers' license (CC-BY-4.0 assumed; Apache-2.0 if the
      owner prefers the repository's licence for the manuscripts too).
- [ ] Authorise the Zenodo GitHub app on the repository, if the version DOIs
      are to be minted from the releases.
- [ ] Decide whether to attach assets to the `v0.10.0` release (and to the
      earlier tags) or to deposit the software record manually.
- [ ] Decide whether the paper preprints are deposited before or after the
      journal route is attempted. Depositing first is the safer order: it
      establishes priority and the DOI can be cited in a journal submission.
- [ ] Update the ORCID record's GitHub URL. It still points at
      `github.com/nuerainc`; the live organization is
      `github.com/nueraresearch`. **This is an owner action in the ORCID
      interface** and nothing in this repository can change it.
- [ ] Run `python benchmarks/zenodo_metadata.py` and confirm it passes.
- [ ] Confirm the deposit's file list against the artifacts the manuscript
      actually cites.
- [ ] After publishing, record each DOI in `CITATION.cff`, in the manuscript's
      own header, and in `CHANGELOG.md`.

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
- `zenodo/software-v0.10.0.json` — the software record's metadata.
- `zenodo/paper-01-preprint.json` — Paper 01's record metadata.
- `zenodo/paper-02-preprint.json` — Paper 02's record metadata.
- `benchmarks/zenodo_metadata.py` — validates every metadata file against
  Zenodo's published schema, fetching the schema from Zenodo's repository and
  caching it under `.scratch/`.
- `docs/PDF-PIPELINE.md` — how the PDFs are built.

→ `.zenodo.json`; `zenodo/`; `benchmarks/zenodo_metadata.py`;
`docs/PDF-PIPELINE.md`; `CITATION.cff`; `LICENSE`.
