"""Register original straight-grate paint to exact source motions and verify the exports."""
from pathlib import Path
import argparse
import importlib.util

from PIL import Image, ImageChops, ImageDraw

HERE = Path(__file__).resolve()
BASE = HERE.parent
SPEC = importlib.util.spec_from_file_location("grate_common", BASE / "verify-opaque-grates.py")
common = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(common)
ROOT, FLAGS, UNKNOWN = common.ROOT, common.FLAGS, common.UNKNOWN
read, write, sha, digest, check, rel, stamp = (common.read, common.write, common.sha, common.digest,
                                               common.check, common.rel, common.stamp)
PAIRS = {17130: 17131, 17132: 17133}
AXES = {17130: "y", 17132: "x"}
SIZE = 40
COUNT = 10
RAIL = 8
PERIOD = 20
STEP = 4
DENSITIES = common.DENSITIES


def canonical_pixels(image, axis):
    return image if axis == "y" else image.transpose(Image.Transpose.TRANSPOSE)


def verified_source(element):
    directory = BASE / str(element)
    path = directory / "source-contract.json"
    contract = read(path)
    decoder, metadata, raw = common.source_member(contract)
    check(contract["elementId"] == element and metadata["frameCount"] == COUNT and metadata["directions"] == 1 and
          metadata["declaredCanvas"] == [SIZE, SIZE] and contract["sourceMapElemOffset"] == [0, 0] and
          contract["sourceGridAttr"] == [3855] and contract["sourceFootprintCells"] == [1, 1], "Source header differs")
    board_file = directory / "source-phase-board.png"
    board = Image.open(board_file).convert("RGBA")
    board_record = read(Path(str(board_file) + ".source.json"))
    check(board_record["sha256"] == sha(board_file) and board_record["sourceContractSha256"] == sha(path),
          "Source reference board differs")
    frames = []
    for index, (native, frame, item) in enumerate(zip(metadata["frames"], contract["sourceFrames"], board_record["items"], strict=True)):
        check(index == native["index"] == frame["frameIndex"] == item["sourceFrameIndex"] and not native["empty"] and
              native["frameOffset"] == frame["sourceFrameOffset"] == [0, 0] and
              [native["width"], native["height"]] == frame["sourceFrameSize"] == [SIZE, SIZE], "Source geometry differs")
        offset = native["pixelDataOffset"]
        pixels = decoder.decode_frame_pixels(raw[offset:offset + native["pixelByteLength"]], native["pixelMode"], SIZE, SIZE)
        source = ROOT / frame["file"]
        raster = Image.open(source).convert("RGBA")
        check(raster.tobytes() == pixels and digest(pixels) == frame["decodedRgbaSha256"] and
              sha(source) == frame["sha256"] == item["sha256"] and item["file"] == frame["file"] and
              raster.getchannel("A").getextrema() == (255, 255), "Source decode differs")
        scale = item["uniformNearestScale"]
        expected = raster.resize((SIZE * scale, SIZE * scale), Image.Resampling.NEAREST)
        check(board.crop(item["rect"]).tobytes() == expected.tobytes(), "Source board phase differs")
        frames.append(raster)
    check(len({frame["decodedRgbaSha256"] for frame in contract["sourceFrames"]}) == COUNT, "Source aliases differ")
    return contract, frames


def source_motion(source_frames, axis):
    mesh_rows = []
    rail_rows = []
    for frame in source_frames:
        pixels = canonical_pixels(frame, axis)
        joints = []
        mesh = []
        for y in range(SIZE):
            red = [pixels.getpixel((x, y))[0] for x in range(SIZE)]
            check((red[4] < 80) == (red[35] < 80), "Source rails are out of phase")
            if red[4] < 80:
                joints.append(y)
            interior = red[9:31]
            if max(interior) - min(interior) > 13 and sum(a != b for a, b in zip(interior, interior[1:])) > 15:
                mesh.append(y)
        mesh_rows.append(mesh)
        rail_rows.append(joints)
    for index, (mesh, joints) in enumerate(zip(mesh_rows, rail_rows, strict=True)):
        check(len(mesh) == 14 and len(joints) == 2 and
              mesh == sorted((row + STEP * index) % SIZE for row in mesh_rows[0]) and
              joints == sorted((row + STEP * index) % SIZE for row in rail_rows[0]), "Source motion model differs")
    start = mesh_rows[0][0]
    span = len(mesh_rows[0]) // 2
    check(mesh_rows[0] == list(range(start, start + span)) + list(range(start + PERIOD, start + PERIOD + span)),
          "Source mesh is not a repeated strip")
    return {"sourceScanAxis": axis, "meshStart": start, "meshSpan": span, "meshPeriod": PERIOD,
            "railPeriod": SIZE, "advancePerSourcePosition": STEP, "sourceMeshRowsByPhase": mesh_rows,
            "sourceRailJointRowsByPhase": rail_rows,
            "measurement": "Mesh from repeated interior pixel alternation, joints from corresponding dark pixels in opposite rails."}


