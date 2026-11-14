"""Export stationary illumination candidates with source dimensions and separate offsets."""
from pathlib import Path
import argparse
import importlib.util

from PIL import Image, ImageChops, ImageDraw, ImageStat

HERE = Path(__file__).resolve()
BASE = HERE.parent
SPEC = importlib.util.spec_from_file_location("grate_common", BASE / "verify-opaque-grates.py")
common = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(common)
ROOT, FLAGS, UNKNOWN, DENSITIES = common.ROOT, common.FLAGS, common.UNKNOWN, common.DENSITIES
read, write, sha, digest, check, rel, stamp = (common.read, common.write, common.sha, common.digest,
                                               common.check, common.rel, common.stamp)
IDS = (17048, 17052, 17077)
COUNT = 4
GEOMETRY = {17048: ([40, 57], [0, 0], [0, 17]), 17052: ([36, 59], [1, 0], [2, 28]),
            17077: ([36, 59], [3, 0], [-2, 19])}
SOURCE_LIGHT = {17048: [(7, 35, 15, 42), (25, 35, 33, 42)], 17052: [(11, 23, 17, 30)],
                17077: [(19, 23, 25, 30)]}


def light_metric(raster, rects, element):
    values = []
    for rect in rects:
        stats = ImageStat.Stat(raster.crop(rect).convert("RGB")).mean
        values.append(stats[0] - max(stats[1:]) if element == 17048 else stats[1])
    return [round(value, 3) for value in values]


def verified_source(element):
    directory = BASE / str(element)
    path = directory / "source-contract.json"
    contract = read(path)
    decoder, metadata, raw = common.source_member(contract)
    size, frame_offset, map_offset = GEOMETRY[element]
    check(contract["elementId"] == element and metadata["frameCount"] == COUNT and metadata["directions"] == 1 and
          metadata["declaredCanvas"] == contract["sourceDeclaredCanvas"] and
          contract["sourceMapElemOffset"] == map_offset and contract["sourceFootprintCells"] == [1, 1], "Source geometry differs")
    board_path = directory / "source-phase-board.png"
    board = Image.open(board_path).convert("RGB")
    board_record = read(Path(str(board_path) + ".source.json"))
    check(board_record["sha256"] == sha(board_path) and board_record["sourceContractSha256"] == sha(path),
          "Source reference board differs")
    metrics = []
    for phase, (native, frame, item) in enumerate(zip(metadata["frames"], contract["sourceFrames"], board_record["items"], strict=True)):
        check(phase == native["index"] == frame["frameIndex"] == item["sourceFrameIndex"] and
              native["frameOffset"] == frame["sourceFrameOffset"] == frame_offset and
              [native["width"], native["height"]] == frame["sourceFrameSize"] == size and not native["empty"] and
              frame["aliasOf"] is None, "Source frame contract differs")
        offset = native["pixelDataOffset"]
        pixels = decoder.decode_frame_pixels(raw[offset:offset + native["pixelByteLength"]], native["pixelMode"], *size)
        source = ROOT / frame["file"]
        raster = Image.open(source).convert("RGBA")
        alpha = raster.getchannel("A")
        canonical = raster.copy()
        canonical.paste((0, 0, 0, 0), (0, 0, *size), alpha.point([255] + [0] * 255))
        check(raster.tobytes() == pixels and digest(pixels) == frame["decodedRgbaSha256"] and
              digest(canonical.tobytes()) == frame["canonicalRgbaSha256"] and
              sha(source) == frame["sha256"] == item["sha256"] and item["file"] == frame["file"] and
              alpha.getextrema() == (0, 255), "Source pixels differ")
        scale = item["uniformNearestScale"]
        expected = Image.new("RGBA", tuple(n * scale for n in size), tuple(board_record["boardBackdropRgb"]) + (255,))
        expected.alpha_composite(raster.resize(expected.size, Image.Resampling.NEAREST))
        check(board.crop(item["rect"]).tobytes() == expected.convert("RGB").tobytes(), "Reference board phase differs")
        metrics.append(light_metric(raster, SOURCE_LIGHT[element], element))
    check(len({frame["canonicalRgbaSha256"] for frame in contract["sourceFrames"]}) == COUNT, "Unexpected source aliases")
    return contract, metrics


