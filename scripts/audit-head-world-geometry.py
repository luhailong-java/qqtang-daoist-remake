"""Independently measure a selected head-world manifest; never change assets.

Exit 0: technical checks and the measured aspect gate pass.  Exit 2: only
aspect warnings remain.  Exit 1: source, alpha, registration or provenance
errors.  These checks do not establish animation timing or runtime acceptance.
"""
from pathlib import Path
import argparse
import hashlib
import json
import math

from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--item", type=int, required=True)
parser.add_argument("--manifest", help="Project-relative candidate manifest")
parser.add_argument("--aspect-limit", type=float, default=0.1)
parser.add_argument("--allow-partial", action="store_true", help="Audit an explicitly partial candidate selection")
args = parser.parse_args()


def local(name):
    path = (ROOT / name).resolve()
    if not path.is_relative_to(ROOT):
        raise ValueError("Input path leaves this project")
    return path


def read(name):
    return json.loads(local(name).read_text(encoding="utf-8-sig"))


def sha(name):
    return hashlib.sha256(local(name).read_bytes()).hexdigest()


images = {}


def image(name):
    if name not in images:
        with Image.open(local(name)) as opened:
            images[name] = opened.convert("RGBA")
    return images[name]


def box16(picture):
    return picture.getchannel("A").point(lambda a: 255 if a >= 16 else 0).getbbox()


base = "assets/items/head-adornments"
contract = read(f"{base}/references/world/{args.item}/source-contract.json")
manifest = args.manifest or f"{base}/world-{args.item}-art.json"
item = next(entry for entry in read(manifest)["items"] if entry["itemId"] == args.item)
frames = item["frames"]
by_index = {frame["sourceFrameIndex"]: frame for frame in frames}
representatives = {index: group[0] for group in contract["encodedRasterGroups"] for index in group}
errors = []
measures = []
expected_order = contract.get("frameOrder", list(range(len(contract["frames"]))))
expected_positions = set(expected_order)
candidate_order = [frame["sourceFrameIndex"] for frame in frames]
missing_positions = sorted(expected_positions - set(by_index))
if len(by_index) != len(frames):
    errors.append("Duplicate source positions in candidate manifest")
if expected_positions != set(range(len(contract["frames"]))) or len(expected_order) != len(expected_positions):
    errors.append("Source contract frameOrder is not a complete valid position list")
if item.get("sourceFrameOrder") != expected_order:
    errors.append("Candidate sourceFrameOrder differs from contract")
if missing_positions and not args.allow_partial:
    errors.append(f"Missing required source positions: {missing_positions}")
if candidate_order != [index for index in expected_order if index in by_index]:
    errors.append("Candidate position order differs from explicit source order")