def verify_master(directory, contract):
    fit_path = directory / "paint-fit.json"
    fit = read(fit_path)
    evidence_path = directory / "builtin-material-submission.json"
    evidence = read(evidence_path)
    input_data = evidence["input"]
    prompt = directory / "prompt-material-v1.txt"
    check(prompt.read_bytes() == input_data["prompt"].encode() and input_data["transparent_background"] is False,
          "Exact generation input differs")
    reference_roles = ("Exact source frame 0", "Existing original identity", "Original material family",
                       "Daoist Q paint style", "Daoist Q paint style")
    references = []
    for path, role in zip(input_data["referenced_image_paths"], reference_roles, strict=True):
        path = ROOT / path.split("/qqtang-daoist-remake/", 1)[1]
        references.append({"file": rel(path), "sha256": sha(path), "role": role})
    identity = contract["currentOwnFirstFrame"]
    first_frame = contract["sourceFrames"][0]
    check(references[0]["file"] == first_frame["file"] and references[0]["sha256"] == first_frame["sha256"] and
          references[1]["file"] == identity["file"] and references[1]["sha256"] == identity["sha256"] and
          sha(ROOT / identity["generationRecord"]) == identity["generationRecordSha256"] and
          sha(ROOT / identity["provenanceRecord"]) == identity["provenanceSha256"], "Master reference lineage differs")
    master_path = directory / "painted-material-v1.png"
    master = Image.open(master_path)
    check(master.width == master.height == fit["nativeMasterSize"] and master.width >= 768 and
          master.convert("RGBA").getchannel("A").getextrema() == (255, 255) and master.format == "PNG" and
          evidence["result"]["localAtlasSha256"] == sha(master_path), "Master pixels or source differ")
    config = ROOT / "config/image-generation.json"
    gen = {"schemaVersion": 1, "file": rel(master_path), "sha256": sha(master_path), "width": master.width,
           "height": master.height, "storedMode": master.mode, "decodedRGBAAlphaExtrema": [255, 255],
           "tool": "image_gen.imagegen", "route": "builtin", "actualModel": None, "actualQuality": None,
           "configSource": {"file": rel(config), "sha256": sha(config)}, "references": references,
           "promptFile": rel(prompt), "promptFileSha256": sha(prompt), "submittedInput": input_data,
           "submissionEvidence": {"file": rel(evidence_path), "sha256": sha(evidence_path), **evidence["result"]}, **FLAGS}
    return master.convert("RGBA"), fit, gen


def fit_regions(master, fit, motion, density):
    master = canonical_pixels(master, motion["sourceScanAxis"]).convert("RGBa")
    rail_px = RAIL * density
    size_px = SIZE * density
    period_px = PERIOD * density
    center_px = size_px - 2 * rail_px
    mesh = motion["meshSpan"]
    junction_a, junction_b = motion["sourceRailJointRowsByPhase"][0]
    rail_target_breaks = [0, junction_a, junction_a + 1, junction_b, junction_b + 1, SIZE]
    regions = []
    for rail in fit["rails"]:
        left, right = rail["crossAxisBounds"]
        breaks = rail["movementAxisBreaks"]
        check(0 <= left < right <= master.width and len(breaks) == len(rail_target_breaks) and
              0 <= breaks[0] < breaks[-1] <= master.height and sorted(set(breaks)) == breaks, "Invalid rail crop")
        strip = Image.new("RGBa", (rail_px, size_px))
        for top, bottom, dest_top, dest_bottom in zip(breaks[:-1], breaks[1:], rail_target_breaks[:-1], rail_target_breaks[1:], strict=True):
            painted = master.crop((left, top, right, bottom))
            strip.paste(painted.resize((rail_px, (dest_bottom - dest_top) * density), Image.Resampling.LANCZOS),
                        (0, dest_top * density))
        regions.append(strip)
    check(len(regions) == 2, "Expected two painted rails")
    left, right = fit["center"]["crossAxisBounds"]
    top, middle, bottom = fit["center"]["movementAxisBreaks"]
    check(0 <= left < right <= master.width and 0 <= top < middle < bottom <= master.height, "Invalid center crop")
    center = Image.new("RGBa", (center_px, period_px))
    center.paste(master.crop((left, top, right, middle)).resize((center_px, mesh * density), Image.Resampling.LANCZOS), (0, 0))
    center.paste(master.crop((left, middle, right, bottom)).resize((center_px, (PERIOD - mesh) * density), Image.Resampling.LANCZOS),
                 (0, mesh * density))
    return regions[0], center, regions[1]