def generation_evidence(directory, contract, version):
    filename = f"builtin-submission-{version}.json"
    call = read(directory / filename)
    input_data = call["input"]
    prompt_path = directory / f"prompt-{version}.txt"
    atlas_path = directory / f"sequence-{version}.png"
    atlas = Image.open(atlas_path)
    check(atlas.format == "PNG" and atlas.mode == "RGBA" and atlas.width == atlas.height and
          atlas.width % 2 == 0 and atlas.getchannel("A").getextrema() == (0, 255) and
          sha(atlas_path) == call["result"]["localAtlasSha256"], "Host atlas bytes or alpha differ")
    check(prompt_path.read_bytes() == input_data["prompt"].encode() and input_data["transparent_background"] is True,
          "Exact submission differs")
    references = []
    roles = ("Four source phases", "Original first-frame design", "Daoist Q art finish", "Daoist Q art finish")
    for path, role in zip(input_data["referenced_image_paths"], roles, strict=True):
        path = ROOT / path.split("/qqtang-daoist-remake/", 1)[1]
        references.append({"file": rel(path), "sha256": sha(path), "role": role})
    identity = contract["currentOwnFirstFrame"]
    check(references[0]["file"] == rel(directory / "source-phase-board.png") and
          references[1]["file"] == identity["file"] and references[1]["sha256"] == identity["sha256"] and
          sha(ROOT / identity["generationRecord"]) == identity["generationRecordSha256"] and
          sha(ROOT / identity["provenanceRecord"]) == identity["provenanceSha256"], "Master reference lineage differs")
    config = ROOT / "config/image-generation.json"
    record = {"schemaVersion": 1, "file": rel(atlas_path), "sha256": sha(atlas_path), "nativeSize": list(atlas.size),
              "mode": atlas.mode, "alphaExtrema": [0, 255], "tool": "image_gen.imagegen", "route": "builtin",
              "actualModel": None, "actualQuality": None, "config": {"file": rel(config), "sha256": sha(config)},
              "references": references, "promptFile": rel(prompt_path), "promptSha256": sha(prompt_path),
              "exactSubmittedInput": input_data, "callRecord": {"file": rel(directory / filename),
              "sha256": sha(directory / filename), **call["result"]}, **FLAGS}
    return atlas, atlas_path, record


def fit_atlas(atlas, fit, logical_size):
    cell_size = atlas.width // 2
    w, h = logical_size
    cells = []
    for phase, rect in enumerate(fit["cellRelativeCrops"]):
        x, y = phase % 2 * cell_size, phase // 2 * cell_size
        cell = atlas.crop((x, y, x + cell_size, y + cell_size))
        alpha = cell.getchannel("A")
        bounds = alpha.point(lambda value: 255 if value >= 8 else 0).getbbox()
        left, top, right, bottom = rect
        check(bounds and 0 <= left <= bounds[0] < bounds[2] <= right <= cell_size and
              0 <= top <= bounds[1] < bounds[3] <= bottom <= cell_size and
              (right - left) * h == (bottom - top) * w, "Exact-aspect crop clips visible art")
        outside = [(0, 0, left, cell_size), (right, 0, cell_size, cell_size),
                   (left, 0, right, top), (left, bottom, right, cell_size)]
        outside_alpha = [alpha.crop(region).getextrema()[1] for region in outside
                         if region[0] < region[2] and region[1] < region[3]]
        max_alpha = max(outside_alpha, default=0)
        check(max_alpha < 8, "Visible alpha outside exact-aspect crop")
        cells.append({"sourceRectLTRB": [left + x, top + y, right + x, bottom + y],
                      "alpha8BoundsWithinCell": list(bounds), "maxAlphaOutsideCrop": max_alpha})
    check(len(cells) == COUNT, "Four atlas cells required")
    return cells


def export_pixels(atlas, cell, logical_size, density):
    extent = tuple(n * density for n in logical_size)
    crop = atlas.crop(cell["sourceRectLTRB"]).convert("RGBa")
    return crop.resize(extent, Image.Resampling.LANCZOS).convert("RGBA")


