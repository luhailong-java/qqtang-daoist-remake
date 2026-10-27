"""Read local package/index bytes and decode reference PNGs; never load clients.

Independently implemented from recorded binary-format observations. Package
resource names and frame pixels are evidence; ID/category mapping and client
map composition are deliberately not inferred as established facts.
Requires Pillow only for PNG encoding and the labelled inspection contact sheet.
"""
import argparse
import hashlib
import json
from pathlib import Path
import struct
import zlib

from PIL import Image, ImageDraw, ImageFont


ARCHIVE_SHA256 = "fd9d80320605bebbe6c5d42fa182dfbe74486405fa3718093513b10969fabec7"
ARCHIVE_URL = "https://github.com/kuuhaku1314/qqtang/releases/download/v1.3.4/QQTang-Local.zip"
DIMG_EVIDENCE = {
    "authority": "community-reverse-engineered-format-and-local-byte-checks",
    "communityCommit": "4b3a245fd985cabd4abd68ade6c282cc163d9edb",
    "localFormatEvidence": ".artifacts/reference-inputs/community-dimg-format.go",
    "officialSpecification": "unverified",
}


def sha256(data):
    return hashlib.sha256(data).hexdigest()


def parse_index(data, package_length):
    if len(data) < 16:
        raise ValueError("Index header truncated")
    words = list(struct.unpack_from("<4I", data))
    if words[2] != 16 or words[3] != len(data) - 16 or words[1] > 10000:
        raise ValueError("Unsupported index header layout")
    cursor = 16
    entries = []
    names = set()
    for ordinal in range(words[1]):
        start = cursor
        if cursor + 2 > len(data):
            raise ValueError("Index pathname length truncated")
        length = struct.unpack_from("<H", data, cursor)[0]
        cursor += 2
        if length == 0 or length > 4096 or cursor + length + 16 > len(data):
            raise ValueError("Index entry truncated or pathname excessive")
        raw_name = data[cursor:cursor + length]
        name = raw_name.decode("gb18030", errors="strict")
        cursor += length
        reserved, offset, raw_size, compressed_size = struct.unpack_from("<4I", data, cursor)
        cursor += 16
        if name.lower() in names:
            raise ValueError("Duplicate index pathname")
        if raw_size > 64 * 1024 * 1024 or compressed_size < 1 or offset + compressed_size > package_length:
            raise ValueError("Indexed stream exceeds package bounds or decode limit")
        names.add(name.lower())
        entries.append({"ordinal": ordinal, "indexOffset": start, "path": name,
                        "reservedWord": reserved, "packageOffset": offset,
                        "rawByteLength": raw_size, "compressedByteLength": compressed_size})
    if cursor != len(data):
        raise ValueError("Index has unparsed trailing bytes")
    return {"headerWords": words, "byteLength": len(data), "entries": entries}


def unpack_resource(package, entry):
    start = entry["packageOffset"]
    compressed = package[start:start + entry["compressedByteLength"]]
    decoder = zlib.decompressobj()
    data = decoder.decompress(compressed, entry["rawByteLength"] + 1)
    if not decoder.eof or decoder.unused_data or decoder.unconsumed_tail or len(data) != entry["rawByteLength"]:
        raise ValueError("Resource stream bounds or expanded length do not match index")
    return data, sha256(compressed)


def decode_frame_pixels(data, mode, width, height):
    count = width * height
    rgba = bytearray(count * 4)
    if mode in (3, 0x11000000):
        if len(data) != count * 3:
            raise ValueError("RGB565/alpha plane size mismatch")
        for pixel in range(count):
            value = data[2 * pixel] | (data[2 * pixel + 1] << 8)
            alpha = min(32, data[count * 2 + pixel])
            rgba[4 * pixel:4 * pixel + 4] = bytes((
                ((value >> 11) & 31) * 255 // 31,
                ((value >> 5) & 63) * 255 // 63,
                (value & 31) * 255 // 31,
                (alpha * 255 + 16) // 32,
            ))
    elif mode == 8:
        if len(data) != count * 4:
            raise ValueError("BGRA plane size mismatch")
        for pixel in range(count):
            blue, green, red, alpha = data[4 * pixel:4 * pixel + 4]
            rgba[4 * pixel:4 * pixel + 4] = bytes((red, green, blue, alpha))
    elif mode == 16:
        if len(data) != count * 3:
            raise ValueError("BGR plane size mismatch")
        for pixel in range(count):
            blue, green, red = data[3 * pixel:3 * pixel + 3]
            rgba[4 * pixel:4 * pixel + 4] = bytes((red, green, blue, 255))
    else:
        raise ValueError(f"Unsupported pixel mode {mode:#x}")
    return bytes(rgba)


