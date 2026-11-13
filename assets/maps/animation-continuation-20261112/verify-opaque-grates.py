"""Export and verify the new full-square grate atlases against pinned source members."""
from pathlib import Path
import argparse
import datetime
import hashlib
import importlib.util
import json

from PIL import Image, ImageDraw

HERE = Path(__file__).resolve()
ROOT = HERE.parents[3]
BASE = HERE.parent
IDS = (17033, 17037, 17038)
FLAGS = dict(accepted=False, visualAccepted=False, geometryAccepted=False,
             stateCorrespondenceAccepted=False, seamlessVerified=False, runtimeIntegrated=False)
UNKNOWN = dict(sourceNativeDurationMs=None, nativeFrameTimingMs=None, loopPolicy=None,
               nativeFrameStateMeaning=None, combinedRenderOrigin=None)
DENSITIES = {1: "frames-logical-x1", 4: "frames-compatible-x4"}


def rel(path):
    return path.relative_to(ROOT).as_posix()


def digest(data):
    return hashlib.sha256(data).hexdigest()


def sha(path):
    return digest(path.read_bytes())


def read(path):
    return json.loads(path.read_bytes())


def write(path, value):
    path.write_bytes((json.dumps(value, ensure_ascii=False, indent=2) + "\n").encode())


def check(condition, error):
    if not condition:
        raise ValueError(error)


def stamp():
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


def source_member(contract):
    spec = importlib.util.spec_from_file_location("reference_dimg", ROOT / "scripts/inspect-reference-dimg.py")
    decoder = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(decoder)
    pkg = contract["sourcePackage"]
    production = read(ROOT / contract["sourceProductionIndex"]["file"])
    definition = next(record for record in production["elements"] if record["elementId"] == contract["elementId"])
    package = ROOT / pkg["file"]
    index = ROOT / pkg["indexFile"]
    entry = pkg["entry"]
    check(definition["packageEntry"] == entry and definition["dimgSha256"] == contract["sourceRawSHA256"] and
          definition["compressedStreamSha256"] == pkg["compressedStreamSha256"], "Production member differs")
    check(definition["footprintCells"] == contract["sourceFootprintCells"] and
          definition["gridAttr"] == contract["sourceGridAttr"] and
          definition["mapElemOffsetRaw"] == contract["sourceMapElemOffset"], "Production source geometry differs")
    check(sha(index) == pkg["indexSha256AsPreviouslyVerified"], "Source index SHA mismatch")
    records = decoder.parse_index(index.read_bytes(), package.stat().st_size)["entries"]
    check(records[entry["ordinal"]] == entry, "Source member index mismatch")
    with package.open("rb") as stream:
        stream.seek(entry["packageOffset"])
        compressed = stream.read(entry["compressedByteLength"])
    raw, compressed_sha = decoder.unpack_resource(compressed, dict(entry, packageOffset=0))
    check(compressed_sha == pkg["compressedStreamSha256"] and digest(raw) == contract["sourceRawSHA256"],
          "Source member byte mismatch")
    metadata, _ = decoder.inspect_dimg(raw, metadata_only=True)
    return decoder, metadata, raw