def measure_painted_phases(atlas, cells, fit, size, element):
    rasters = [export_pixels(atlas, cell, size, 4) for cell in cells]
    metrics = [light_metric(raster, fit["lightRectsDensity4"], element) for raster in rasters]
    for values in zip(*metrics, strict=True):
        check(values[0] < min(values[1], values[3]) and values[2] > max(values[1], values[3]),
              f"Source dim/medium/bright/medium order differs: {values}")
    masks = [raster.getchannel("A").point([0] * 128 + [255] * 128) for raster in rasters]
    similarity = []
    for mask in masks:
        shared = ImageChops.darker(masks[0], mask).histogram()[255]
        union = ImageChops.lighter(masks[0], mask).histogram()[255]
        similarity.append(round(shared / union, 5))
    check(min(similarity) > 0.94, f"Stationary silhouette drift exceeds threshold: {similarity}")
    return metrics, similarity


def make_contact(directory, sequence):
    board = Image.new("RGB", (940, 850), "#1b2421")
    draw = ImageDraw.Draw(board)
    inputs = []
    for frame in sequence["frames"]:
        phase = frame["sourceFrameIndex"]
        x = 18 + phase * 225
        source = ROOT / frame["sourceFrameReference"]
        art = ROOT / frame["exports"]["4"]["file"]
        logical = ROOT / frame["exports"]["1"]["file"]
        for path, y, label, background, scale in ((source, 20, "Source x4", "#cecec2", 4),
                (art, 294, "Painted x4 on ivory", "#e8dfc7", 1), (art, 568, "Painted x4 on deep jade", "#203d32", 1),
                (logical, 568, "", "#203d32", 1)):
            if label:
                draw.text((x, y), f"{phase:02} {label}", fill="#f4e5c8")
                draw.rectangle((x, y + 19, x + 210, y + 255), fill=background)
            pixels = Image.open(path).convert("RGBA")
            if scale != 1:
                pixels = pixels.resize(tuple(n * scale for n in pixels.size), Image.Resampling.NEAREST)
            offset = (x + 2, y + 19) if label else (x + 166, y + 194)
            board.paste(pixels, offset, pixels)
            inputs.append({"file": rel(path), "sha256": sha(path)})
    path = directory / "phase-contact.png"
    board.save(path)
    write(Path(str(path) + ".source.json"), {"file": rel(path), "sha256": sha(path), "inputs": inputs,
          "sequenceSha256": sha(directory / "sequence.json"), **FLAGS})


