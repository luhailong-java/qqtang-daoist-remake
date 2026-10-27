"""Build a data-only art worklist and bounded, deduplicated source references.

Only imports this project's independent DIMG inspector. Inspected Python,
client binaries and community executables are never imported or run.
"""
from pathlib import Path
from collections import Counter, defaultdict
import hashlib
import importlib.util
import json
import re
import struct

PROJECT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("local_reference_decoder", PROJECT / "scripts/inspect-reference-dimg.py")
decoder = importlib.util.module_from_spec(spec)
spec.loader.exec_module(decoder)
from PIL import Image, ImageDraw, ImageFont

GROUPS = {
    1: ("desert", "沙漠"), 2: ("snow", "冰雪"), 3: ("town", "中国城"),
    4: ("mine", "矿洞"), 5: ("water", "水面"), 6: ("field", "田野"),
    7: ("bomb", "炸弹场景"), 8: ("bun", "抢包山"), 9: ("pig", "小猪场景"),
    10: ("treasure", "寻宝"), 11: ("match", "比武"), 12: ("sculpture", "雕塑"),
    13: ("machine", "机械"), 14: ("box", "推箱子"), 15: ("practice", "练习"),
    16: ("exploration", "探险场景"), 17: ("common", "通用场景"), 18: ("pve", "探险关卡"),
}
MAPPING_STATUS = "candidate-numeric-prefix-family-cooccurrence-and-filename-suffix-not-client-lookup-proof"


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def digest(data):
    return hashlib.sha256(data).hexdigest()


def relative(path):
    return path.relative_to(PROJECT).as_posix()


def write_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def visible_identity(frame):
    """Dedup exact visible content, including transparent RGB/padding aliases.

    Original frame extent/offset remain in each element record; the sole PNG is
    the representative's native full frame, never a crop or runtime substitute.
    """
    image = Image.frombytes("RGBA", (frame["width"], frame["height"]), frame["pixels"])
    bbox = image.getchannel("A").getbbox()
    if not bbox:
        return image, digest(b"fully-transparent"), None
    cropped = image.crop(bbox)
    pixels = bytearray(cropped.tobytes())
    for offset in range(0, len(pixels), 4):
        if pixels[offset + 3] == 0:
            pixels[offset:offset + 3] = b"\x00\x00\x00"
    key = struct.pack("<2I", cropped.width, cropped.height) + pixels
    return image, digest(key), list(bbox)


