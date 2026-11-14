"""Export animated map-prop art with native per-frame rectangles and separate offsets."""
from pathlib import Path
import argparse
import importlib.util

from PIL import Image, ImageChops, ImageDraw

HERE = Path(__file__).resolve()
BASE = HERE.parent
SPEC = importlib.util.spec_from_file_location("grate_common", BASE / "verify-opaque-grates.py")
common = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(common)
ROOT, FLAGS, UNKNOWN, DENSITIES = common.ROOT, common.FLAGS, common.UNKNOWN, common.DENSITIES
read, write, sha, digest, check, rel, stamp = (common.read, common.write, common.sha, common.digest,
                                               common.check, common.rel, common.stamp)
IDS = (17039, 17046, 17054)


def verified_source(element):
    directory = BASE / str(element)
    contract_path = directory / "source-contract.json"
    contract = read(contract_path)
    decoder, metadata, raw = common.source_member(contract)
    check(contract["elementId"] == element and metadata["frameCount"] == contract["sourceDeclaredFrames"] and
          metadata["directions"] == contract["sourceDeclaredDirections"] == 1 and
          metadata["declaredCanvas"] == contract["sourceDeclaredCanvas"], "Source declaration differs")
    board_path = directory / "source-phase-board.png"
    board = Image.open(board_path).convert("RGB")
    board_record = read(Path(str(board_path) + ".source.json"))
    check(board_record["sha256"] == sha(board_path) and board_record["sourceContractSha256"] == sha(contract_path),
          "Source reference board differs")
    for phase, (native, frame, item) in enumerate(zip(metadata["frames"], contract["sourceFrames"], board_record["items"], strict=True)):
        size = [native["width"], native["height"]]
        check(phase == native["index"] == frame["frameIndex"] == item["sourceFrameIndex"] and
              native["frameOffset"] == frame["sourceFrameOffset"] and size == frame["sourceFrameSize"] and
              not native["empty"] and frame["aliasOf"] is None, "Source frame differs")
        offset = native["pixelDataOffset"]
        pixels = decoder.decode_frame_pixels(raw[offset:offset + native["pixelByteLength"]], native["pixelMode"], *size)
        source = ROOT / frame["file"]
        raster = Image.open(source).convert("RGBA")
        alpha = raster.getchannel("A")
        canonical = raster.copy()
        canonical.paste((0, 0, 0, 0), (0, 0, *size), alpha.point([255] + [0] * 255))
        check(raster.tobytes() == pixels and digest(pixels) == frame["decodedRgbaSha256"] and
              digest(canonical.tobytes()) == frame["canonicalRgbaSha256"] and sha(source) == frame["sha256"] == item["sha256"] and
              item["file"] == frame["file"] and alpha.getextrema() == (0, 255), "Source decoded bytes differ")
        scale = item["uniformNearestScale"]
        expected = Image.new("RGBA", tuple(n * scale for n in size), tuple(board_record["boardBackdropRgb"]) + (255,))
        expected.alpha_composite(raster.resize(expected.size, Image.Resampling.NEAREST))
        check(board.crop(item["rect"]).tobytes() == expected.convert("RGB").tobytes(), "Source board position differs")
    check(len({frame["canonicalRgbaSha256"] for frame in contract["sourceFrames"]}) == metadata["frameCount"],
          "Unexpected source aliases")
    return contract


