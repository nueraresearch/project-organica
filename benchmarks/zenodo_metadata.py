"""Validate the Zenodo deposit metadata against Zenodo's published deposit
JSON schema.

The schema is fetched from the primary record — Zenodo's own repository —
rather than transcribed from memory, because every field name and every enum
value in it is load-bearing: the schema sets ``additionalProperties: false``,
so a field name that does not exist there is a field the deposit form will
reject.

    python benchmarks/zenodo_metadata.py [--schema <path>]

With no ``--schema`` the schema is fetched from Zenodo's repository and
cached under ``.scratch/``.  The check is offline if the schema is already
cached.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
SCHEMA_URL = ("https://raw.githubusercontent.com/zenodo/zenodo/master/"
               "zenodo/modules/deposit/jsonschemas/deposits/records/"
               "legacyrecord.json")
SCHEMA_CACHE = REPO / ".scratch" / "zenodo_legacyrecord.json"

#: Every file that carries deposit metadata: the GitHub-integration file and
#: every record under ``zenodo/``.  The list is read from the directory rather
#: than written out here because the software record's filename carries a
#: version, and a hard-coded copy of that version goes stale silently: this
#: check went on listing ``software-v0.10.0.json`` after the record had moved
#: to a new version, so it failed on a missing file instead of validating the
#: metadata it exists to validate -- a check that is red for the wrong reason
#: is a check nobody reads.
METADATA_FILES = [".zenodo.json"] + sorted(
    str(path.relative_to(REPO).as_posix()) for path in (REPO / "zenodo").glob("*.json"))


def fetch_schema() -> dict:
    if SCHEMA_CACHE.exists():
        return json.loads(SCHEMA_CACHE.read_text(encoding="utf-8"))
    import urllib.request
    with urllib.request.urlopen(SCHEMA_URL, timeout=60) as response:
        raw = response.read().decode("utf-8")
    SCHEMA_CACHE.parent.mkdir(parents=True, exist_ok=True)
    SCHEMA_CACHE.write_text(raw, encoding="utf-8")
    return json.loads(raw)


def validate(document: dict, schema: dict, label: str) -> list[str]:
    """Return the problems in one metadata document."""
    problems: list[str] = []
    properties = schema.get("properties", {})
    allowed = set(properties)
    extra = set(document) - allowed
    if extra:
        problems.append("%s: field(s) not in the schema: %s"
                        % (label, ", ".join(sorted(extra))))
    for field, value in document.items():
        spec = properties.get(field)
        if spec is None:
            continue
        enum = spec.get("enum")
        if enum and value not in enum:
            problems.append("%s: %s = %r is not one of %s"
                            % (label, field, value, ", ".join(map(str, enum))))
        kind = spec.get("type")
        if kind == "string" and not isinstance(value, str):
            problems.append("%s: %s should be a string" % (label, field))
        if kind == "array" and not isinstance(value, list):
            problems.append("%s: %s should be an array" % (label, field))
        if kind == "object" and not isinstance(value, dict):
            problems.append("%s: %s should be an object" % (label, field))
        if field == "creators":
            for index, creator in enumerate(value):
                unknown = set(creator) - set(properties["creators"]["items"]["properties"])
                if unknown:
                    problems.append("%s: creators[%d] has field(s) not in the "
                                    "schema: %s"
                                    % (label, index, ", ".join(sorted(unknown))))
                if "orcid" in creator:
                    orcid = creator["orcid"]
                    if not (len(orcid) == 19 and orcid[4] == "-" and orcid[9] == "-"
                            and orcid[14] == "-" and orcid[19:] == ""):
                        problems.append("%s: creators[%d].orcid is not a bare "
                                        "ORCID iD: %r" % (label, index, orcid))
                    else:
                        body = orcid.replace("-", "")
                        if not body.isdigit():
                            problems.append("%s: creators[%d].orcid is not "
                                            "numeric" % (label, index))
        if field == "related_identifiers":
            item_props = properties["related_identifiers"]["items"]["properties"]
            for index, item in enumerate(value):
                unknown = set(item) - set(item_props)
                if unknown:
                    problems.append("%s: related_identifiers[%d] has field(s) "
                                    "not in the schema: %s"
                                    % (label, index, ", ".join(sorted(unknown))))
                for field_name, spec in item_props.items():
                    if "enum" in spec and item.get(field_name) not in spec["enum"]:
                        problems.append("%s: related_identifiers[%d].%s = %r is "
                                        "not one of %s"
                                        % (label, index, field_name,
                                           item.get(field_name),
                                           ", ".join(map(str, spec["enum"]))))
        if field == "communities":
            for index, community in enumerate(value):
                unknown = set(community) - {"identifier"}
                if unknown:
                    problems.append("%s: communities[%d] has field(s) not in "
                                    "the schema: %s"
                                    % (label, index, ", ".join(sorted(unknown))))
    return problems


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--schema", default=None,
                        help="path to the deposit JSON schema")
    args = parser.parse_args(argv)

    if args.schema:
        schema = json.loads(Path(args.schema).read_text(encoding="utf-8"))
    else:
        schema = fetch_schema()

    problems: list[str] = []
    if not any("software-v" in rel for rel in METADATA_FILES):
        problems.append("zenodo/software-v<version>.json: missing -- no "
                        "software record to validate")
    for rel in METADATA_FILES:
        path = REPO / rel
        if not path.exists():
            problems.append("%s: missing" % rel)
            continue
        document = json.loads(path.read_text(encoding="utf-8"))
        problems.extend(validate(document, schema, rel))

    for rel in METADATA_FILES:
        path = REPO / rel
        if path.exists():
            print("checked %s" % rel)
    if problems:
        print("\nPROBLEMS:")
        for problem in problems:
            print("  - %s" % problem)
        return 1
    print("\nall metadata files conform to the deposit schema")
    return 0


if __name__ == "__main__":
    sys.exit(main())
