"""Export static literals from a community-patched client's data, never import it.

Uses Python's AST and literal_eval only. No exec/eval/import of inspected files.
This is an independently written data reader; it is not QQTang client code.
"""
import argparse
import ast
from collections import Counter
import hashlib
import json
import math
from pathlib import Path


def json_literal(value):
    if value is None or type(value) in (str, int, bool):
        return value
    if type(value) is float and math.isfinite(value):
        return value
    if type(value) in (tuple, list):
        return [json_literal(item) for item in value]
    if type(value) is dict and all(type(key) is str for key in value):
        return {key: json_literal(item) for key, item in value.items()}
    raise ValueError("Unsupported or nonfinite literal value")


def named_assignment(node):
    if not isinstance(node, ast.Assign) or len(node.targets) != 1 or not isinstance(node.targets[0], ast.Name):
        raise ValueError(f"Only simple static assignments are supported (line {getattr(node, 'lineno', '?')})")
    return node.targets[0].id


def parse_catalog_text(text):
    tree = ast.parse(text, filename="mapDesc.py", mode="exec")
    if len(tree.body) != 1 or named_assignment(tree.body[0]) != "mapDesc":
        raise ValueError("Expected only one mapDesc literal assignment")
    rows = ast.literal_eval(tree.body[0].value)
    if type(rows) not in (list, tuple):
        raise ValueError("mapDesc must be a literal list or tuple")
    entries = []
    for ordinal, row in enumerate(rows):
        if type(row) not in (tuple, list) or len(row) != 13:
            raise ValueError(f"Catalog row {ordinal} must have 13 fields")
        if any(type(row[index]) is not int for index in (0, 3, 4, 5, 9, 11, 12)):
            raise ValueError(f"Catalog row {ordinal} has invalid integer fields")
        if any(type(row[index]) is not str for index in (1, 2, 6, 7, 8, 10)):
            raise ValueError(f"Catalog row {ordinal} has invalid text fields")
        if row[3] < 1 or row[4] < 1 or row[5] < 1:
            raise ValueError(f"Catalog row {ordinal} has invalid dimensions or player limit")
        if any(char in row[6] for char in ("/", "\\", "\0")) or not row[6].lower().endswith(".map"):
            raise ValueError(f"Catalog row {ordinal} has an unsafe map filename")
        entries.append({
            "ordinal": ordinal, "id": row[0], "family": row[1], "name": row[2],
            "catalogWidth": row[3], "catalogHeight": row[4], "playerLimit": row[5],
            "mapFileName": row[6], "previewFileName": row[7], "musicFileName": row[8],
            "requiredPoints": row[9], "directive": row[10], "selectableFlag": row[11],
            "field12": row[12], "rawFields": json_literal(row),
        })
    counts = Counter(entry["id"] for entry in entries)
    return {
        "schemaVersion": 1, "entryCount": len(entries),
        "fieldNotes": {
            "catalogWidth/catalogHeight": "Catalog-declared metadata; never overrides .map header dimensions.",
            "field12": "Raw column 12; mode-dependent meaning has not been established by this static reader.",
            "rawFields": "Original tuple field order, converted to a JSON array without execution.",
        },
        "duplicateIds": [key for key, count in counts.items() if count > 1],
        "entries": entries,
    }