def generation(directory, contract, fit):
    version = fit["version"]
    path = directory / f"sequence-{version}.png"
    call_path = directory / f"builtin-submission-{version}.json"
    prompt_path = directory / f"prompt-{version}.txt"
    call = read(call_path)
    request = call["input"]
    atlas = Image.open(path)
    alpha_extrema = atlas.getchannel("A").getextrema()
    check(atlas.mode == "RGBA" and atlas.format == "PNG" and alpha_extrema[0] == 0 and alpha_extrema[1] >= 248 and
          sha(path) == call["result"]["localAtlasSha256"] and list(atlas.size) == fit["nativeAtlasSize"], "Host atlas differs")
    check(prompt_path.read_bytes() == request["prompt"].encode() and request["transparent_background"] is True,
          "Exact tool request differs")
    refs = []
    for path_string, role in zip(request["referenced_image_paths"], ("Source phase board", "Existing original identity",
            "Daoist Q art finish", "Daoist Q art finish"), strict=True):
        reference = ROOT / path_string.split("/qqtang-daoist-remake/", 1)[1]
        refs.append({"file": rel(reference), "sha256": sha(reference), "role": role})
    identity = contract["currentOwnFirstFrame"]
    check(refs[0]["file"] == rel(directory / "source-phase-board.png") and refs[1]["file"] == identity["file"] and
          refs[1]["sha256"] == identity["sha256"] and sha(ROOT / identity["generationRecord"]) == identity["generationRecordSha256"] and
          sha(ROOT / identity["provenanceRecord"]) == identity["provenanceSha256"], "Identity lineage differs")
    config = ROOT / "config/image-generation.json"
    record = {"schemaVersion": 1, "file": rel(path), "sha256": sha(path), "nativeSize": list(atlas.size),
              "mode": atlas.mode, "alphaExtrema": list(alpha_extrema), "tool": "image_gen.imagegen", "route": "builtin",
              "actualModel": None, "actualQuality": None, "config": {"file": rel(config), "sha256": sha(config)},
              "references": refs, "promptFile": rel(prompt_path), "promptSha256": sha(prompt_path), "exactSubmittedInput": request,
              "callRecord": {"file": rel(call_path), "sha256": sha(call_path), **call["result"]}, **FLAGS}
    return atlas, path, record


def registered_cells(atlas, contract, fit):
    width, height = atlas.size
    split_x = fit["atlasColumnBoundaries"]
    split_y = fit["atlasRowBoundaries"]
    check(split_x[0] == split_y[0] == 0 and split_x[-1] == width and split_y[-1] == height and
          len(split_x) == 4 and len(split_y) == 3 and split_x == sorted(set(split_x)) and split_y == sorted(set(split_y)),
          "Invalid atlas cell boundaries")
    count = contract["sourceDeclaredFrames"]
    alpha = atlas.getchannel("A")
    bounds = []
    for phase in range(6):
        x, y = phase % 3, phase // 3
        box = (split_x[x], split_y[y], split_x[x + 1], split_y[y + 1])
        cell = alpha.crop(box)
        if phase >= count:
            check(cell.getextrema()[1] < 8, "Unexpected visible art in unused slot")
            continue
        left, top, right, bottom = fit["atlasFrameCrops"][phase]
        w, h = contract["sourceFrames"][phase]["sourceFrameSize"]
        actual = cell.point([0] * 8 + [255] * 248).getbbox()
        check(actual and box[0] <= left <= box[0] + actual[0] and box[1] <= top <= box[1] + actual[1] and
              box[0] + actual[2] <= right <= box[2] and box[1] + actual[3] <= bottom <= box[3] and
              abs((right - left) * h - (bottom - top) * w) < 0.000001, "Exact-aspect crop clips visible art")
        bounds.append({"sourceRectLTRB": [left, top, right, bottom], "alpha8BoundsWithinCell": list(actual),
                       "cellRectLTRB": list(box), "uniformSourcePixelsPerLogicalPixel": (right - left) / w})
    check(len(bounds) == count, "Atlas cells do not cover source positions")
    return bounds


def render(atlas, cell, source, density):
    extent = tuple(n * density for n in source["sourceFrameSize"])
    rect = cell["sourceRectLTRB"]
    if any(isinstance(value, float) for value in rect):
        return atlas.convert("RGBa").resize(extent, Image.Resampling.LANCZOS, box=tuple(rect)).convert("RGBA")
    return atlas.crop(rect).convert("RGBa").resize(extent, Image.Resampling.LANCZOS).convert("RGBA")


def measure_body(atlas, cells, contract, fit):
    ref_frames = contract["sourceFrames"]
    width = max(frame["sourceFrameSize"][0] + frame["sourceFrameOffset"][0] for frame in ref_frames) * 4
    height = max(frame["sourceFrameSize"][1] + frame["sourceFrameOffset"][1] for frame in ref_frames) * 4
    masks = []
    for cell, source in zip(cells, ref_frames, strict=True):
        raster = render(atlas, cell, source, 4)
        mask = Image.new("L", (width, height))
        mask.paste(raster.getchannel("A").point([0] * 128 + [255] * 128), tuple(n * 4 for n in source["sourceFrameOffset"]))
        masks.append(mask.crop((0, height - 4 * fit["stationaryBodyHeightLogical"], width, height)))
    scores = []
    for mask in masks:
        intersection = ImageChops.darker(masks[0], mask).histogram()[255]
        union = ImageChops.lighter(masks[0], mask).histogram()[255]
        scores.append(round(intersection / union, 5))
    check(min(scores) >= 0.86, f"Stationary lower-body silhouette differs: {scores}")
    return scores


