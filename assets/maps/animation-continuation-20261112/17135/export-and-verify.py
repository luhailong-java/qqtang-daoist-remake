"""Export and verify the fixed 17135 atlas crop and source position bindings."""
from pathlib import Path
import argparse
import datetime
import hashlib
import importlib.util
import json

from PIL import Image, ImageDraw, ImageStat

ROOT = Path(__file__).resolve().parents[4]
BASE = Path(__file__).resolve().parent
ELEMENT = 17135
LOGICAL = (41, 43)
# A single in-slot 41:43 rectangle. All five alpha >= 8 silhouettes fit inside.
CROP = (73, 59, 442, 446)
CROP_SIZE = (369, 387)
PREVIEW = BASE / "previews" / "five-phase-contact.png"
GENERATION = BASE / "sequence-v1.png.generation.json"
ATLAS = BASE / "sequence-v1.png"
FALSE_FLAGS = {
    "accepted": False,
    "visualAccepted": False,
    "geometryAccepted": False,
    "stateCorrespondenceAccepted": False,
    "runtimeIntegrated": False,
}
UNKNOWN = {
    "sourceNativeDurationMs": None,
    "loopPolicy": None,
    "nativeFrameStateMeaning": None,
    "combinedRenderOrigin": None,
}


def rel(file):
    return file.relative_to(ROOT).as_posix()


def sha_bytes(data):
    return hashlib.sha256(data).hexdigest()


def sha(file):
    return sha_bytes(file.read_bytes())


def read(file):
    return json.loads(file.read_bytes())


def write(file, data):
    file.parent.mkdir(parents=True, exist_ok=True)
    file.write_bytes((json.dumps(data, ensure_ascii=False, indent=2) + "\n").encode("utf-8"))


def utc():
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


def require(value, message):
    if not value:
        raise ValueError(message)


def reference_evidence(contract, inputs):
    roles = [
        "Five downward source positions and cumulative light-state correspondence",
        "Current original downward jade arrow tile identity",
        "Sister upward atlas for matching outer frame, jade texture and registration only",
        "Confirmed Daoist chibi painted jade and metal finish",
        "Confirmed Daoist chibi painted jade and metal finish",
    ]
    references = []
    for path, role in zip(inputs["referenced_image_paths"], roles, strict=True):
        # Evidence records the actual submitted Windows absolute paths. References
        # resolve through project-relative paths so verification also works on CI.
        suffix = path.split("/qqtang-daoist-remake/", 1)[1]
        file = ROOT / suffix
        evidence = {"path": suffix, "sha256": sha(file), "purpose": role}
        if suffix == contract["currentOwnFirstFrame"]["file"]:
            identity = contract["currentOwnFirstFrame"]
            for name in ("generationRecord", "provenanceRecord"):
                evidence[name] = identity[name]
                evidence[name + "Sha256"] = sha(ROOT / identity[name])
            require(evidence["sha256"] == identity["sha256"], "Original identity changed")
        references.append(evidence)
    return references