for frame in frames:
    index = frame["sourceFrameIndex"]
    try:
        if not isinstance(index, int) or isinstance(index, bool) or index < 0 or index >= len(contract["frames"]):
            raise ValueError("Source position lies outside the source contract")
        source = contract["frames"][index]
        native = source["nativeFrameSize"]
        raw = source["frameOffsetRaw"]
        if frame["logicalFrameSize"] != native or frame["frameOffsetRaw"] != raw:
            raise ValueError("Native logical canvas or rawOffset changed")
        if frame["exportDensity"] != 4 or frame["frameOffsetPxAtDensity4"] != [v * 4 for v in raw]:
            raise ValueError("Export density or pixel offset differs from contract")
        output = image(frame["file"])
        if list(output.size) != [v * 4 for v in native] or list(output.size) != [frame["width"], frame["height"]]:
            raise ValueError("Decoded PNG canvas differs from native canvas times four")
        alpha_min, alpha_max = output.getchannel("A").getextrema()
        # RGBA sprites may legitimately top out at254 or use translucent paint.
        # The source contract requires empty alpha plus visible content, not255.
        if alpha_min != 0 or alpha_max < 16:
            raise ValueError("PNG lacks fully transparent alpha or visible content")
        if sha(frame["file"]) != frame["sha256"]:
            raise ValueError("Output SHA mismatch")

        rep = representatives[index]
        if frame.get("imagePhaseRepresentativeIndex") != rep:
            raise ValueError("Source representative metadata does not match encoded raster equality")
        if index != rep and frame["file"] != by_index[rep]["file"]:
            raise ValueError("Exact source alias does not reuse its representative candidate")
        if index != rep and frame.get("rasterAliasOfSourceFrameIndex") != rep:
            raise ValueError("Source raster alias metadata differs")

        reference = frame["sourceReference"]
        source_picture = image(reference["file"])
        if sha(reference["file"]) != reference["sha256"] or list(source_picture.size) != native:
            raise ValueError("Source-reference SHA or size mismatch")
        source_box = box16(source_picture)
        if not source_box or list(source_box) != source["sourceAlphaBBoxAt16"]:
            raise ValueError("Decoded source alpha envelope differs from contract")

        mother = frame["derivedFrom"]
        if sha(mother["file"]) != mother["sha256"]:
            raise ValueError("Mother SHA mismatch")
        operation = frame["operation"].get("originalPaintOperation", frame["operation"])
        rect = operation["sourceCellRectLTRB"]
        master = image(mother["file"])
        if not (0 <= rect[0] < rect[2] <= master.width and 0 <= rect[1] < rect[3] <= master.height):
            raise ValueError("Recorded crop lies outside mother")
        crop = master.crop(rect)
        painted_box = box16(crop)
        if not painted_box or list(painted_box) != operation["generatedContentBBoxAt16"]:
            raise ValueError("Measured mother alpha envelope differs from provenance")
        if painted_box[0] == 0 or painted_box[1] == 0 or painted_box[2] == crop.width or painted_box[3] == crop.height:
            raise ValueError("Mother crop touches visible content")
        if operation["sourceLogicalAlphaBBoxAt16"] != list(source_box):
            raise ValueError("Provenance source envelope differs from decoded source")
        sw, sh = source_box[2] - source_box[0], source_box[3] - source_box[1]
        pw, ph = painted_box[2] - painted_box[0], painted_box[3] - painted_box[1]
        source_aspect = sw / sh
        painted_aspect = pw / ph
        deviation = abs(painted_aspect / source_aspect - 1)
        for key, value in (("sourceVisibleAspect", source_aspect), ("generatedVisibleAspect", painted_aspect), ("relativeAspectDeviation", deviation)):
            if not math.isclose(frame["qa"][key], value, rel_tol=1e-9, abs_tol=1e-9):
                raise ValueError(f"Stored QA {key} does not match actual decoded pixels")
        scale = min(sw * 4 / pw, sh * 4 / ph)
        painted_size = [round(pw * scale), round(ph * scale)]
        placement = [source_box[0] * 4 + (sw * 4 - painted_size[0]) // 2,
                     source_box[1] * 4 + sh * 4 - painted_size[1]]
        if not math.isclose(operation["uniformScale"], scale, rel_tol=1e-9, abs_tol=1e-9) or operation["placementPx"] != placement:
            raise ValueError("Recorded scale or registration is not uniform source-envelope fit")
        measures.append({"sourceFrameIndex": index, "representative": rep, "nativeFrameSize": native,
                         "frameOffsetRaw": raw, "sourceVisibleAspect": source_aspect,
                         "measuredMotherVisibleAspect": painted_aspect, "relativeAspectDeviation": deviation,
                         "aspectGatePassed": deviation <= args.aspect_limit})
    except Exception as exc:
        errors.append(f"{index}: {exc}")

warnings = [row["sourceFrameIndex"] for row in measures if not row["aspectGatePassed"]]
print(json.dumps({"itemId": args.item, "manifest": manifest, "sourceDeclaredPositions": len(contract["frames"]),
                  "candidatePositions": len(frames), "missingPositions": missing_positions,
                  "uniqueCandidateRasters": len({frame["file"] for frame in frames}), "alphaThreshold": 16,
                  "aspectLimit": args.aspect_limit, "measuredPositions": measures,
                  "aspectWarningSourcePositions": warnings, "errors": errors,
                  "scope": "Independent pixel/provenance geometry audit; no animation or runtime acceptance",
                  "animationTimingKnown": item.get("animationTimingKnown"), "runtimeAdopted": item.get("runtimeAdopted")},
                 ensure_ascii=False, indent=2))
raise SystemExit(1 if errors else 2 if warnings else 0)