def render(regions, phase, motion, density):
    size = SIZE * density
    left, center, right = regions
    step = phase * STEP * density
    frame = Image.new("RGBa", (size, size))
    frame.paste(ImageChops.offset(left, 0, step), (0, 0))
    frame.paste(ImageChops.offset(right, 0, step), (size - right.width, 0))
    center = ImageChops.offset(center, 0, step + motion["meshStart"] * density)
    frame.paste(center, (left.width, 0))
    frame.paste(center, (left.width, center.height))
    return canonical_pixels(frame.convert("RGBA"), motion["sourceScanAxis"])


def preview(directory, sequence):
    board = Image.new("RGB", (940, 1000), "#1b2421")
    draw = ImageDraw.Draw(board)
    inputs = []
    for frame in sequence["frames"]:
        index = frame["sourceFrameIndex"]
        x = 18 + index % 5 * 183
        y = 20 + index // 5 * 490
        draw.text((x, y), f"Source {index:02d} x4", fill="#f4e5c8")
        source = ROOT / frame["sourceFrameReference"]
        board.paste(Image.open(source).resize((160, 160), Image.Resampling.NEAREST), (x, y + 20))
        inputs.append(source)
        for density, caption, height in (("4", "Painted x4", 190), ("1", "Logical x1", 385)):
            paint = ROOT / frame["exports"][density]["file"]
            draw.text((x, y + height), caption, fill="#f4e5c8")
            board.paste(Image.open(paint), (x, y + height + 20))
            inputs.append(paint)
    path = directory / "phase-contact.png"
    board.save(path)
    write(Path(str(path) + ".source.json"), {"file": rel(path), "sha256": sha(path),
          "sequenceSha256": sha(directory / "sequence.json"),
          "inputs": [{"file": rel(path), "sha256": sha(path)} for path in inputs], **FLAGS})