def inspect_atlas(atlas):
    require(atlas.mode == "RGBA" and atlas.size == (1536, 1024), "Unexpected atlas")
    require(atlas.crop((1024, 512, 1536, 1024)).getchannel("A").getextrema()[1] <= 1,
            "Unused atlas slot must have no visible art")
    evidence = []
    base_luma = None
    inlay_regions = [
        (215, 303, 296, 333),
        (180, 250, 331, 267),
        (180, 208, 331, 225),
        (180, 167, 331, 184),
    ]
    for phase in range(5):
        x, y = (phase % 3) * 512, (phase // 3) * 512
        cell = atlas.crop((x, y, x + 512, y + 512))
        alpha = cell.getchannel("A")
        bounds = alpha.point(lambda value: 255 if value >= 8 else 0).getbbox()
        require(bounds and bounds[0] >= CROP[0] and bounds[1] >= CROP[1]
                and bounds[2] <= CROP[2] and bounds[3] <= CROP[3], "Crop clips visible tile")
        regions = [(0, 0, CROP[0], 512), (CROP[2], 0, 512, 512),
                   (CROP[0], 0, CROP[2], CROP[1]), (CROP[0], CROP[3], CROP[2], 512)]
        outside = max(alpha.crop(region).getextrema()[1] for region in regions)
        require(outside < 8, "Visible alpha outside common crop")
        luma = [round(ImageStat.Stat(cell.crop(rect).convert("L")).mean[0], 3)
                for rect in inlay_regions]
        if base_luma is None:
            base_luma = luma
        active = [value - base >= 40 for value, base in zip(luma, base_luma)]
        require(active == [i < phase for i in range(4)], "Wrong progressive light state")
        evidence.append({
            "sourceFrameIndex": phase,
            "cellRectLTRB": [x, y, x + 512, y + 512],
            "sourceRectLTRB": [x + CROP[0], y + CROP[1], x + CROP[2], y + CROP[3]],
            "alpha8BoundsWithinCell": list(bounds),
            "maxAlphaOutsideFixedCrop": outside,
            "inlayMeanLumaTriangleBottomMiddleTop": luma,
            "brightInlaysTriangleBottomMiddleTop": active,
        })
    return evidence


def export_frame(atlas, rect, density):
    extent = tuple(density * side for side in LOGICAL)
    return (atlas.crop(rect).convert("RGBa")
            .resize(extent, Image.Resampling.LANCZOS).convert("RGBA"))


def make_preview(sequence):
    width, height = 1010, 650
    margin, cell_width, cell_height = 30, 190, 200
    image = Image.new("RGB", (width, height), "#142921")
    draw = ImageDraw.Draw(image)
    for row, (title, background) in enumerate([
        ("Source frames", "#d8d8cc"), ("Own art on ivory", "#e8dfc7"), ("Own art on deep jade", "#203d32")
    ]):
        top = 23 + row * cell_height
        draw.text((margin, top), title, fill="#f6eddc")
        for frame in sequence["frames"]:
            phase = frame["sourceFrameIndex"]
            left = margin + phase * cell_width
            draw.rectangle((left, top + 20, left + cell_width - 8, top + cell_height - 2), fill=background)
            if row == 0:
                sprite = Image.open(ROOT / frame["sourceFrameReference"]).convert("RGBA")
                sprite = sprite.resize((164, 172), Image.Resampling.NEAREST)
            else:
                sprite = Image.open(ROOT / frame["exports"]["4"]["file"]).convert("RGBA")
            image.paste(sprite, (left + 9, top + 22), sprite)
            draw.text((left + 11, top + 23), str(phase), fill="#fff2d4", stroke_width=1, stroke_fill="#163227")
    PREVIEW.parent.mkdir(parents=True, exist_ok=True)
    image.save(PREVIEW)
    write(Path(str(PREVIEW) + ".source.json"), {
        "file": rel(PREVIEW), "sha256": sha(PREVIEW),
        "sequence": rel(BASE / "sequence.json"), "sequenceSha256": sha(BASE / "sequence.json"),
        "inputs": [
            {"file": f["sourceFrameReference"], "sha256": f["sourceFrameReferenceSha256"]}
            for f in sequence["frames"]
        ] + [{k: f["exports"]["4"][k] for k in ("file", "sha256")} for f in sequence["frames"]],
        "operation": "Read-only contact composition; source PNG shown x4 nearest and own RGBA x4 at saved resolution",
        "userReviewStatus": "pending", **FALSE_FLAGS,
    })


def build(contract, atlas, cells):
    submission = BASE / "submitted-input-v1.json"
    inputs = read(submission)
    tool = read(BASE / "builtin-submissions.json")["calls"][0]
    require(tool["input"] == inputs and inputs["transparent_background"] is True, "Tool input mismatch")
    prompt = inputs["prompt"].encode("utf-8")
    require((BASE / "prompt-v1.txt").read_bytes() == prompt, "Exact prompt bytes mismatch")
    config_file = ROOT / "config/image-generation.json"
    atlas_sha = sha(ATLAS)
    generation = {
        "schemaVersion": 1,
        "file": rel(ATLAS), "sha256": atlas_sha,
        "generatedAt": utc(),
        "timeEvidence": "Registration after built-in return; provider timestamp undisclosed",
        "width": atlas.width, "height": atlas.height, "format": "PNG", "storedMode": atlas.mode,
        "decodedRGBAAlphaExtrema": list(atlas.getchannel("A").getextrema()),
        "tool": "image_gen.imagegen", "route": "builtin", "art_source": "host_image",
        "configSnapshot": read(config_file),
        "configSource": {"path": rel(config_file), "sha256": sha(config_file)},
        "submittedParameters": {"model": None, "quality": None,
                                "transparent_background": True,
                                "referenced_image_paths": inputs["referenced_image_paths"]},
        "actualModel": None, "actualQuality": None,
        "unverifiedReason": "Built-in output supplied no actual model or quality metadata",
        "exactPrompt": inputs["prompt"],
        "promptFile": rel(BASE / "prompt-v1.txt"), "promptFileSha256": sha_bytes(prompt),
        "submittedPromptSha256": sha_bytes(prompt),
        "submittedInputFile": rel(submission), "submittedInputFileSha256": sha(submission),
        "references": reference_evidence(contract, inputs),
        "sourceContract": rel(BASE / "source-contract.json"),
        "sourceContractSha256": sha(BASE / "source-contract.json"),
        "evidence": {
            "builtinSubmissions": rel(BASE / "builtin-submissions.json"),
            "builtinSubmissionsSha256": sha(BASE / "builtin-submissions.json"),
            "functionStoreKey": "17135-input-v1",
            **tool["result"],
        },
        "operation": "New built-in RGBA atlas copied without pixel changes",
        **FALSE_FLAGS,
    }
    write(GENERATION, generation)
    mother = {"file": rel(ATLAS), "sha256": atlas_sha, "generationRecord": rel(GENERATION),
              "generationRecordSha256": sha(GENERATION)}
    frames = []
    for source, cell in zip(contract["sourceFrames"], cells, strict=True):
        phase = source["frameIndex"]
        require(phase == cell["sourceFrameIndex"], "Source order changed")
        require(tuple(source["sourceFrameSize"]) == LOGICAL, "Source size changed")
        raw_offset = source["sourceFrameOffset"]
        map_offset = contract["sourceMapElemOffset"]
        require(raw_offset == map_offset == [0, 0], "Source offsets changed")
        require(source["aliasOf"] is None and not source["structuralEmpty"], "Unexpected alias or empty")
        frame = {
            "sourceFrameIndex": phase,
            "sourceFrameSize": list(LOGICAL),
            "sourceFrameOffset": raw_offset,
            "sourceMapElemOffset": map_offset,
            "sourceFootprintCells": contract["sourceFootprintCells"],
            "sourceGridAttr": contract["sourceGridAttr"],
            "sourceFrameReference": source["file"],
            "sourceFrameReferenceSha256": source["sha256"],
            "sourceCanonicalRgbaSha256": source["canonicalRgbaSha256"],
            "structuralEmpty": False, "sourceFullyTransparentPixels": False,
            "aliasOf": None, "pixelEvidence": cell, "exports": {},
            **UNKNOWN, **FALSE_FLAGS,
        }
        for density, dirname in ((1, "frames-logical-x1"), (4, "frames-compatible-x4")):
            file = BASE / dirname / f"frame-{phase:03d}.png"
            file.parent.mkdir(parents=True, exist_ok=True)
            pixels = export_frame(atlas, cell["sourceRectLTRB"], density)
            pixels.save(file)
            output = {
                "file": rel(file), "sha256": sha(file), "decodedRgbaSha256": sha_bytes(pixels.tobytes()),
                "width": pixels.width, "height": pixels.height, "mode": pixels.mode,
                "alphaExtrema": list(pixels.getchannel("A").getextrema()), "exportDensity": density,
                "sourceElementId": ELEMENT, "sourceFrameIndex": phase, "sourceFrameSize": list(LOGICAL),
                "sourceFrameOffsetRaw": raw_offset, "sourceFrameOffsetAtDensity": [v * density for v in raw_offset],
                "sourceMapElemOffsetRaw": map_offset, "sourceMapElemOffsetAtDensity": [v * density for v in map_offset],
                "sourceFootprintCells": frame["sourceFootprintCells"], "sourceGridAttr": frame["sourceGridAttr"],
                "sourceFrameReference": source["file"], "sourceFrameReferenceSha256": source["sha256"],
                "derivedFrom": mother,
                "operation": {
                    "type": "fixed-aspect atlas crop and uniform resize",
                    "sourceRectLTRB": cell["sourceRectLTRB"], "sourceCropSize": list(CROP_SIZE),
                    "uniformScale": density / 9, "resampler": "premultiplied-alpha LANCZOS",
                    "alphaFitPerformed": False, "alphaNormalizationPerformed": False,
                    "nonUniformStretch": False, "newModelGeneration": False,
                },
                **UNKNOWN, **FALSE_FLAGS,
            }
            frame["exports"][str(density)] = output
            write(Path(str(file) + ".source.json"), output)
        frames.append(frame)
    sequence = {
        "schemaVersion": 1, "createdAtUTC": utc(), "elementId": ELEMENT, "family": "common",
        "sourceResourcePath": contract["sourceResourcePath"], "sourceRawSHA256": contract["sourceRawSHA256"],
        "sourceContract": rel(BASE / "source-contract.json"), "sourceContractSha256": sha(BASE / "source-contract.json"),
        "sourceDeclaredFrameCount": 5, "sourceDeclaredDirections": 1,
        "sourceFrameIndices": list(range(5)), "sourceFrameOrder": list(range(5)),
        "sourceEmptyPositions": [], "sourceAliasPositions": [],
        "sourceFootprintCells": contract["sourceFootprintCells"],
        "sourceMapElemOffset": contract["sourceMapElemOffset"], "sourceGridAttr": contract["sourceGridAttr"],
        "actualNativeAtlasSize": list(atlas.size), "selectedNativeAtlas": rel(ATLAS),
        "commonSourceCropSize": list(CROP_SIZE), "ownRepresentativeFramesGenerated": 5,
        "allResourceFramePositionsPresent": True, "frameBindingsProduced": 5,
        "frames": frames, "uniqueOwnRgbaFrames": {"1": 5, "4": 5},
        "nativeFrameTimingMs": None, **UNKNOWN, **FALSE_FLAGS,
        "userReviewStatus": "pending", "previews": [rel(PREVIEW)],
        "pending": ["Human source correspondence and visual review",
                    "Native timing, loop, state gameplay meaning and combined origin",
                    "Neighbor seam and live mobile view"],
    }
    write(BASE / "sequence.json", sequence)
    make_preview(sequence)


def verify(contract, atlas, cells):
    sequence_path = BASE / "sequence.json"
    sequence = read(sequence_path)
    generation = read(GENERATION)
    calls_file = BASE / "builtin-submissions.json"
    inputs = read(BASE / "submitted-input-v1.json")
    require(read(calls_file)["calls"][0]["input"] == inputs, "Submitted input record mismatch")
    require(generation["evidence"]["builtinSubmissionsSha256"] == sha(calls_file), "Call record changed")
    require(generation["submittedInputFileSha256"] == sha(BASE / "submitted-input-v1.json"), "Input SHA mismatch")
    prompt_bytes = inputs["prompt"].encode("utf-8")
    require(generation["exactPrompt"] == inputs["prompt"] and
            sha_bytes(prompt_bytes) == generation["submittedPromptSha256"] == sha(BASE / "prompt-v1.txt"),
            "Exact prompt mismatch")
    require(generation["references"] == reference_evidence(contract, inputs), "Reference evidence changed")
    require(generation["actualModel"] is None and generation["actualQuality"] is None, "Unverified model claim")
    require(generation["sha256"] == sha(ATLAS), "Master bytes changed")
    require(sequence["sourceContractSha256"] == sha(BASE / "source-contract.json"), "Source contract changed")
    require(sequence["sourceFrameIndices"] == sequence["sourceFrameOrder"] == list(range(5)), "Frame order mismatch")
    require(sequence["sourceDeclaredFrameCount"] == contract["sourceDeclaredFrames"] == 5, "Count mismatch")
    require(sequence["sourceMapElemOffset"] == contract["sourceMapElemOffset"] == [0, 0] and
            sequence["sourceFootprintCells"] == contract["sourceFootprintCells"] == [1, 1] and
            sequence["sourceGridAttr"] == contract["sourceGridAttr"] == [3855], "Map metadata mismatch")
    require(all(sequence[name] is None for name in UNKNOWN), "Inferred native meaning")
    require(all(sequence[name] is False for name in FALSE_FLAGS), "Inferred acceptance")
    spec = importlib.util.spec_from_file_location("reference_dimg", ROOT / "scripts/inspect-reference-dimg.py")
    decoder = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(decoder)
    package = contract["sourcePackage"]
    # Seek the exact pinned member range instead of reading unrelated resources.
    entry = package["entry"]
    with (ROOT / package["file"]).open("rb") as stream:
        stream.seek(entry["packageOffset"])
        compressed = stream.read(entry["compressedByteLength"])
    raw, compressed_sha = decoder.unpack_resource(compressed, dict(entry, packageOffset=0))
    require(compressed_sha == package["compressedStreamSha256"] and
            sha_bytes(raw) == contract["sourceRawSHA256"] == sequence["sourceRawSHA256"], "Source member SHA mismatch")
    metadata, _ = decoder.inspect_dimg(raw, metadata_only=True)
    source_checks, exports = [], []
    pixel_hashes = {1: set(), 4: set()}
    for frame, source, native, cell in zip(sequence["frames"], contract["sourceFrames"],
                                           metadata["frames"], cells, strict=True):
        phase = frame["sourceFrameIndex"]
        require(phase == source["frameIndex"] == native["index"] == cell["sourceFrameIndex"], "Position mismatch")
        require(frame["sourceFrameSize"] == source["sourceFrameSize"] ==
                [native["width"], native["height"]] == list(LOGICAL), "Frame size mismatch")
        require(frame["sourceFrameOffset"] == source["sourceFrameOffset"] == native["frameOffset"] == [0, 0],
                "Frame offset mismatch")
        require(frame["aliasOf"] is source["aliasOf"] is None and
                not frame["structuralEmpty"] and not native["empty"], "Alias/empty mismatch")
        data_start = native["pixelDataOffset"]
        decoded = decoder.decode_frame_pixels(raw[data_start:data_start + native["pixelByteLength"]],
                                              native["pixelMode"], native["width"], native["height"])
        source_file = ROOT / source["file"]
        source_pixels = Image.open(source_file).convert("RGBA")
        require(source_pixels.tobytes() == decoded and
                sha_bytes(decoded) == source["decodedRgbaSha256"], "Source PNG decode mismatch")
        require(sha(source_file) == source["sha256"] == frame["sourceFrameReferenceSha256"], "Source PNG SHA mismatch")
        require(source_pixels.getchannel("A").getextrema() == (0, 255), "Source alpha mismatch")
        source_checks.append({"frameIndex": phase, "sha256": sha(source_file), "decodedFromPinnedMember": True})
        for density in (1, 4):
            entry = frame["exports"][str(density)]
            file = ROOT / entry["file"]
            pixels = Image.open(file)
            require(pixels.size == tuple(v * density for v in LOGICAL) and pixels.mode == "RGBA",
                    "Export format or canvas mismatch")
            require(sha(file) == entry["sha256"] and read(Path(str(file) + ".source.json")) == entry,
                    "Export provenance mismatch")
            expected = export_frame(atlas, cell["sourceRectLTRB"], density)
            pixel_hash = sha_bytes(pixels.tobytes())
            require(pixels.tobytes() == expected.tobytes() and pixel_hash == entry["decodedRgbaSha256"],
                    "Fixed crop or uniform resize mismatch")
            require(entry["operation"]["sourceRectLTRB"] == cell["sourceRectLTRB"] and
                    entry["operation"]["uniformScale"] == density / 9, "Transform mismatch")
            require(entry["sourceFrameOffsetRaw"] == entry["sourceFrameOffsetAtDensity"] ==
                    entry["sourceMapElemOffsetRaw"] == entry["sourceMapElemOffsetAtDensity"] == [0, 0],
                    "Export offset mismatch")
            require(all(entry[name] is False for name in FALSE_FLAGS), "Inferred frame acceptance")
            require(all(entry[name] is None for name in UNKNOWN), "Inferred frame semantics")
            low, high = pixels.getchannel("A").getextrema()
            require(low <= 4 and high >= 248, "Export alpha lacks clear cutout and opaque tile")
            require(entry["derivedFrom"]["generationRecordSha256"] == sha(GENERATION), "Master lineage mismatch")
            pixel_hashes[density].add(pixel_hash)
            exports.append({"file": rel(file), "sha256": sha(file), "density": density,
                            "extent": list(pixels.size), "exactPixelMatch": True})
    require(all(len(hashes) == 5 for hashes in pixel_hashes.values()), "Duplicate painted phases")
    preview = read(Path(str(PREVIEW) + ".source.json"))
    require(preview["sequenceSha256"] == sha(sequence_path) and preview["sha256"] == sha(PREVIEW),
            "Preview linkage mismatch")
    require(all(sha(ROOT / item["file"]) == item["sha256"] for item in preview["inputs"]),
            "Preview inputs changed")
    return {
        "schemaVersion": 1, "checkedAt": utc(), "elementId": ELEMENT,
        "scope": "Static source member, actual tool evidence, alpha, light states and pixel-exact exports",
        "sourceDimgSha256": sha_bytes(raw), "sourceContractSha256": sha(BASE / "source-contract.json"),
        "nativeMasterSha256": sha(ATLAS), "sequenceSha256": sha(sequence_path),
        "sourceFramePositions": len(source_checks), "sourceFrameChecks": source_checks,
        "exportChecks": exports, "previewSha256": sha(PREVIEW), "sourceAtlasMeasurements": cells,
        "errors": [], "actualModel": None, "actualQuality": None, **UNKNOWN, **FALSE_FLAGS,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--build", action="store_true", help="Export files and write static audit report")
    args = parser.parse_args()
    contract = read(BASE / "source-contract.json")
    require(contract["elementId"] == ELEMENT, "Unexpected source contract")
    atlas = Image.open(ATLAS)
    measurements = inspect_atlas(atlas)
    if args.build:
        require(not (BASE / "sequence.json").exists(), "Refusing to overwrite frozen sequence")
        build(contract, atlas, measurements)
    report = verify(contract, atlas, measurements)
    if args.build:
        write(BASE / "source-chain-file-audit.json", report)
    print(json.dumps({"elementId": ELEMENT, "sourceFramesVerified": report["sourceFramePositions"],
                      "exportPixelChecks": len(report["exportChecks"]), "errors": report["errors"],
                      "reportWritten": args.build}))


if __name__ == "__main__":
    main()
