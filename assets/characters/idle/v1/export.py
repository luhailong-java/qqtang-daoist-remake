from pathlib import Path
import hashlib
import json

from PIL import Image

OUTPUT = Path(__file__).resolve().parent
PROJECT = OUTPUT.parents[3]
SOURCE_DIR = PROJECT / "assets/characters/motion-generated"
LOTUS_SEAMS = OUTPUT / "lotus-seams.json"
PUBLIC_SOURCE_COMMIT = "fd4b93b3a327700d03c1d73085cfe73d4452727d"
SOURCES = (
    ("maomao", "daoist-child", (570, 990, 1548),
     "91547825c91fa005627b7d480d9c9b605b68478a", "03bb2c6ba2d2da9ffb6bbe350e75b53932a3f650"),
    ("asha", "moon-shadow", (550, 1013, 1581),
     "7ccc25450abaef843ea01544edf6119fce361545", "937c38e4b3a0a1e663d7f89e65ca947139476515"),
    ("wukong", "mountain-guardian", (524, 1001, 1580),
     "077fe0f4a87c1ff6790cd897ee57c8ae36a88a62", "f371e846adacc4a657ca3dfd3a269a8ad6e6df5d"),
    ("titan", "lotus-healer", (560, 1004, 1570),
     "4957fc363de206220fe5fa7afa29447cdb932266", "7f1af5dcaafcb0fa3a9a8c301fecbe9c3e743a83"),
)
NATIVE_SIZE = (2048, 768)
WORKING_SIZE = (896, 896)
WORKING_ROOT = (448, 812)
OUTPUT_SIZE = (256, 256)
OUTPUT_ROOT = (128, 232)
THUMBNAIL_PX = 138
CONTACT_CELL = 144


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def git_blob(data):
    return hashlib.sha1(f"blob {len(data)}\0".encode("ascii") + data).hexdigest()


def relative(path):
    return path.relative_to(PROJECT).as_posix()


def alpha_bounds(alpha, threshold):
    return alpha.point(lambda value: 255 if value > threshold else 0).getbbox()


def source_boundaries(alpha, identity, cuts):
    boundaries = [[cut] * alpha.height for cut in cuts]
    alpha_limits = [2] * len(cuts)
    if identity == "lotus-healer":
        seam_contract = json.loads(LOTUS_SEAMS.read_text(encoding="utf-8"))
        if seam_contract["source"] != relative(SOURCE_DIR / identity / "idle-four-directions-v1.png"):
            raise ValueError("Lotus seam contract points at a different source")
        for index, seam in enumerate(seam_contract["paths"]):
            boundaries[index] = [x for x, rows in seam["xAndRowCounts"] for _ in range(rows)]
            alpha_limits[index] = seam["maxAlpha"]
    if any(len(boundary) != alpha.height for boundary in boundaries):
        raise ValueError(f"Seam does not cover every source row for {identity}")
    spans = [[0] * alpha.height, *boundaries, [alpha.width] * alpha.height]
    if any(tuple(row) != tuple(sorted(set(row))) for row in zip(*spans)):
        raise ValueError(f"Crossed seams for {identity}")

    maxima = []
    for boundary, limit in zip(boundaries, alpha_limits):
        previous_x = boundary[0]
        maximum = 0
        for y, x in enumerate(boundary):
            # Include the neighboring pixels on both sides of each stair step.
            rect = (min(x, previous_x) - 1, max(0, y - 1), max(x, previous_x) + 1, y + 1)
            maximum = max(maximum, alpha.crop(rect).getextrema()[1])
            previous_x = x
        if maximum > limit or limit > 9:
            raise ValueError(f"Source boundary cuts visible art for {identity}: alpha {maximum}")
        maxima.append(maximum)
    return spans, maxima


def extract_pose(source, left, right):
    x0 = min(left)
    cell = Image.new("RGBA", (max(right) - x0, source.height))
    for y, (x1, x2) in enumerate(zip(left, right)):
        cell.paste(source.crop((x1, y, x2, y + 1)), (x1 - x0, y))
    alpha = cell.getchannel("A")
    trim_rect = alpha_bounds(alpha, 2)
    solid_rect = alpha_bounds(alpha, 128)
    if trim_rect is None or solid_rect is None:
        raise ValueError("Source pose is empty")
    baseline = solid_rect[3]
    sole_band = (0, baseline - 26, cell.width, baseline)
    soles = alpha_bounds(alpha.crop(sole_band), 128)
    center_x = round((soles[0] + soles[2]) / 2)
    left_on_canvas = WORKING_ROOT[0] + trim_rect[0] - center_x
    top_on_canvas = WORKING_ROOT[1] + trim_rect[1] - baseline
    trim = cell.crop(trim_rect)
    if (left_on_canvas < 0 or top_on_canvas < 0
            or left_on_canvas + trim.width > WORKING_SIZE[0]
            or top_on_canvas + trim.height > WORKING_SIZE[1]):
        raise ValueError("Source pose exceeds the fixed registration canvas")
    canvas = Image.new("RGBA", WORKING_SIZE)
    canvas.paste(trim, (left_on_canvas, top_on_canvas))
    frame = canvas.convert("RGBa").resize(OUTPUT_SIZE, Image.Resampling.LANCZOS).convert("RGBA")
    crop_rect = (trim_rect[0] + x0, trim_rect[1], trim_rect[2] + x0, trim_rect[3])
    return frame, crop_rect, (center_x + x0, baseline), (left_on_canvas, top_on_canvas)