def parse_elements_text(text):
    tree = ast.parse(text, filename="mapElem.py", mode="exec")
    classes = {}
    registry = None
    for node in tree.body:
        if isinstance(node, ast.ClassDef):
            if node.name in classes or node.decorator_list or node.keywords:
                raise ValueError(f"Unsupported or duplicate class {node.name}")
            if len(node.bases) > 1 or any(not isinstance(base, ast.Name) for base in node.bases):
                raise ValueError(f"Only simple single inheritance is supported: {node.name}")
            bases = [base.id for base in node.bases]
            if any(base not in classes for base in bases):
                raise ValueError(f"Unknown base for {node.name}")
            properties = dict(classes[bases[0]]["properties"]) if bases else {}
            declarations = {}
            for statement in node.body:
                name = named_assignment(statement)
                if name in declarations:
                    raise ValueError(f"Repeated attribute {node.name}.{name}")
                value = json_literal(ast.literal_eval(statement.value))
                declarations[name] = value
                properties[name] = value
            classes[node.name] = {
                "className": node.name, "bases": bases, "sourceLine": node.lineno,
                "declared": declarations, "properties": properties,
            }
        elif isinstance(node, ast.Assign):
            if named_assignment(node) != "qqtMapElems" or registry is not None or not isinstance(node.value, ast.Dict):
                raise ValueError("Only one static qqtMapElems registry is supported")
            registry = []
            seen = set()
            for key_node, value_node in zip(node.value.keys, node.value.values):
                key = ast.literal_eval(key_node)
                if type(key) is not int or key <= 0 or key in seen or not isinstance(value_node, ast.Name):
                    raise ValueError("Invalid element registry entry")
                if value_node.id not in classes:
                    raise ValueError(f"Unknown element registry class {value_node.id}")
                seen.add(key)
                registry.append((key, value_node.id))
        else:
            raise ValueError(f"Executable/unsupported module statement rejected: {type(node).__name__}")
    if registry is None:
        raise ValueError("Missing qqtMapElems registry")
    elements = []
    issues = []
    for key, class_name in registry:
        item = classes[class_name]
        properties = item["properties"]
        size = properties.get("size")
        attrs = properties.get("GridAttr")
        if type(size) is not list or len(size) != 2 or any(type(value) is not int or value < 1 for value in size):
            raise ValueError(f"Invalid element size: {class_name}")
        if type(attrs) is not list or any(type(value) is not int or not 0 <= value <= 0xffffffff for value in attrs):
            raise ValueError(f"Invalid element GridAttr: {class_name}")
        offset = properties.get("offset")
        if type(offset) is not list or len(offset) != 2 or any(type(value) is not int for value in offset):
            raise ValueError(f"Invalid element offset: {class_name}")
        if properties.get("imageID") != key:
            issues.append({"id": key, "code": "IMAGE_ID_DIFFERS", "imageID": properties.get("imageID")})
        if len(attrs) != size[0] * size[1]:
            issues.append({"id": key, "code": "GRID_ATTR_LENGTH", "actual": len(attrs), "expected": size[0] * size[1]})
        elements.append({
            "id": key, **item, "widthCells": size[0], "heightCells": size[1],
            "gridAttr": attrs, "imageOffset": offset,
        })
    referenced = {class_name for _, class_name in registry}
    return {
        "schemaVersion": 1, "classCount": len(classes), "elementCount": len(elements),
        "fieldNotes": {
            "properties": "Static inherited literal attributes; inspected classes are never instantiated.",
            "gridAttr": "Raw per-cell bitfields, not reduced to a solid boolean.",
            "imageOffset": "Raw offset pair; sign/origin/units need client rendering evidence before use.",
        },
        "baseClasses": [item for name, item in classes.items() if name not in referenced],
        "validationIssues": issues, "elements": elements,
    }


def verified_input(path, suffix, manifest):
    data = path.read_bytes()
    if len(data) > 2_000_000:
        raise ValueError("Static source exceeds 2 MB limit")
    digest = hashlib.sha256(data).hexdigest()
    matches = [record for record in manifest["files"] if record["archiveEntry"].endswith(suffix)]
    if len(matches) != 1 or matches[0]["sha256"].lower() != digest or matches[0]["bytes"] != len(data):
        raise ValueError(f"Source does not match extraction manifest: {path}")
    return data, {
        "archiveUrl": manifest["url"], "archiveSha256": manifest["archiveSha256"],
        "sourceType": manifest["sourceType"],
        "officialOriginalAuthenticity": manifest["officialOriginalAuthenticity"],
        "archiveEntry": matches[0]["archiveEntry"], "localInput": matches[0]["localPath"],
        "byteLength": len(data), "sha256": digest, "externalCodeExecuted": False,
        "method": "Python AST + literal_eval; single class inheritance and registry Name references resolved as data only",
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--client-root", required=True, type=Path)
    parser.add_argument("--manifest", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    input_root = args.client_root.resolve()
    output_root = args.output.resolve()
    if output_root == input_root or input_root in output_root.parents:
        raise ValueError("Output must be outside the inspected client directory")
    manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
    catalog_bytes, catalog_source = verified_input(input_root / "map/mapDesc.py", "/runtime/client-patched/map/mapDesc.py", manifest)
    elements_bytes, elements_source = verified_input(input_root / "object/mapElem/mapElem.py", "/runtime/client-patched/object/mapElem/mapElem.py", manifest)
    catalog = parse_catalog_text(catalog_bytes.decode("gb18030", errors="strict"))
    elements = parse_elements_text(elements_bytes.decode("utf-8", errors="strict"))
    catalog["source"] = {**catalog_source, "encoding": "gb18030"}
    elements["source"] = {**elements_source, "encoding": "utf-8"}
    output_root.mkdir(parents=True, exist_ok=True)
    for name, document in (("catalog.json", catalog), ("elements.json", elements)):
        (output_root / name).write_text(json.dumps(document, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"catalogEntries": catalog["entryCount"], "duplicateCatalogIds": catalog["duplicateIds"], "classes": elements["classCount"], "elements": elements["elementCount"], "validationIssues": elements["validationIssues"]}, ensure_ascii=True))


if __name__ == "__main__":
    main()