def contact(directory, sequence):
    frames = sequence["frames"]
    width = max(f["sourceFrameSize"][0] + f["sourceFrameOffset"][0] for f in frames) * 4
    height = max(f["sourceFrameSize"][1] + f["sourceFrameOffset"][1] for f in frames) * 4
    row_stride = height + 42
    stride = width + 18
    board = Image.new("RGB", (16 + len(frames) * stride, 16 + row_stride * 3), "#1b2421")
    draw = ImageDraw.Draw(board)
    inputs = []
    for frame in frames:
        phase = frame["sourceFrameIndex"]
        left = 12 + phase * stride
        source = ROOT / frame["sourceFrameReference"]
        art = ROOT / frame["exports"]["4"]["file"]
        for row, (file, label, background) in enumerate(((source, "Source", "#cecec2"), (art, "Painted on ivory", "#e8dfc7"),
                                                          (art, "Painted on deep jade", "#203d32"))):
            top = 12 + row * row_stride
            draw.text((left, top), f"{phase:02} {label} x4", fill="#f4e5c8")
            draw.rectangle((left, top + 16, left + width, top + 16 + height), fill=background)
            sprite = Image.open(file).convert("RGBA")
            if file == source:
                sprite = sprite.resize(tuple(n * 4 for n in sprite.size), Image.Resampling.NEAREST)
            off_x, off_y = frame["sourceFrameOffset"]
            board.paste(sprite, (left + off_x * 4, top + 16 + off_y * 4), sprite)
            inputs.append({"file": rel(file), "sha256": sha(file)})
    path = directory / "phase-contact.png"
    board.save(path)
    write(Path(str(path) + ".source.json"), {"file": rel(path), "sha256": sha(path), "inputs": inputs,
          "sequenceSha256": sha(directory / "sequence.json"), **FLAGS})