def tool_evidence(directory, contract, version):
    request_path = directory / f"submitted-input-{version}.json"
    request = read(request_path)
    call_path = directory / ("builtin-submissions.json" if version == "v1" else f"builtin-submissions-{version}.json")
    call = next(record for record in read(call_path)["calls"] if record["input"] == request)
    check(call["input"] == request and request["transparent_background"] is False,
          "Actual generation input differs")
    prompt = directory / f"prompt-{version}.txt"
    check(prompt.read_bytes() == request["prompt"].encode(), "Exact prompt bytes differ")
    roles = (("Six source phases and rail orientation", "Original first frame identity", "Sibling material reference",
              "Daoist Q paint style", "Daoist Q paint style") if version == "v1" else
             ("Six source phases and rail orientation", "First generated atlas edited for joint motion",
              "Daoist Q paint style", "Daoist Q paint style"))
    references = []
    for absolute, role in zip(request["referenced_image_paths"], roles, strict=True):
        path = ROOT / absolute.split("/qqtang-daoist-remake/", 1)[1]
        references.append({"path": rel(path), "sha256": sha(path), "purpose": role})
    board_path = directory / "source-phase-board.png"
    board_record = read(Path(str(board_path) + ".source.json"))
    board = Image.open(board_path).convert("RGBA")
    check(references[0]["path"] == board_record["file"] == rel(board_path) and
          references[0]["sha256"] == board_record["sha256"], "Source reference board differs")
    for phase, (item, source) in enumerate(zip(board_record["items"], contract["sourceFrames"], strict=True)):
        source_pixels = Image.open(ROOT / source["file"]).convert("RGBA")
        scaled = source_pixels.resize((400, 400), Image.Resampling.NEAREST)
        check(phase == item["sourceFrameIndex"] == source["frameIndex"] and
              item["file"] == source["file"] and item["sha256"] == source["sha256"] and
              board.crop(item["rect"]).tobytes() == scaled.tobytes(), "Source board phase differs")
    identity = contract["currentOwnFirstFrame"]
    check(sha(ROOT / identity["generationRecord"]) == identity["generationRecordSha256"] and
          sha(ROOT / identity["provenanceRecord"]) == identity["provenanceSha256"],
          "Original identity lineage differs")
    if version == "v1":
        check(references[1]["path"] == identity["file"] and references[1]["sha256"] == identity["sha256"],
              "Original identity reference differs")
    else:
        first_atlas = directory / "sequence-v1.png"
        first_generation = Path(str(first_atlas) + ".generation.json")
        first_record = read(first_generation)
        check(references[1]["path"] == rel(first_atlas) and references[1]["sha256"] == sha(first_atlas),
              "First atlas reference differs")
        first_call = tool_evidence(directory, contract, "v1")
        check(sha(first_atlas) == first_record["sha256"] and
              all(first_record[key] == value for key, value in first_call.items()), "First atlas evidence differs")
        references[1].update(generationRecord=rel(first_generation), generationRecordSha256=sha(first_generation))
    return {
        "promptFile": rel(prompt), "promptFileSha256": sha(prompt), "exactPrompt": request["prompt"],
        "submittedPromptSha256": sha(prompt), "submittedInputFile": rel(request_path),
        "submittedInputFileSha256": sha(request_path), "references": references,
        "submittedParameters": dict(request, model=None, quality=None),
        "actualModel": None, "actualQuality": None,
        "evidence": {"builtinSubmissions": rel(call_path), "builtinSubmissionsSha256": sha(call_path),
                     "functionStoreKey": f"{contract['elementId']}-input-{version}", **call["result"]},
    }


def cell_rect(phase):
    left, top = phase % 3 * 512, phase // 3 * 512
    return [left, top, left + 512, top + 512]


def resize(atlas, phase, density):
    return (atlas.crop(cell_rect(phase)).convert("RGBa")
            .resize((40 * density, 40 * density), Image.Resampling.LANCZOS).convert("RGBA"))


def make_preview(directory, sequence):
    board = Image.new("RGB", (1128, 608), "#1b2421")
    draw = ImageDraw.Draw(board)
    rows = ((20, "Exact source frames x4", "source"), (221, "Original painted candidates x4", "4"),
            (424, "Logical-size candidates x1", "1"))
    inputs = []
    for top, title, density in rows:
        draw.text((18, top), title, fill="#f4e5c8")
        for frame in sequence["frames"]:
            phase = frame["sourceFrameIndex"]
            x = 18 + phase * 183
            if density == "source":
                path = ROOT / frame["sourceFrameReference"]
                pixels = Image.open(path).resize((160, 160), Image.Resampling.NEAREST)
            else:
                path = ROOT / frame["exports"][density]["file"]
                pixels = Image.open(path)
            pixels = pixels.convert("RGBA")
            y = top + 24
            board.paste(pixels, (x, y), pixels)
            draw.text((x, y + pixels.height + 2), str(phase), fill="#f4e5c8")
            inputs.append({"file": rel(path), "sha256": sha(path)})
    path = directory / "phase-contact.png"
    board.save(path)
    write(Path(str(path) + ".source.json"), {"file": rel(path), "sha256": sha(path), "inputs": inputs,
          "sequenceSha256": sha(directory / "sequence.json"), "userReviewStatus": "pending", **FLAGS})