def inspect_dimg(data):
    if len(data) < 40 or data[:8] != b"QQF\x1aDIMG":
        raise ValueError("DIMG signature/header mismatch")
    words = list(struct.unpack_from("<8I", data, 8))
    version, frame_info_size, frame_count, directions, unknown24, unknown28, canvas_width, canvas_height = words
    if version not in (65536, 65537) or frame_info_size != 24:
        raise ValueError("Unsupported DIMG version/frame-info declaration")
    if not 1 <= frame_count <= 1024 or not 1 <= directions <= 32 or frame_count % directions:
        raise ValueError("Invalid DIMG frame/direction count")
    frames = []
    first_visible = None
    cursor = 40
    total_pixels = 0
    for index in range(frame_count):
        offset = cursor
        if cursor + 16 > len(data):
            raise ValueError("DIMG frame header truncated")
        marker, x, y, mode = struct.unpack_from("<IiiI", data, cursor)
        cursor += 16
        if marker != 0:
            raise ValueError("Unsupported DIMG frame marker")
        frame = {"index": index, "offset": offset, "rawMarker": marker,
                 "frameOffset": [x, y], "pixelMode": mode}
        if mode == 0:
            frame.update({"empty": True, "width": 0, "height": 0})
        else:
            if cursor + 12 > len(data):
                raise ValueError("DIMG image header truncated")
            width, height, unknown_image_word = struct.unpack_from("<3I", data, cursor)
            cursor += 12
            frame.update({"width": width, "height": height, "unknownImageHeaderWord": unknown_image_word})
            if width == 0 and height == 0:
                frame["empty"] = True
            else:
                if not 1 <= width <= 4096 or not 1 <= height <= 4096:
                    raise ValueError("DIMG frame exceeds dimension bound")
                if mode not in (3, 0x11000000, 8, 16):
                    raise ValueError("DIMG pixel mode unsupported")
                total_pixels += width * height
                if total_pixels > 64 * 1024 * 1024:
                    raise ValueError("DIMG total frame pixels exceed bound")
                byte_length = width * height * (4 if mode == 8 else 3)
                if cursor + byte_length > len(data):
                    raise ValueError("DIMG pixel plane truncated")
                frame.update({"empty": False, "pixelDataOffset": cursor, "pixelByteLength": byte_length,
                              "encodedPixelSha256": sha256(data[cursor:cursor + byte_length])})
                if first_visible is None:
                    pixels = decode_frame_pixels(data[cursor:cursor + byte_length], mode, width, height)
                    first_visible = {"index": index, "width": width, "height": height, "pixels": pixels}
                    frame["decodedRgbaSha256"] = sha256(pixels)
                cursor += byte_length
        frames.append(frame)
    # No unrecognized container extension is silently accepted, even for 65537.
    if cursor != len(data):
        raise ValueError(f"DIMG has {len(data) - cursor} unrecognized trailing bytes")
    if first_visible is None:
        raise ValueError("DIMG has no visible frame")
    return {
        "byteLength": len(data), "sha256": sha256(data), "version": version,
        "frameInfoSize": frame_info_size, "frameCount": frame_count, "directions": directions,
        "unknownHeaderWordsAt24And28": [unknown24, unknown28],
        "declaredCanvas": [canvas_width, canvas_height],
        "declaredCanvasWithinBound": 1 <= canvas_width <= 4096 and 1 <= canvas_height <= 4096,
        "frames": frames, "parsedByteLength": cursor, "trailingByteLength": 0,
    }, first_visible