def run(element, build, write_audit):
    directory = BASE / str(element)
    sequence_path = directory / "sequence.json"
    contract = verified_source(element)
    fit_path = directory / "paint-fit.json"
    fit = read(fit_path)
    atlas, path, gen = generation(directory, contract, fit)
    cells = registered_cells(atlas, contract, fit)
    body = measure_body(atlas, cells, contract, fit)
    gen_path = Path(str(path) + ".generation.json")
    if build:
        check(not sequence_path.exists(), "Refusing to overwrite existing sequence")
        write(gen_path, gen)
    check(read(gen_path) == gen, "Generation record differs")
    master = {"file": rel(path), "sha256": sha(path), "generationRecord": rel(gen_path), "generationRecordSha256": sha(gen_path),
              "fitFile": rel(fit_path), "fitSha256": sha(fit_path)}
    map_offset = contract["sourceMapElemOffset"]
    frames, audits = [], []
    for phase, (source, cell) in enumerate(zip(contract["sourceFrames"], cells, strict=True)):
        offset = source["sourceFrameOffset"]
        frame = {"sourceFrameIndex": phase, "sourceFrameSize": source["sourceFrameSize"], "sourceFrameOffset": offset,
                 "sourceMapElemOffset": map_offset, "sourceFrameReference": source["file"], "sourceFrameReferenceSha256": source["sha256"],
                 "structuralEmpty": False, "sourceFullyTransparentPixels": False, "aliasOf": None, **UNKNOWN, **FLAGS}
        exports = {}
        for density, folder in DENSITIES.items():
            png = directory / folder / f"frame-{phase:03}.png"
            raster = render(atlas, cell, source, density)
            alpha_extrema = raster.getchannel("A").getextrema()
            check(alpha_extrema[0] == 0 and alpha_extrema[1] >= 248, "Export should retain true Alpha")
            if build:
                png.parent.mkdir(exist_ok=True)
                raster.save(png)
            actual = Image.open(png)
            check(actual.mode == "RGBA" and actual.size == raster.size and actual.tobytes() == raster.tobytes(), "Export pixels differ")
            record = {**frame, "file": rel(png), "sha256": sha(png), "decodedRgbaSha256": digest(raster.tobytes()), "mode": actual.mode,
                      "width": actual.width, "height": actual.height, "exportDensity": density, "alphaExtrema": list(alpha_extrema),
                      "sourceFrameOffsetRaw": offset, "sourceMapElemOffsetRaw": map_offset,
                      "sourceFrameOffsetAtDensity": [n * density for n in offset], "sourceMapElemOffsetAtDensity": [n * density for n in map_offset],
                      "derivedFrom": master, "operation": {"type": ("Uniform premultiplied LANCZOS export from fractional source rectangle"
                          if any(isinstance(n, float) for n in cell["sourceRectLTRB"]) else "Integer crop with uniform premultiplied LANCZOS resize"),
                                                                "nonUniformStretch": False, **cell}}
            sidecar = Path(str(png) + ".source.json")
            if build:
                write(sidecar, record)
            check(read(sidecar) == record, "Export record differs")
            exports[str(density)] = record
            audits.append({"sourceFrameIndex": phase, "density": density, "file": rel(png), "sha256": record["sha256"], "exactPixelMatch": True})
        frames.append({**frame, "exports": exports})
    counts = {str(d): len({frame["exports"][str(d)]["decodedRgbaSha256"] for frame in frames}) for d in DENSITIES}
    count = contract["sourceDeclaredFrames"]
    check(all(value == count for value in counts.values()), "Duplicate art phase")
    contract_path = directory / "source-contract.json"
    sequence = {"schemaVersion": 1, "createdAtUTC": stamp() if build else read(sequence_path)["createdAtUTC"],
                "elementId": element, "family": contract["family"], "sourceResourcePath": contract["sourceResourcePath"],
                "sourceRawSHA256": contract["sourceRawSHA256"], "sourceContract": rel(contract_path), "sourceContractSha256": sha(contract_path),
                "sourceDeclaredFrameCount": count, "sourceDeclaredDirections": 1, "sourceFrameOrder": list(range(count)),
                "sourceFrameIndices": list(range(count)), "sourceEmptyPositions": [], "sourceAliasPositions": [],
                "allResourceFramePositionsPresent": True, "sourceMapElemOffset": map_offset, "sourceGridAttr": contract["sourceGridAttr"],
                "sourceFootprintCells": contract["sourceFootprintCells"], "selectedNativeAtlas": rel(path), "nativeAtlasSize": list(atlas.size),
                "ownRepresentativeFramesGenerated": count, "uniqueOwnRgbaFrames": counts, "frames": frames,
                "previews": [rel(directory / "phase-contact.png")], "userReviewStatus": "pending", **UNKNOWN, **FLAGS}
    if build:
        write(sequence_path, sequence)
        contact(directory, sequence)
    check(read(sequence_path) == sequence, "Sequence manifest differs")
    preview = directory / "phase-contact.png"
    preview_record = read(Path(str(preview) + ".source.json"))
    check(preview_record["sha256"] == sha(preview) and preview_record["sequenceSha256"] == sha(sequence_path) and
          all(sha(ROOT / item["file"]) == item["sha256"] for item in preview_record["inputs"]), "Preview differs")
    audit_path = directory / "source-chain-file-audit.json"
    audit = {"schemaVersion": 1, "elementId": element, "checkedAt": stamp() if build else read(audit_path)["checkedAt"],
             "verificationScript": rel(HERE), "verificationScriptSha256": sha(HERE), "sourceMemberHelperSha256": sha(Path(common.__file__)),
             "sequenceSha256": sha(sequence_path), "sourceContractSha256": sha(contract_path), "sourceDimgSha256": contract["sourceRawSHA256"],
             "lowerBodySilhouetteIouInRelativeFrameOffsetSpace": body, "exportChecks": audits, "previewSha256": sha(preview),
             "errors": [], **FLAGS, **UNKNOWN}
    if build or write_audit:
        write(audit_path, audit)
    check(read(audit_path) == audit, "Saved audit differs")
    print(f"{element}: {count} source positions, {len(audits)} PNGs, SHA-256 {audit['sequenceSha256']}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("element", type=int, choices=IDS)
    parser.add_argument("--build", action="store_true")
    parser.add_argument("--write-audit", action="store_true")
    args = parser.parse_args()
    run(args.element, args.build, args.write_audit)