def build(directory, contract, atlas, atlas_path, evidence):
    generation_path = Path(str(atlas_path) + ".generation.json")
    config = ROOT / "config/image-generation.json"
    write(generation_path, {
        "schemaVersion": 1, "file": rel(atlas_path), "sha256": sha(atlas_path),
        "generatedAt": stamp(), "timeEvidence": "UTC registration after host output",
        "width": atlas.width, "height": atlas.height, "format": "PNG",
        "storedMode": atlas.mode, "decodedRGBAAlphaExtrema": [255, 255],
        "tool": "image_gen.imagegen", "route": "builtin", "art_source": "host_image",
        "configSnapshot": read(config), "configSource": {"path": rel(config), "sha256": sha(config)},
        "sourceContract": rel(directory / "source-contract.json"),
        "sourceContractSha256": sha(directory / "source-contract.json"),
        "operation": "Native full-square atlas copied without changing image pixels", **evidence, **FLAGS,
    })
    master = {"file": rel(atlas_path), "sha256": sha(atlas_path), "generationRecord": rel(generation_path),
              "generationRecordSha256": sha(generation_path)}
    frames = []
    for source in contract["sourceFrames"]:
        phase = source["frameIndex"]
        common = {
            "sourceFrameIndex": phase, "sourceFrameSize": source["sourceFrameSize"],
            "sourceFrameOffset": source["sourceFrameOffset"], "sourceMapElemOffset": contract["sourceMapElemOffset"],
            "sourceGridAttr": contract["sourceGridAttr"], "sourceFootprintCells": contract["sourceFootprintCells"],
            "sourceFrameReference": source["file"], "sourceFrameReferenceSha256": source["sha256"],
            "structuralEmpty": False, "sourceFullyTransparentPixels": False, "aliasOf": None,
            **UNKNOWN, **FLAGS,
        }
        exports = {}
        for density, folder in DENSITIES.items():
            path = directory / folder / f"frame-{phase:03d}.png"
            path.parent.mkdir(exist_ok=True)
            pixels = resize(atlas, phase, density)
            pixels.save(path)
            entry = {
                **common, "file": rel(path), "sha256": sha(path), "decodedRgbaSha256": digest(pixels.tobytes()),
                "width": pixels.width, "height": pixels.height, "mode": pixels.mode,
                "alphaExtrema": [255, 255], "exportDensity": density,
                "sourceElementId": contract["elementId"], "sourceFrameOffsetRaw": source["sourceFrameOffset"],
                "sourceFrameOffsetAtDensity": [v * density for v in source["sourceFrameOffset"]],
                "sourceMapElemOffsetRaw": contract["sourceMapElemOffset"],
                "sourceMapElemOffsetAtDensity": [v * density for v in contract["sourceMapElemOffset"]],
                "derivedFrom": master,
                "operation": {"type": "whole-cell crop and uniform resize", "sourceRectLTRB": cell_rect(phase),
                              "uniformScale": 40 * density / 512, "resampler": "premultiplied-alpha LANCZOS",
                              "alphaFitPerformed": False, "nonUniformStretch": False, "newModelGeneration": False},
            }
            write(Path(str(path) + ".source.json"), entry)
            exports[str(density)] = entry
        frames.append({**common, "exports": exports})
    sequence = {
        "schemaVersion": 1, "createdAtUTC": stamp(), "elementId": contract["elementId"], "family": "common",
        "sourceResourcePath": contract["sourceResourcePath"], "sourceRawSHA256": contract["sourceRawSHA256"],
        "sourceContract": rel(directory / "source-contract.json"), "sourceContractSha256": sha(directory / "source-contract.json"),
        "sourceDeclaredFrameCount": 6, "sourceDeclaredDirections": 1,
        "sourceFrameIndices": list(range(6)), "sourceFrameOrder": list(range(6)),
        "sourceEmptyPositions": [], "sourceAliasPositions": [], "allResourceFramePositionsPresent": True,
        "sourceFootprintCells": contract["sourceFootprintCells"], "sourceMapElemOffset": contract["sourceMapElemOffset"],
        "sourceGridAttr": contract["sourceGridAttr"], "selectedNativeAtlas": rel(atlas_path),
        "actualNativeAtlasSize": list(atlas.size), "nativeCompleteCellSize": [512, 512],
        "ownRepresentativeFramesGenerated": 6, "frameBindingsProduced": 6,
        "uniqueOwnRgbaFrames": {"1": 6, "4": 6}, "frames": frames,
        "userReviewStatus": "pending", "previews": [rel(directory / "phase-contact.png")],
        "pending": ["Human phase, seam and in-map visual review", "Native timing, state semantics, loop and combined origin"],
        **UNKNOWN, **FLAGS,
    }
    write(directory / "sequence.json", sequence)
    make_preview(directory, sequence)