def encode_frame(frame, destination):
    image = Image.frombytes("RGBA", (frame["width"], frame["height"]), frame["pixels"])
    image.save(destination, format="PNG")
    return image, {"file": destination.name, "width": image.width, "height": image.height,
                   "sha256": sha256(destination.read_bytes()), "operation": "decode-first-visible-frame-no-resize-no-client-composition"}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project", type=Path, default=Path("."))
    args = parser.parse_args()
    project = args.project.resolve()
    inputs = project / ".artifacts/reference-inputs"
    output = project / "references/qqtang-map-data/visual-reference"
    archive_manifest = json.loads((inputs / "extracted/QQTang-Local/release-manifest.json").read_text(encoding="utf-8-sig"))
    archive_files = {item["path"]: item for item in archive_manifest["files"]}
    data_sources = {}
    package = (inputs / "object.pkg").read_bytes()
    index_bytes = (inputs / "object.idx").read_bytes()
    thumbnail_bytes = (inputs / "town01_4.img").read_bytes()
    for relative_path, data in (("data/object.pkg", package), ("data/object.idx", index_bytes), ("map/town01_4.img", thumbnail_bytes)):
        record = archive_files["runtime/client-patched/" + relative_path]
        if record["size"] != len(data) or record["sha256"] != sha256(data):
            raise ValueError("Input does not match community release manifest: " + relative_path)
        data_sources[relative_path] = {"archiveEntry": "QQTang-Local/" + record["path"], "byteLength": len(data), "sha256": sha256(data)}
    package_index = parse_index(index_bytes, len(package))
    by_path = {entry["path"].lower(): entry for entry in package_index["entries"]}
    town_map = json.loads((project / "references/qqtang-map-data/maps/town01_4.json").read_text(encoding="utf-8"))
    catalog = json.loads((project / "references/qqtang-map-data/catalog.json").read_text(encoding="utf-8"))
    catalog_matches = [entry for entry in catalog["entries"] if entry["id"] == 201]
    if len(catalog_matches) != 1 or catalog_matches[0]["mapFileName"] != "town01_4.map" or catalog_matches[0]["previewFileName"] != "town01_4.img":
        raise ValueError("Map ID 201 and its preview do not match static catalog data")
    element_data = json.loads((project / "references/qqtang-map-data/elements.json").read_text(encoding="utf-8"))
    by_id = {element["id"]: element for element in element_data["elements"]}
    used_ids = sorted({value for layer in town_map["layers"] for value in layer["values"] if value > 0})
    resources = []
    decoded_images = []
    # This numerical naming relation is labelled a candidate, never promoted to
    # a recovered client ID lookup table. The direct thumbnail needs no relation.
    for element_id in used_ids:
        candidate = f"object\\mapElem\\town\\elem{element_id - 3000}_stand.img"
        entry = by_path.get(candidate.lower())
        if entry is None:
            resources.append({"mapElementId": element_id, "candidatePath": candidate, "status": "missing-candidate"})
            continue
        data, compressed_hash = unpack_resource(package, entry)
        metadata, first_frame = inspect_dimg(data)
        element = by_id[element_id]
        resources.append({
            "mapElementId": element_id, "status": "decoded-candidate",
            "mappingStatus": "filename-numeric-and-family-inference-not-client-lookup-proof",
            "packageEntry": entry, "compressedStreamSha256": compressed_hash,
            "dimg": metadata, "elementFootprintCells": [element["widthCells"], element["heightCells"]],
            "mapElemOffsetRaw": element["imageOffset"], "gridAttrRaw": element["gridAttr"],
            "clientCompositionAnchor": "unverified-not-applied", "selectedFrame": first_frame["index"],
        })
        decoded_images.append((resources[-1], first_frame))
    thumbnail_meta, thumbnail_frame = inspect_dimg(thumbnail_bytes)
    output.mkdir(parents=True, exist_ok=True)
    for record, frame in decoded_images:
        image, encoded = encode_frame(frame, output / f"town-candidate-{record['mapElementId']}-frame.png")
        record["png"] = encoded
        record["_image"] = image
    thumbnail_image, thumbnail_png = encode_frame(thumbnail_frame, output / "town01_4-thumbnail-frame.png")
    # Inspection enlargement is explicitly separate from native 150x125 pixels.
    enlarged = thumbnail_image.resize((thumbnail_image.width * 4, thumbnail_image.height * 4), Image.Resampling.NEAREST)
    enlarged_path = output / "town01_4-thumbnail-4x-inspection.png"
    enlarged.save(enlarged_path)
    cell_width, cell_height, columns = 304, 220, 4
    rows = (len(decoded_images) + columns - 1) // columns
    sheet = Image.new("RGB", (columns * cell_width, 70 + rows * cell_height), (232, 232, 232))
    draw = ImageDraw.Draw(sheet)
    font = ImageFont.load_default(size=12)
    draw.text((16, 12), "REFERENCE ONLY - community client-patched data, original authenticity unverified", fill=(20, 20, 20), font=font)
    draw.text((16, 32), "Native frame pixels; candidate element IDs are filename inference. No map anchor applied.", fill=(120, 25, 20), font=font)
    for ordinal, record in enumerate(resources):
        if "_image" not in record:
            continue
        column, row = ordinal % columns, ordinal // columns
        x, y = column * cell_width, 70 + row * cell_height
        draw.rectangle((x + 2, y + 2, x + cell_width - 2, y + cell_height - 2), fill=(250, 250, 250), outline=(180, 180, 180))
        draw.text((x + 10, y + 8), f"candidate ID {record['mapElementId']} | {record['elementFootprintCells']} cells", fill=(20, 20, 20), font=font)
        frame = record["dimg"]["frames"][record["selectedFrame"]]
        draw.text((x + 10, y + 27), f"frame {frame['width']}x{frame['height']}  offset {frame['frameOffset']}", fill=(60, 60, 60), font=font)
        image = record.pop("_image")
        if image.width > cell_width - 20 or image.height > cell_height - 85:
            raise ValueError("Contact sheet would require scaling/cropping; adjust inspection layout instead")
        sheet.paste(image, (x + (cell_width - image.width) // 2, y + 57), image)
        draw.text((x + 10, y + cell_height - 22), f"mapElem offset raw: {record['mapElemOffsetRaw']}", fill=(70, 70, 70), font=font)
    sheet_path = output / "town01-building-candidates-contact-sheet.png"
    sheet.save(sheet_path)
    source = {
        "archiveUrl": ARCHIVE_URL, "archiveSha256": ARCHIVE_SHA256,
        "sourceType": "community-patched-client-data", "officialOriginalAuthenticity": "unverified",
        "inputFiles": data_sources, "externalCodeExecuted": False,
    }
    result = {
        "schemaVersion": 1, "generatedOn": "2026-10-26", "source": source,
        "formatEvidence": {**DIMG_EVIDENCE, "localFormatEvidenceSha256": sha256((inputs / "community-dimg-format.go").read_bytes())},
        "catalogSource": catalog["source"], "elementDefinitionSource": element_data["source"],
        "packageIndex": {"headerWords": package_index["headerWords"], "entryCount": len(package_index["entries"]), "parsedWholeIndex": True},
        "map": {"id": 201, "name": "中国城01", "file": "town01_4.map", "sha256": town_map["source"]["sha256"], "usedPositiveElementIds": used_ids},
        "thumbnail": {"catalogPreviewPath": "map/town01_4.img", "directCatalogFileMatch": True, "dimg": thumbnail_meta, "png": thumbnail_png,
                      "inspectionEnlargement": {"file": enlarged_path.name, "scale": 4, "resampling": "nearest-neighbor", "sha256": sha256(enlarged_path.read_bytes()), "nativeResolutionClaim": False}},
        "resources": resources,
        "contactSheet": {"file": sheet_path.name, "sha256": sha256(sheet_path.read_bytes()), "size": list(sheet.size), "sourceFramesScaled": False, "decorations": "neutral backdrop and data labels only"},
        "limitations": [
            "ID 3000+N to town/elemN filename relation is only a candidate until independently verified in client lookup data.",
            "Raw mapElem offset and DIMG frame offset are separate; no guessed anchor, sign, origin or map composition was applied.",
            "The map thumbnail is the catalog-linked source frame, not a reconstructed full-resolution map.",
            "Thumbnail canvas header is invalid/uninitialized; only its bounded declared frame is decoded.",
            "PNG files are source/structure reference only and are not copied into runtime assets.",
        ],
    }
    (output / "manifest.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"indexEntries": len(package_index["entries"]), "decodedCandidates": len(decoded_images), "mapThumbnailFrame": [thumbnail_image.width, thumbnail_image.height], "thumbnailCanvasValid": thumbnail_meta["declaredCanvasWithinBound"], "output": str(output)}, ensure_ascii=True))


if __name__ == "__main__":
    main()