def run(element, build, write_audit):
    directory = BASE / str(element)
    sequence_path = directory / "sequence.json"
    contract, metrics = verified_source(element)
    fit_path = directory / "paint-fit.json"
    fit = read(fit_path)
    version = fit["version"]
    size, frame_offset, map_offset = GEOMETRY[element]
    atlas, atlas_path, generation = generation_evidence(directory, contract, version)
    cells = fit_atlas(atlas, fit, size)
    painted_metrics, silhouette_similarity = measure_painted_phases(atlas, cells, fit, size, element)
    gen_path = Path(str(atlas_path) + ".generation.json")
    if build:
        check(not sequence_path.exists(), "Refusing to overwrite an existing candidate sequence")
        write(gen_path, generation)
    check(read(gen_path) == generation, "Saved generation evidence differs")
    master = {"file": rel(atlas_path), "sha256": generation["sha256"], "generationRecord": rel(gen_path),
              "generationRecordSha256": sha(gen_path), "fitFile": rel(fit_path), "fitSha256": sha(fit_path)}
    frames = []
    export_checks = []
    for phase, (source, cell) in enumerate(zip(contract["sourceFrames"], cells, strict=True)):
        frame = {"sourceFrameIndex": phase, "sourceFrameSize": size, "sourceFrameOffset": frame_offset,
                 "sourceMapElemOffset": map_offset, "sourceFrameReference": source["file"],
                 "sourceFrameReferenceSha256": source["sha256"], "structuralEmpty": False,
                 "sourceFullyTransparentPixels": False, "aliasOf": None, **UNKNOWN, **FLAGS}
        exports = {}
        for density, folder in DENSITIES.items():
            path = directory / folder / f"frame-{phase:03}.png"
            extent = tuple(n * density for n in size)
            raster = export_pixels(atlas, cell, size, density)
            check(raster.getchannel("A").getextrema() == (0, 255), "Candidate should preserve true alpha")
            if build:
                path.parent.mkdir(exist_ok=True)
                raster.save(path)
            actual = Image.open(path)
            check(actual.mode == "RGBA" and actual.size == extent and actual.tobytes() == raster.tobytes(), "Export pixels differ")
            record = {**frame, "file": rel(path), "sha256": sha(path), "decodedRgbaSha256": digest(raster.tobytes()),
                      "width": actual.width, "height": actual.height, "mode": actual.mode, "exportDensity": density,
                      "alphaExtrema": [0, 255], "sourceFrameOffsetRaw": frame_offset, "sourceMapElemOffsetRaw": map_offset,
                      "sourceFrameOffsetAtDensity": [n * density for n in frame_offset],
                      "sourceMapElemOffsetAtDensity": [n * density for n in map_offset], "derivedFrom": master,
                      "operation": {"type": "integer crop and uniform premultiplied-alpha LANCZOS resize",
                                    "nonUniformStretch": False, **cell}}
            sidecar = Path(str(path) + ".source.json")
            if build:
                write(sidecar, record)
            check(read(sidecar) == record, "Export lineage differs")
            exports[str(density)] = record
            export_checks.append({"sourceFrameIndex": phase, "density": density, "file": rel(path),
                                  "sha256": record["sha256"], "exactPixelMatch": True})
        frames.append({**frame, "exports": exports})
    counts = {str(density): len({frame["exports"][str(density)]["decodedRgbaSha256"] for frame in frames}) for density in DENSITIES}
    check(all(value == COUNT for value in counts.values()), "Duplicate frame within sequence")
    contract_path = directory / "source-contract.json"
    sequence = {"schemaVersion": 1, "createdAtUTC": stamp() if build else read(sequence_path)["createdAtUTC"],
                "elementId": element, "family": "common", "sourceResourcePath": contract["sourceResourcePath"],
                "sourceRawSHA256": contract["sourceRawSHA256"], "sourceContract": rel(contract_path),
                "sourceContractSha256": sha(contract_path), "sourceDeclaredFrameCount": COUNT, "sourceDeclaredDirections": 1,
                "sourceFrameOrder": list(range(COUNT)), "sourceFrameIndices": list(range(COUNT)), "sourceEmptyPositions": [],
                "sourceAliasPositions": [], "allResourceFramePositionsPresent": True, "sourceMapElemOffset": map_offset,
                "sourceFootprintCells": contract["sourceFootprintCells"], "sourceGridAttr": contract["sourceGridAttr"],
                "selectedNativeAtlas": rel(atlas_path), "nativeAtlasSize": list(atlas.size),
                "ownRepresentativeFramesGenerated": COUNT, "uniqueOwnRgbaFrames": counts, "frames": frames,
                "previews": [rel(directory / "phase-contact.png")], "userReviewStatus": "pending", **UNKNOWN, **FLAGS}
    if build:
        write(sequence_path, sequence)
        make_contact(directory, sequence)
    check(read(sequence_path) == sequence, "Sequence manifest differs")
    contact = directory / "phase-contact.png"
    contact_record = read(Path(str(contact) + ".source.json"))
    check(contact_record["sha256"] == sha(contact) and contact_record["sequenceSha256"] == sha(sequence_path) and
          all(sha(ROOT / item["file"]) == item["sha256"] for item in contact_record["inputs"]), "Preview differs")
    audit_path = directory / "source-chain-file-audit.json"
    audit = {"schemaVersion": 1, "elementId": element, "checkedAt": stamp() if build else read(audit_path)["checkedAt"],
             "verificationScript": rel(HERE), "verificationScriptSha256": sha(HERE),
             "sourceMemberHelperSha256": sha(Path(common.__file__)), "sequenceSha256": sha(sequence_path),
             "sourceContractSha256": sha(contract_path), "sourceDimgSha256": contract["sourceRawSHA256"],
             "sourceLightRects": [list(rect) for rect in SOURCE_LIGHT[element]], "sourceLightMetrics": metrics,
             "paintedLightMetricsDensity4": painted_metrics, "silhouetteIouAgainstFrame0Density4": silhouette_similarity,
             "exportChecks": export_checks,
             "previewSha256": sha(contact), "errors": [], **FLAGS, **UNKNOWN}
    if build or write_audit:
        write(audit_path, audit)
    check(read(audit_path) == audit, "Saved audit differs")
    print(f"{element}: {COUNT} source positions, {len(export_checks)} PNGs, SHA-256 {audit['sequenceSha256']}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("element", type=int, choices=IDS)
    parser.add_argument("--build", action="store_true")
    parser.add_argument("--write-audit", action="store_true")
    args = parser.parse_args()
    run(args.element, args.build, args.write_audit)