def verify(directory, contract, atlas, atlas_path, evidence):
    sequence_path = directory / "sequence.json"
    seq = read(sequence_path)
    gen_path = Path(str(atlas_path) + ".generation.json")
    gen = read(gen_path)
    check(gen["sha256"] == sha(atlas_path) and all(gen[key] == value for key, value in evidence.items()),
          "Generation record differs")
    decoder, metadata, raw = source_member(contract)
    check(metadata["frameCount"] == 6 and metadata["directions"] == 1 and metadata["declaredCanvas"] == [40, 40],
          "Source layout differs")
    check(seq["elementId"] == contract["elementId"] and seq["sourceFrameOrder"] == list(range(6)) and
          seq["sourceDeclaredFrameCount"] == 6 and seq["sourceRawSHA256"] == contract["sourceRawSHA256"] and
          seq["sourceContractSha256"] == sha(directory / "source-contract.json"), "Sequence identity differs")
    check(seq["sourceFootprintCells"] == contract["sourceFootprintCells"] == [1, 1] and
          seq["sourceGridAttr"] == contract["sourceGridAttr"] == [3855] and
          seq["sourceMapElemOffset"] == contract["sourceMapElemOffset"] == [0, 0], "Map geometry differs")
    check(all(seq[key] is value for key, value in (UNKNOWN | FLAGS).items()), "Speculative status")
    decoded_sources, verified_exports = [], []
    distinct = {density: set() for density in DENSITIES}
    for phase, (native, source, frame) in enumerate(zip(metadata["frames"], contract["sourceFrames"], seq["frames"], strict=True)):
        check(phase == native["index"] == source["frameIndex"] == frame["sourceFrameIndex"], "Order differs")
        check(not native["empty"] and not frame["structuralEmpty"] and frame["aliasOf"] is None, "Empty/alias differs")
        check([native["width"], native["height"]] == source["sourceFrameSize"] == frame["sourceFrameSize"] == [40, 40] and
              native["frameOffset"] == source["sourceFrameOffset"] == frame["sourceFrameOffset"] == [0, 0], "Native frame geometry differs")
        offset = native["pixelDataOffset"]
        decoded = decoder.decode_frame_pixels(raw[offset:offset + native["pixelByteLength"]], native["pixelMode"], 40, 40)
        src_path = ROOT / source["file"]
        check(digest(decoded) == source["decodedRgbaSha256"] and Image.open(src_path).convert("RGBA").tobytes() == decoded and
              sha(src_path) == source["sha256"] == frame["sourceFrameReferenceSha256"], "Source pixels differ")
        decoded_sources.append({"sourceFrameIndex": phase, "sha256": sha(src_path), "exactPinnedMemberDecode": True})
        for density in DENSITIES:
            entry = frame["exports"][str(density)]
            path = ROOT / entry["file"]
            pixels = Image.open(path)
            check(pixels.mode == "RGBA" and pixels.size == (density * 40, density * 40) and
                  pixels.getchannel("A").getextrema() == (255, 255), "Export dimensions/alpha differ")
            check(entry == read(Path(str(path) + ".source.json")) and entry["sha256"] == sha(path), "Export lineage differs")
            check(pixels.tobytes() == resize(atlas, phase, density).tobytes() and
                  digest(pixels.tobytes()) == entry["decodedRgbaSha256"], "Independent export reconstruction differs")
            check(entry["sourceMapElemOffset"] == entry["sourceFrameOffset"] ==
                  entry["sourceMapElemOffsetAtDensity"] == entry["sourceFrameOffsetAtDensity"] == [0, 0], "Export offsets differ")
            check(entry["derivedFrom"]["generationRecordSha256"] == sha(gen_path), "Master lineage differs")
            distinct[density].add(entry["decodedRgbaSha256"])
            verified_exports.append({"sourceFrameIndex": phase, "density": density, "sha256": sha(path),
                                     "file": rel(path), "exactPixelMatch": True})
    check(all(len(values) == 6 for values in distinct.values()), "Duplicate art phase")
    preview = directory / "phase-contact.png"
    record = read(Path(str(preview) + ".source.json"))
    check(record["sha256"] == sha(preview) and record["sequenceSha256"] == sha(sequence_path) and
          all(sha(ROOT / item["file"]) == item["sha256"] for item in record["inputs"]), "Preview inputs differ")
    return {
        "schemaVersion": 1, "elementId": contract["elementId"], "checkedAt": stamp(),
        "scope": "Pinned source decode, generation evidence, whole-square pixel reproduction and frame order",
        "verificationScript": rel(HERE), "verificationScriptSha256": sha(HERE),
        "sourceMemberSha256": digest(raw), "sourceChecks": decoded_sources, "exportChecks": verified_exports,
        "previewSha256": sha(preview), "sequenceSha256": sha(sequence_path), "errors": [], **UNKNOWN, **FLAGS,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("element", choices=IDS, type=int)
    parser.add_argument("--build", action="store_true")
    parser.add_argument("--version", choices=("v1", "v2"))
    parser.add_argument("--write-audit", action="store_true")
    args = parser.parse_args()
    directory = BASE / str(args.element)
    contract = read(directory / "source-contract.json")
    check(contract["elementId"] == args.element, "Wrong source element")
    sequence_path = directory / "sequence.json"
    version = args.version or (Path(read(sequence_path)["selectedNativeAtlas"]).stem.split("-")[-1]
                               if sequence_path.exists() else "v1")
    atlas_path = directory / f"sequence-{version}.png"
    atlas = Image.open(atlas_path)
    check(atlas.size == (1536, 1024) and atlas.convert("RGBA").getchannel("A").getextrema() == (255, 255),
          "Full-square opaque atlas required")
    evidence = tool_evidence(directory, contract, version)
    if "localAtlasSha256" in evidence["evidence"]:
        check(evidence["evidence"]["localAtlasSha256"] == sha(atlas_path), "Native host atlas copy differs")
    if args.build:
        replaces_first_pass = (version == "v2" and args.element == 17038 and sequence_path.exists() and
                               Path(read(sequence_path)["selectedNativeAtlas"]).name == "sequence-v1.png")
        check(not sequence_path.exists() or replaces_first_pass,
              "Refusing to overwrite sequence")
        build(directory, contract, atlas, atlas_path, evidence)
    report = verify(directory, contract, atlas, atlas_path, evidence)
    audit_path = directory / "source-chain-file-audit.json"
    if args.build or args.write_audit:
        write(audit_path, report)
    else:
        saved = read(audit_path)
        check(all(saved[key] == value for key, value in report.items() if key != "checkedAt"), "Saved audit differs")
    print(json.dumps({"elementId": args.element, "sourceFrames": len(report["sourceChecks"]),
                      "exports": len(report["exportChecks"]), "errors": report["errors"]}))


if __name__ == "__main__":
    main()