def main():
    references = PROJECT / "references/qqtang-map-data"
    output = references / "visual-reference/families"
    inputs = PROJECT / ".artifacts/reference-inputs"
    elements_doc = read_json(references / "elements.json")
    elements = sorted(elements_doc["elements"], key=lambda item: item["id"])
    if len(elements) != 721 or len({item["id"] for item in elements}) != 721:
        raise ValueError("Expected exactly the inspected 721 unique elements")
    package, index_bytes = (inputs / "object.pkg").read_bytes(), (inputs / "object.idx").read_bytes()
    release = read_json(inputs / "extracted/QQTang-Local/release-manifest.json")
    release_files = {entry["path"]: entry for entry in release["files"]}
    input_evidence = {}
    for name, data in (("object.idx", index_bytes), ("object.pkg", package)):
        manifest = release_files["runtime/client-patched/data/" + name]
        if manifest["size"] != len(data) or manifest["sha256"] != digest(data):
            raise ValueError(name + " does not match community release bytes")
        input_evidence[name] = {"path": relative(inputs / name), "byteLength": len(data), "sha256": digest(data)}
    package_index = decoder.parse_index(index_bytes, len(package))
    by_path = {entry["path"].lower(): entry for entry in package_index["entries"]}
    package_family_counts = Counter()
    for entry in package_index["entries"]:
        match = re.fullmatch(r"object\\mapElem\\([^\\]+)\\elem\d+_stand\.img", entry["path"], re.I)
        if match:
            package_family_counts[match[1].lower()] += 1
    usage, family_cooccurrence = defaultdict(list), defaultdict(Counter)
    known_ids = {element["id"] for element in elements}
    unknown_map_ids = defaultdict(list)
    for file in sorted((references / "maps").glob("*.json")):
        source_map = read_json(file)
        catalog = source_map.get("catalogEntries", [])
        used = {value for layer in source_map["layers"] for value in layer["values"] if value > 0}
        for element_id in used:
            record = {"file": file.stem + ".map", "catalogIds": [entry["id"] for entry in catalog], "families": sorted({entry["family"] for entry in catalog})}
            if element_id in known_ids:
                usage[element_id].append(record)
            else:
                unknown_map_ids[element_id].append(file.stem + ".map")
        for group in {value // 1000 for value in used if value in known_ids}:
            for family in {entry["family"] for entry in catalog}:
                family_cooccurrence[group][family] += 1
    painted = {}
    art_inputs = []
    for manifest_path in sorted((PROJECT / "assets/maps").glob("*/art.json")):
        manifest = read_json(manifest_path)
        art_inputs.append({"file": relative(manifest_path), "sha256": digest(manifest_path.read_bytes())})
        for piece in manifest.get("pieces", []):
            path = PROJECT / piece["file"]
            if not path.is_file() or digest(path.read_bytes()) != piece["sha256"]:
                raise ValueError("Current original-art piece fails file/hash verification: " + piece["file"])
            provenance_candidates = [piece.get("provenanceRecord"), piece["file"] + ".provenance.json", piece["file"] + ".source.json"]
            provenance_path = next((item for item in provenance_candidates if item and (PROJECT / item).is_file()), None)
            if not provenance_path:
                raise ValueError("Original-art candidate lacks a retained per-piece source record: " + piece["file"])
            provenance = read_json(PROJECT / provenance_path)
            if provenance.get("elementId") != piece["elementId"] or provenance.get("sha256") != piece["sha256"]:
                raise ValueError("Original-art source record does not match piece: " + piece["file"])
            piece["provenanceRecord"] = provenance_path
            origins = piece.get("derivedFrom", {})
            origins = origins if isinstance(origins, list) else [origins]
            generation_records = [origin["generationRecord"] for origin in origins if origin.get("generationRecord")]
            if not generation_records:
                raise ValueError("Original-art candidate lacks generation provenance: " + piece["file"])
            for origin in origins:
                if origin.get("file") and origin.get("sha256"):
                    origin_path = PROJECT / origin["file"]
                    if not origin_path.is_file() or digest(origin_path.read_bytes()) != origin["sha256"]:
                        raise ValueError("Original-art source fails hash verification: " + origin["file"])
            painted[piece["elementId"]] = piece
    # Reuse already retained town source frames rather than duplicate references.
    existing_pictures = {}
    old_reference_manifest = references / "visual-reference/manifest.json"
    if old_reference_manifest.is_file():
        for record in read_json(old_reference_manifest).get("resources", []):
            png = record.get("png")
            if not png:
                continue
            existing = old_reference_manifest.parent / png["file"]
            if not existing.is_file() or digest(existing.read_bytes()) != png["sha256"]:
                raise ValueError("Existing reference frame hash mismatch: " + str(existing))
            with Image.open(existing) as image:
                frame = {"width": image.width, "height": image.height, "pixels": image.convert("RGBA").tobytes()}
            _, visible_hash, _ = visible_identity(frame)
            existing_pictures.setdefault(visible_hash, {"file": relative(existing), "sha256": png["sha256"], "nativeFrameSize": [frame["width"], frame["height"]]})
    prior_index_path = output / "index.json"
    prior_index = read_json(prior_index_path) if prior_index_path.is_file() else {}
    dimg_cache, visual_groups, family_images, records = {}, {}, defaultdict(list), []
    for element in elements:
        element_id = element["id"]
        group = element_id // 1000
        family, theme = GROUPS[group]
        candidate = f"object\\mapElem\\{family}\\elem{element_id % 1000}_stand.img"
        record = {"elementId": element_id, "className": element["className"], "family": family, "theme": theme,
                  "familyMappingStatus": MAPPING_STATUS, "footprintCells": [element["widthCells"], element["heightCells"]],
                  "gridAttr": element["gridAttr"], "mapElemOffsetRaw": element["imageOffset"],
                  "lifeTime": element["properties"]["LifeTime"], "canMove": element["properties"]["canMove"],
                  "candidatePath": candidate, "usedByMapCount": len(usage[element_id]), "usedByMaps": usage[element_id],
                  "referenceOnly": True, "runtimeOriginalArt": None,
                  "productionStatus": "pending", "geometryAccepted": False}
        if element_id in painted:
            piece = painted[element_id]
            origins = piece["derivedFrom"] if isinstance(piece["derivedFrom"], list) else [piece["derivedFrom"]]
            generation_records = [origin["generationRecord"] for origin in origins if origin.get("generationRecord")]
            record["runtimeOriginalArt"] = {"file": piece["file"], "sha256": piece["sha256"], "generationRecord": generation_records[0], "generationRecords": generation_records, "origins": origins,
                                           "provenanceRecord": piece["provenanceRecord"], "status": piece["status"], "geometryAccepted": piece.get("geometryAccepted", False)}
            record["productionStatus"] = "painted-candidate-awaiting-validation"
        entry = by_path.get(candidate.lower())
        if entry is None:
            record["referenceStatus"] = "missing-candidate-resource"
            records.append(record)
            continue
        record["packageEntry"] = entry
        try:
            raw, compressed_hash = decoder.unpack_resource(package, entry)
            raw_hash = digest(raw)
            dimg_alias = raw_hash in dimg_cache
            if not dimg_alias:
                metadata, frame = decoder.inspect_dimg(raw)
                image, visual_hash, bbox = visible_identity(frame)
                dimg_cache[raw_hash] = (metadata, frame, image, visual_hash, bbox)
            metadata, frame, image, visual_hash, bbox = dimg_cache[raw_hash]
            if visual_hash not in visual_groups:
                retained = existing_pictures.get(visual_hash)
                if retained:
                    png_file, png_hash, native_size = retained["file"], retained["sha256"], retained["nativeFrameSize"]
                else:
                    destination = output / family / "frames" / f"candidate-{element_id}-{visual_hash[:12]}.png"
                    destination.parent.mkdir(parents=True, exist_ok=True)
                    image.save(destination, format="PNG")
                    png_file, png_hash, native_size = relative(destination), digest(destination.read_bytes()), [image.width, image.height]
                visual_groups[visual_hash] = {"id": "visual-" + visual_hash[:16], "visibleContentSha256": visual_hash,
                    "representativeElementId": element_id, "representativeFamily": family,
                    "file": png_file, "sha256": png_hash, "reusedExistingReference": bool(retained),
                    "nativeFrameSize": native_size, "elementIds": [], "families": []}
            visual = visual_groups[visual_hash]
            visual["elementIds"].append(element_id)
            if family not in visual["families"]:
                visual["families"].append(family)
            first_meta = metadata["frames"][frame["index"]]
            record.update({"referenceStatus": "decoded-candidate", "compressedStreamSha256": compressed_hash,
                "dimgSha256": raw_hash, "dimgByteLength": len(raw), "dimgVersion": metadata["version"],
                "dimgFrameCount": metadata["frameCount"], "dimgDirections": metadata["directions"],
                "declaredCanvasRaw": metadata["declaredCanvas"], "declaredCanvasWithinBound": metadata["declaredCanvasWithinBound"],
                "selectedFrame": frame["index"], "selectedFrameSize": [frame["width"], frame["height"]],
                "selectedFrameOffsetRaw": first_meta["frameOffset"], "decodedRgbaSha256": digest(frame["pixels"]),
                "visibleContentSha256": visual_hash, "visibleBoundingBox": bbox, "visualGroupId": visual["id"],
                "referencePng": {"file": visual["file"], "sha256": visual["sha256"], "representativeElementId": visual["representativeElementId"],
                    "nativeFrameSize": visual["nativeFrameSize"], "sameNativeFrameExtent": visual["nativeFrameSize"] == [frame["width"], frame["height"]]},
                "duplicateDimg": dimg_alias, "samePictureAlias": visual["representativeElementId"] != element_id,
                "anchorStatus": "unverified-not-applied", "newModelGeneration": False,
            })
            family_images[family].append((record, image.copy()))
        except Exception as error:
            record["referenceStatus"] = "decode-rejected"
            record["referenceError"] = str(error)
        records.append(record)
    font = ImageFont.load_default(size=13)
    summaries = []
    for group, (family, theme) in GROUPS.items():
        family_records = [record for record in records if record["family"] == family]
        unique = {}
        for record, image in family_images[family]:
            unique.setdefault(record["visibleContentSha256"], (record, image))
        # Bounded representative sheet: first cover distinct footprint/frame-size
        # combinations, then fill by numeric ID. Every omitted frame stays indexed.
        candidates = sorted(unique.values(), key=lambda item: (-(item[0]["footprintCells"][0] * item[0]["footprintCells"][1]), item[0]["elementId"]))
        chosen, signature_seen = [], set()
        for pair in candidates:
            record = pair[0]
            signature = tuple(record["footprintCells"] + record["selectedFrameSize"])
            if signature not in signature_seen and len(chosen) < 24:
                chosen.append(pair);signature_seen.add(signature)
        for pair in candidates:
            if len(chosen) >= 24:
                break
            if pair[0]["elementId"] not in {record["elementId"] for record, image in chosen}:
                chosen.append(pair)
        contact = None
        if chosen:
            columns, cell_width, cell_height = 4, 280, 218
            rows = (len(chosen) + columns - 1) // columns
            sheet = Image.new("RGB", (columns * cell_width, 76 + rows * cell_height), (231, 234, 230))
            draw = ImageDraw.Draw(sheet)
            draw.text((12, 10), f"{family.upper()} - SOURCE REFERENCE ONLY - community patched data, authenticity unverified", fill=(30, 40, 34), font=font)
            draw.text((12, 30), "Candidate ID lookup. Native frames below may be downscaled for inspection; no map anchor applied.", fill=(120, 40, 30), font=font)
            draw.text((12, 50), f"{len(chosen)} representatives / {len(unique)} unique visible pictures / {len(family_records)} element definitions", fill=(50, 60, 50), font=font)
            sheet_items = []
            for number, (record, image) in enumerate(chosen):
                x, y = (number % columns) * cell_width, 76 + (number // columns) * cell_height
                draw.rectangle((x + 3, y + 3, x + cell_width - 3, y + cell_height - 3), fill=(250, 250, 247), outline=(180, 187, 177))
                draw.text((x + 10, y + 8), f"candidate {record['elementId']} | cells {record['footprintCells']}", fill=(20, 30, 24), font=font)
                draw.text((x + 10, y + 27), f"native frame {image.width}x{image.height}", fill=(60, 65, 60), font=font)
                thumb = image.copy();thumb.thumbnail((cell_width - 24, 144), Image.Resampling.LANCZOS)
                sheet.paste(thumb, (x + (cell_width - thumb.width) // 2, y + 50 + (144 - thumb.height) // 2), thumb)
                draw.text((x + 10, y + cell_height - 22), f"ID lookup + render anchor UNVERIFIED", fill=(110, 50, 35), font=font)
                sheet_items.append({"elementId": record["elementId"], "visualGroupId": record["visualGroupId"], "sourceFrameSize": record["selectedFrameSize"], "inspectionThumbnailSize": list(thumb.size), "resizedForInspection": list(thumb.size) != record["selectedFrameSize"]})
            destination = output / family / "contact-sheet.png"
            destination.parent.mkdir(parents=True, exist_ok=True)
            sheet.save(destination)
            contact = {"file": relative(destination), "sha256": digest(destination.read_bytes()), "size": list(sheet.size), "representatives": sheet_items, "notRuntimeArt": True}
        summaries.append({"family": family, "theme": theme, "numericPrefix": group * 1000, "mappingStatus": MAPPING_STATUS,
            "elementCount": len(family_records), "packageStandResourceCount": package_family_counts[family],
            "candidateMatchedCount": sum(record["referenceStatus"] == "decoded-candidate" for record in family_records),
            "uniqueVisiblePictureCount": len(unique), "uniqueDimgCount": len({record.get("dimgSha256") for record in family_records if record.get("dimgSha256")}),
            "footprintCounts": dict(Counter(f"{record['footprintCells'][0]}x{record['footprintCells'][1]}" for record in family_records)),
            "paintedCandidateCount": sum(record["productionStatus"] != "pending" for record in family_records),
            "pendingCount": sum(record["productionStatus"] == "pending" for record in family_records),
            "acceptedCount": 0, "sourceMapFamilyCooccurrence": dict(family_cooccurrence[group]), "contactSheet": contact})
    expected_files = {item["file"] for item in visual_groups.values()}
    removed = list(prior_index.get("removedRedundantReferenceFiles", []))
    for previous in prior_index.get("visualGroups", []):
        path = PROJECT / previous["file"]
        if previous["file"] in expected_files or not path.is_file() or not path.resolve().is_relative_to(output.resolve()):
            continue
        if digest(path.read_bytes()) != previous["sha256"]:
            raise ValueError("Prior task reference changed; refusing cleanup: " + str(path))
        path.unlink()  # Exact task-owned file only; no recursive directory removal.
        removed.append({"file": previous["file"], "sha256": previous["sha256"], "reason": "duplicate-visible-picture-reuses-existing-retained-reference"})
    summary = {"elementCount": len(records), "familyCount": len(summaries), "decodedCandidateCount": sum(record["referenceStatus"] == "decoded-candidate" for record in records),
        "uniqueDimgCount": len(dimg_cache), "uniqueVisiblePictureCount": len(visual_groups),
        "savedReferencePngCount": len(visual_groups), "contactSheetCount": sum(item["contactSheet"] is not None for item in summaries),
        "newFamilyReferencePngCount": sum(not group["reusedExistingReference"] for group in visual_groups.values()),
        "reusedExistingReferencePngCount": sum(group["reusedExistingReference"] for group in visual_groups.values()),
        "samePictureAliasCount": sum(record.get("samePictureAlias", False) for record in records),
        "duplicateDimgAliasCount": sum(record.get("duplicateDimg", False) for record in records),
        "missingCandidateCount": sum(record["referenceStatus"] == "missing-candidate-resource" for record in records),
        "decodeRejectedCount": sum(record["referenceStatus"] == "decode-rejected" for record in records),
        "paintedCandidateCount": len(painted), "pendingCount": sum(record["productionStatus"] == "pending" for record in records), "acceptedCount": 0,
        "paintedCandidateCoveragePercent": round(len(painted) * 100 / len(records), 2), "acceptedCoveragePercent": 0,
        "unknownSourceElementIdCount": len(unknown_map_ids), "unmappedPackageFamilyCount": len(set(package_family_counts) - {item[0] for item in GROUPS.values()})}
    result = {"schemaVersion": 1, "generatedOn": "2026-10-26", "purpose": "production-worklist-and-source-reference-only",
        "source": {"archiveUrl": decoder.ARCHIVE_URL, "archiveSha256": decoder.ARCHIVE_SHA256, "sourceType": "community-patched-client-data",
            "officialOriginalAuthenticity": "unverified", "externalCodeExecuted": False, "inputFiles": input_evidence,
            "elementCatalogSha256": digest((references / "elements.json").read_bytes()), "elementDefinitionSource": elements_doc["source"]},
        "mappingEvidence": {"status": MAPPING_STATUS, "method": "ID thousand-prefix + package subdirectory + exact elem suffix; cross-check full 377-map family cooccurrence. No client lookup table recovered.",
            "unmatchedPackageFamilies": sorted(set(package_family_counts) - {item[0] for item in GROUPS.values()})},
        "deduplication": {"dimg": "SHA256 of decompressed full DIMG resource", "picture": "SHA256 of visible RGBA content+cropped visible dimensions, transparent RGB canonicalized; no representative frame is cropped or rescaled", "geometryAliases": "Every element retains its native frame extent, offsets, footprint and GridAttr even when pixels share a reference PNG"},
        "summary": summary, "originalArtManifestInputs": art_inputs, "families": summaries,
        "elements": records, "visualGroups": list(visual_groups.values()), "removedRedundantReferenceFiles": removed,
        "unknownSourceElementIds": [{"elementId": identity, "maps": names, "status": "definition-missing-not-covered-by-721-inventory"} for identity, names in sorted(unknown_map_ids.items())],
        "limitations": ["Source pixels are reference only and never count as own painted art or runtime completion.", "All family/path/ID links remain candidate until client lookup proof.", "Town existing pieces are original AI-painted candidates; source lookup, anchors, geometry and in-game acceptance remain false.", "Only first visible stand frames were decoded; animation, death, trigger and effect production remain separate and pending.", "Contact sheets show at most 24 unique pictures per family, with explicitly labelled inspection downscaling.", "Logical size and offsets are retained data; no inferred anchor or source pixel composition is made."]}
    write_json(output / "index.json", result)
    write_json(PROJECT / "assets/maps/production-index.json", result)
    write_document(result)
    print(json.dumps(summary, ensure_ascii=True))


def write_document(result):
    total = result["summary"]
    lines = ["# 地图原创美术生产库存", "", "核对日期：2026-10-26。范围为已静态提取的721条地图元素定义；不等同于全部原版资源。以 `USER_REQUIREMENTS_LOCK_20261026.md` 的同坐标、同占地要求为准。", "",
        "## 当前覆盖", "", f"- 元素 **{total['elementCount']}** 条，候选family **{total['familyCount']}** 组；stand候选成功解码 **{total['decodedCandidateCount']}** 条。",
        f"- 去重后 **{total['uniqueDimgCount']}** 个DIMG、**{total['uniqueVisiblePictureCount']}** 幅可见画面；引用 **{total['savedReferencePngCount']}** 张原生首个非空帧PNG（本轮family目录新增 **{total['newFamilyReferencePngCount']}** 张、复用已留存town参考 **{total['reusedExistingReferencePngCount']}** 张），另有 **{total['contactSheetCount']}** 张有限代表联系表。",
        f"- 原创已画候选 **{total['paintedCandidateCount']}** 条（{total['paintedCandidateCoveragePercent']}%），待制作 **{total['pendingCount']}** 条；**正式几何/锚点/游戏验收通过0条，验收覆盖0%**。",
        f"- 原图参考不计原创完成；同画面别名 **{total['samePictureAliasCount']}** 条单列，不能把重复源图计为多次原创制作。", "",
        "`assets/maps/production-index.json` 是完整721条逐项生产清单，含每条family/theme/size/GridAttr、使用地图、候选资源路径、原生帧尺寸、哈希、去重组、原创稿路径及待验收状态。`references/qqtang-map-data/visual-reference/families/index.json` 是同批取证索引；其中参考PNG仅供结构核对，不进入运行资源。", "",
        "## 按family/theme与占地的清单", "", "| 候选family / 主题 | 元素 | 占地分布（格） | 对应stand / 包内stand | 不同画面 | 原创候选 / 待作 | 代表联系表 |", "|---|---:|---|---:|---:|---:|---|"]
    for family in result["families"]:
        footprints = "、".join(f"{size}×{count}" for size, count in sorted(family["footprintCounts"].items()))
        contact = family["contactSheet"]
        link = f"[查看]({('../' + contact['file']) if contact else ''})" if contact else "无"
        lines.append(f"| `{family['family']}` / {family['theme']} | {family['elementCount']} | {footprints} | {family['candidateMatchedCount']} / {family['packageStandResourceCount']} | {family['uniqueVisiblePictureCount']} | {family['paintedCandidateCount']} / {family['pendingCount']} | {link} |")
    lines += ["", "占地分布中的`2x1×3`表示定义占地2×1格的元素有3条，不是输出图像尺寸。包内stand数量可能大于721条所用范围；未关联的额外文件未批量导出。", "",
        "## 现有原创稿与后续批次", "", "town已存在的手绘切片仅标记为`painted-candidate-awaiting-validation`，不是原版几何或同坐标验收完成。当前依据art.json实际存在、哈希匹配且具有生成记录的文件计数；A/B源母图和切片不重复累计。", "",
        "| 元素ID | 原创候选文件 | 状态 |", "|---|---|---|"]
    for record in result["elements"]:
        if record["runtimeOriginalArt"]:
            art = record["runtimeOriginalArt"]
            lines.append(f"| {record['elementId']} | [{Path(art['file']).name}](../{art['file']}) | 已画候选，几何/锚点/游戏验收未通过 |")
    lines += ["", "已画之外全部维持pending。水岸合成稿分别记录新AI纹理与原图区域mask来源，不重复计为模型新生图；其接缝与视觉锚点仍未通过。不能以已计划、已提交提示词或源参考解码替代完成回执。后续重跑此脚本按现存art.json与哈希刷新，不自动认定通过。", "",
        "## 来源、候选映射与去重", "",
        f"- 社区发行ZIP：[{decoder.ARCHIVE_URL}]({decoder.ARCHIVE_URL})，SHA256 `{decoder.ARCHIVE_SHA256}`；腾讯原始版本身份未核实。",
        "- 只静态读取object.idx/pkg，并使用本项目独立的`inspect-reference-dimg.py`解包/解码；输入字节数、哈希均与社区release-manifest核对。没有执行被检查的Python、客户端或其他二进制。",
        "- ID千位组与包内family/elem编号采用全后缀匹配及377张地图的family共现核对，但尚无客户端ID查找表证明，全部标candidate。主题中文仅为生产分类描述。",
        "- 对全DIMG做SHA256去重，再对可见RGBA画面做去重；透明像素RGB与透明留边不制造新画面。每个ID仍保留自身frame尺寸、offset、size与GridAttr；画面别名不代表几何可互换。",
        "- 原生PNG保存某一代表的完整首个非空帧，不裁切、不缩放。每family最多24个不同画面做联系表；联系表可能缩小，仅供检查，实际缩放记录逐项列出。未选代表仍可从完整索引定位原生帧。", "",
        "## 缺口与验收门槛", "",
        f"- 另有 **{total['unknownSourceElementIdCount']}** 个正元素ID出现在地图中但不属于这721条定义；在JSON的unknownSourceElementIds列其地图，保持缺失，不猜资源。",
        "- 包内tank目录尚无本批721定义对应组，未盲目导出其图片；不能把它漏记成制作完成。",
        "- 首帧不覆盖行走/触发/死亡/破坏动画，完整状态制作仍待单独合同。",
        "- 每条正式原创资源必须保留实际生成来源记录，核对候选IDlookup、原生frame尺寸/偏移、建筑占地/通路/遮挡与像素锚点，并完成游戏内等比例截图验收后才能从候选升为accepted。", "",
        "## 重建", "", "使用带Pillow的本机Python执行：", "", "```text", "python -B scripts/build-map-art-inventory.py", "```", "", "脚本只更新本任务库存/参考输出与生产索引，不修改地图数据、运行贴图、UI或Git。"]
    (PROJECT / "docs/MAP_ART_PRODUCTION_INVENTORY.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