def run(base_element, build):
    paired = PAIRS[base_element]
    directory = BASE / str(base_element)
    if build:
        check(all(not (BASE / str(element) / "sequence.json").exists() for element in (base_element, paired)),
              "Refusing to overwrite an existing candidate sequence")
    contract, source = verified_source(base_element)
    reverse_contract, reverse = verified_source(paired)
    motion = source_motion(source, AXES[base_element])
    check(all(a.tobytes() == b.tobytes() for a, b in zip(source, reversed(reverse), strict=True)), "Reversed raster relation differs")
    master, fit, generation = verify_master(directory, contract)
    gen_path = directory / "painted-material-v1.png.generation.json"
    if build:
        write(gen_path, generation)
    check(read(gen_path) == generation, "Generation record differs")
    inputs = {"file": generation["file"], "sha256": generation["sha256"], "generationRecord": rel(gen_path),
              "generationRecordSha256": sha(gen_path), "fitFile": rel(directory / "paint-fit.json"),
              "fitSha256": sha(directory / "paint-fit.json")}
    regions = {density: fit_regions(master, fit, motion, density) for density in DENSITIES}
    for elem_contract in (contract, reverse_contract):
        elem = elem_contract["elementId"]
        elem_dir = BASE / str(elem)
        same_order = elem == base_element
        indices = list(range(COUNT)) if same_order else list(reversed(range(COUNT)))
        sequence_path = elem_dir / "sequence.json"
        frames = []
        checks = []
        for index, master_index in enumerate(indices):
            source_item = elem_contract["sourceFrames"][index]
            match = contract["sourceFrames"][master_index]
            check(source_item["decodedRgbaSha256"] == match["decodedRgbaSha256"], "Cross-element pixel identity differs")
            frame = {"sourceFrameIndex": index, "sourceFrameSize": [SIZE, SIZE], "sourceFrameOffset": [0, 0],
                     "sourceMapElemOffset": [0, 0], "sourceFrameReference": source_item["file"],
                     "sourceFrameReferenceSha256": source_item["sha256"], "structuralEmpty": False,
                     "sourceFullyTransparentPixels": False, "sourceAliasOfFrameIndex": None,
                     "matchingSourceFrame": {"elementId": base_element, "frameIndex": master_index,
                                             "decodedRgbaSha256": match["decodedRgbaSha256"]}, **UNKNOWN, **FLAGS}
            exports = {}
            for density, folder in DENSITIES.items():
                path = elem_dir / folder / f"frame-{index:03}.png"
                raster = render(regions[density], master_index, motion, density)
                if build:
                    path.parent.mkdir(exist_ok=True)
                    raster.save(path)
                actual = Image.open(path)
                check(actual.size == (SIZE * density, SIZE * density) and actual.mode == "RGBA" and
                      actual.getchannel("A").getextrema() == (255, 255) and actual.tobytes() == raster.tobytes(), "Export pixels differ")
                export = {**frame, "file": rel(path), "sha256": sha(path), "decodedRgbaSha256": digest(raster.tobytes()),
                          "width": actual.width, "height": actual.height, "mode": actual.mode,
                          "alphaExtrema": [255, 255], "exportDensity": density, "derivedFrom": inputs,
                          "sourceFrameOffsetRaw": [0, 0], "sourceFrameOffsetAtDensity": [0, 0],
                          "sourceMapElemOffsetRaw": [0, 0], "sourceMapElemOffsetAtDensity": [0, 0],
                          "operation": {"type": "Fit painted strips and apply source-measured circular shifts",
                                        "motionAxis": motion["sourceScanAxis"], "shiftLogicalPixels": master_index * STEP,
                                        "meshPeriodLogicalPixels": PERIOD, "railPeriodLogicalPixels": SIZE,
                                        "resampler": "premultiplied-alpha LANCZOS", "newModelGeneration": False}}
                sidecar = Path(str(path) + ".source.json")
                if build:
                    write(sidecar, export)
                check(read(sidecar) == export, "Frame lineage differs")
                exports[str(density)] = export
                checks.append({"file": rel(path), "sha256": sha(path), "exactPixelMatch": True})
            frames.append({**frame, "exports": exports})
        counts = {str(density): len({frame["exports"][str(density)]["decodedRgbaSha256"] for frame in frames}) for density in DENSITIES}
        check(all(value == COUNT for value in counts.values()), "Duplicate frame within sequence")
        contract_path = elem_dir / "source-contract.json"
        sequence = {"schemaVersion": 1, "createdAtUTC": stamp() if build else read(sequence_path)["createdAtUTC"],
                    "elementId": elem, "family": "common", "sourceResourcePath": elem_contract["sourceResourcePath"],
                    "sourceRawSHA256": elem_contract["sourceRawSHA256"], "sourceContract": rel(contract_path),
                    "sourceContractSha256": sha(contract_path), "sourceDeclaredFrameCount": COUNT,
                    "sourceDeclaredDirections": 1, "sourceFrameOrder": list(range(COUNT)), "sourceFrameIndices": list(range(COUNT)),
                    "sourceEmptyPositions": [], "sourceAliasPositions": [], "allResourceFramePositionsPresent": True,
                    "sourceMapElemOffset": [0, 0], "sourceGridAttr": [3855], "sourceFootprintCells": [1, 1],
                    "sourceMotionEvidence": motion, "materialMasterElementId": base_element, "materialInputs": inputs,
                    "sourceMatchedMasterPositions": indices, "ownMaterialMastersGeneratedForElement": int(same_order),
                    "derivedFramePositions": COUNT, "uniqueOwnRgbaFrames": counts, "frames": frames,
                    "previews": [rel(elem_dir / "phase-contact.png")], "userReviewStatus": "pending", **UNKNOWN, **FLAGS}
        if build:
            write(sequence_path, sequence)
            preview(elem_dir, sequence)
        check(read(sequence_path) == sequence, "Sequence manifest differs")
        contact = elem_dir / "phase-contact.png"
        contact_record = read(Path(str(contact) + ".source.json"))
        check(contact_record["sha256"] == sha(contact) and contact_record["sequenceSha256"] == sha(sequence_path) and
              all(sha(ROOT / item["file"]) == item["sha256"] for item in contact_record["inputs"]), "Preview differs")
        audit_path = elem_dir / "source-chain-file-audit.json"
        audit = {"schemaVersion": 1, "elementId": elem, "checkedAt": stamp() if build else read(audit_path)["checkedAt"],
                 "verificationScript": rel(HERE), "verificationScriptSha256": sha(HERE),
                 "sourceMemberHelperSha256": sha(Path(common.__file__)), "materialMasterSha256": generation["sha256"],
                 "sequenceSha256": sha(sequence_path), "sourceContractSha256": sha(contract_path),
                 "sourceDimgSha256": elem_contract["sourceRawSHA256"], "exactDecodedSourcePositions": COUNT,
                 "sourceMatchingOrder": indices, "exportChecks": checks, "previewSha256": sha(contact),
                 "errors": [], **FLAGS, **UNKNOWN}
        if build:
            write(audit_path, audit)
        check(read(audit_path) == audit, "Saved audit differs")
        print(f"{elem}: {COUNT} source positions, {len(checks)} PNGs, SHA-256 {audit['sequenceSha256']}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("element", type=int, choices=tuple(PAIRS))
    parser.add_argument("--build", action="store_true")
    args = parser.parse_args()
    run(args.element, args.build)
