from pathlib import Path
import hashlib
import json

from PIL import Image

OUTPUT = Path(__file__).resolve().parent
PROJECT = OUTPUT.parents[3]
SOURCE = PROJECT / "assets/characters/motion-generated/trapped-four-v2.png"
RECORD = SOURCE.with_suffix(".png.generation.json")
SOURCE_SHA256 = "9d788373f7f2dd257a4654ad4cd2b17d7c6326acab7b098e52a8d4abfc0cb326"
POSES = (
    ("maomao", "daoist-child", (0, 0, 768, 500)),
    ("asha", "moon-shadow", (768, 0, 1536, 500)),
    ("wukong", "mountain-guardian", (0, 500, 768, 1024)),
    ("titan", "lotus-healer", (768, 500, 1536, 1024)),
)


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def relative(path):
    return path.relative_to(PROJECT).as_posix()


def main():
    source_record = json.loads(RECORD.read_text(encoding="utf-8"))
    if digest(SOURCE) != SOURCE_SHA256 or source_record["sha256"] != SOURCE_SHA256:
        raise ValueError("Trapped-state source does not match the recorded SHA256")
    with Image.open(SOURCE) as source:
        if source.format != "PNG" or source.mode != "RGBA" or source.size != (1536, 1024):
            raise ValueError("Expected the native 1536×1024 RGBA source")
        alpha = source.getchannel("A")
        cuts = [(766, 0, 770, 1024), (0, 498, 1536, 502)]
        cut_alpha_max = [alpha.crop(cut).getextrema()[1] for cut in cuts]
        if max(cut_alpha_max) > 1:
            raise ValueError("A source seam intersects visible paint")

        contact = Image.new("RGB", (432, 216))
        for row, background in enumerate(("#f4ecd7", "#203a38")):
            contact.paste(background, (0, row * 108, contact.width, (row + 1) * 108))

        frames = []
        for index, (character_id, identity, cell_rect) in enumerate(POSES):
            cell = source.crop(cell_rect)
            alpha = cell.getchannel("A")
            trim_rect = alpha.point(lambda value: 255 if value > 1 else 0).getbbox()
            rim_rect = alpha.point(lambda value: 255 if value > 8 else 0).getbbox()
            if trim_rect is None or rim_rect is None:
                raise ValueError(f"Empty source cell for {identity}")
            trim = cell.crop(trim_rect)
            rim_center = ((rim_rect[0] + rim_rect[2]) / 2, (rim_rect[1] + rim_rect[3]) / 2)
            left = round(256 + trim_rect[0] - rim_center[0])
            top = round(256 + trim_rect[1] - rim_center[1])
            if left < 0 or top < 0 or left + trim.width > 512 or top + trim.height > 512:
                raise ValueError(f"Source art exceeds the common canvas for {identity}")

            canvas = Image.new("RGBA", (512, 512))
            canvas.paste(trim, (left, top))
            image = canvas.convert("RGBa").resize((256, 256), Image.Resampling.LANCZOS).convert("RGBA")
            path = OUTPUT / f"{identity}.png"
            image.save(path, optimize=True)
            with Image.open(path) as output:
                output.load()
                if output.size != (256, 256) or output.mode != "RGBA":
                    raise ValueError(f"Bad export size or mode for {identity}")
                output_alpha = output.getchannel("A")
                visible_bounds = output_alpha.point(lambda value: 255 if value > 8 else 0).getbbox()
                alpha_extrema = output_alpha.getextrema()
                if visible_bounds is None or alpha_extrema[0] != 0 or alpha_extrema[1] < 250:
                    raise ValueError(f"Bad export alpha for {identity}")
                if min(*visible_bounds[:2], 256 - visible_bounds[2], 256 - visible_bounds[3]) < 12:
                    raise ValueError(f"Paint approaches output edge for {identity}")

            thumb = image.convert("RGBa").resize((96, 96), Image.Resampling.LANCZOS).convert("RGBA")
            for row in range(2):
                contact.paste(thumb, (index * 108 + 6, row * 108 + 6), thumb)
            frames.append({
                "characterId": character_id,
                "identity": identity,
                "file": relative(path),
                "sha256": digest(path),
                "width": 256,
                "height": 256,
                "anchor": [128, 128],
                "sourceCellRect": cell_rect,
                "sourceCropRect": [
                    cell_rect[0] + trim_rect[0], cell_rect[1] + trim_rect[1],
                    cell_rect[0] + trim_rect[2], cell_rect[1] + trim_rect[3],
                ],
                "sourceRimCenterInCell": rim_center,
                "placementOn512Canvas": [left, top],
                "visibleBoundsAlphaAbove8": visible_bounds,
                "alphaExtrema": alpha_extrema,
            })

    if len({frame["sha256"] for frame in frames}) != 4:
        raise ValueError("Expected four distinct exports")
    contact_path = OUTPUT / "contact.png"
    contact.save(contact_path, optimize=True)
    manifest = {
        "schemaVersion": 1,
        "state": "trapped",
        "format": "RGBA PNG",
        "kind": "static-character-and-shell-candidate",
        "source": {
            "file": relative(SOURCE),
            "sha256": SOURCE_SHA256,
            "size": [1536, 1024],
            "generationRecord": relative(RECORD),
            "generationRecordSha256": digest(RECORD),
            "seamBands": cuts,
            "seamBandAlphaMax": cut_alpha_max,
        },
        "operation": {
            "type": "deterministic-crop-center-uniform-resample",
            "trimBoundsAlphaThreshold": 1,
            "centeringAlphaThreshold": 8,
            "workingCanvas": [512, 512],
            "resampler": "premultiplied-alpha LANCZOS",
            "scale": 0.5,
            "newModelGeneration": False,
        },
        "placementCandidate": {
            "displaySizeIn64UnitActorSpace": [76, 76],
            "centerWithinActorCellIn64UnitSpace": [32, 26],
        },
        "frames": frames,
        "contactSheet": {"file": relative(contact_path), "sha256": digest(contact_path), "displayPx": 96},
        "clientApproved": False,
        "userAccepted": False,
    }
    (OUTPUT / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(f"Verified and exported {len(frames)} distinct RGBA state sprites")


if __name__ == "__main__":
    main()