def save_verified(frame, path):
    frame.save(path, optimize=True)
    with Image.open(path) as exported:
        exported.load()
        if exported.format != "PNG" or exported.mode != "RGBA" or exported.size != OUTPUT_SIZE:
            raise ValueError(f"Invalid output encoding: {path.name}")
        alpha = exported.getchannel("A")
        visible = alpha_bounds(alpha, 8)
        if visible is None or alpha.getextrema() != (0, 255):
            raise ValueError(f"Invalid output alpha: {path.name}")
        if min(*visible[:2], OUTPUT_SIZE[0] - visible[2], OUTPUT_SIZE[1] - visible[3]) < 12:
            raise ValueError(f"Paint approaches an output edge: {path.name}")
    return visible


def main():
    contact = Image.new("RGB", (8 * CONTACT_CELL, 4 * CONTACT_CELL), "#f4ecd7")
    contact.paste("#203a38", (4 * CONTACT_CELL, 0, contact.width, contact.height))
    sources = []
    frames = []
    for row, (character_id, identity, cuts, expected_blob, expected_record_blob) in enumerate(SOURCES):
        path = SOURCE_DIR / identity / "idle-four-directions-v1.png"
        record_path = path.with_suffix(".png.generation.json")
        source_bytes = path.read_bytes()
        record_bytes = record_path.read_bytes()
        record = json.loads(record_bytes)
        source_hash = hashlib.sha256(source_bytes).hexdigest()
        if source_hash != record["sha256"]:
            raise ValueError(f"Source hash mismatch for {identity}")
        if git_blob(source_bytes) != expected_blob or git_blob(record_bytes) != expected_record_blob:
            raise ValueError(f"Source or record differs from the published source for {identity}")

        with Image.open(path) as source:
            if source.format != "PNG" or source.mode != "RGBA" or source.size != NATIVE_SIZE:
                raise ValueError(f"Invalid native source encoding for {identity}")
            spans, maxima = source_boundaries(source.getchannel("A"), identity, cuts)
            sources.append({
                "identity": identity,
                "file": relative(path),
                "sha256": source_hash,
                "publicGitBlobSha1": expected_blob,
                "size": NATIVE_SIZE,
                "generationRecord": relative(record_path),
                "generationRecordSha256": hashlib.sha256(record_bytes).hexdigest(),
                "publicGenerationRecordGitBlobSha1": expected_record_blob,
                "nominalCutX": cuts,
                "seamAlphaMax": maxima,
                "variableSeams": relative(LOTUS_SEAMS) if identity == "lotus-healer" else None,
            })
            for column, (direction, left, right) in enumerate(zip("NESW", spans, spans[1:])):
                frame, crop_rect, root, placement = extract_pose(source, left, right)
                output_path = OUTPUT / f"{identity}-{direction}.png"
                visible = save_verified(frame, output_path)
                frames.append({
                    "characterId": character_id,
                    "identity": identity,
                    "direction": direction,
                    "file": relative(output_path),
                    "sha256": digest(output_path),
                    "width": OUTPUT_SIZE[0],
                    "height": OUTPUT_SIZE[1],
                    "anchor": OUTPUT_ROOT,
                    "sourceCropRect": crop_rect,
                    "sourceSoleAnchor": root,
                    "placementOn896Canvas": placement,
                    "visibleBoundsAlphaAbove8": visible,
                    "alphaExtrema": [0, 255],
                })
                thumb = (frame.convert("RGBa")
                         .resize((THUMBNAIL_PX, THUMBNAIL_PX), Image.Resampling.LANCZOS)
                         .convert("RGBA"))
                for index in (column, column + 4):
                    contact.paste(thumb, (index * CONTACT_CELL + 3, row * CONTACT_CELL + 3), thumb)

    if len({frame["sha256"] for frame in frames}) != 16:
        raise ValueError("Expected sixteen distinct directional stills")
    contact_path = OUTPUT / "contact.png"
    contact.save(contact_path, optimize=True)
    manifest = {
        "schemaVersion": 1,
        "state": "idle",
        "format": "RGBA PNG",
        "kind": "directional-static-actor-candidate",
        "publicSourceCommit": PUBLIC_SOURCE_COMMIT,
        "directions": ["N", "E", "S", "W"],
        "directionEvidence": "Visually checked: rear view, nose toward screen-right, front view, nose toward screen-left.",
        "sources": sources,
        "operation": {
            "type": "deterministic-source-ownership-crop-sole-registration-uniform-resample",
            "trimBoundsAlphaThreshold": 2,
            "soleBoundsAlphaThreshold": 128,
            "soleBandHeight": 26,
            "workingCanvas": WORKING_SIZE,
            "workingAnchor": WORKING_ROOT,
            "resampler": "premultiplied-alpha LANCZOS",
            "scale": OUTPUT_SIZE[0] / WORKING_SIZE[0],
            "newModelGeneration": False,
        },
        "placementCandidate": {
            "displaySizeIn64UnitActorSpace": [110, 110],
            "rootWithinActorCellIn64UnitSpace": [32, 59],
        },
        "frames": frames,
        "contactSheet": {
            "file": relative(contact_path),
            "sha256": digest(contact_path),
            "displayPx": THUMBNAIL_PX,
            "columnDirections": ["N", "E", "S", "W", "N", "E", "S", "W"],
        },
        "clientApproved": False,
        "userAccepted": False,
    }
    (OUTPUT / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(f"Verified and exported {len(frames)} distinct directional RGBA stills")


if __name__ == "__main__":
    main()
