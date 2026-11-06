"""Keep the water floor opaque and matched at its source-size tile boundaries."""

import hashlib
import json
from pathlib import Path
import unittest

from PIL import Image


ROOT = Path(__file__).resolve().parents[1]


class WaterGroundPair(unittest.TestCase):
    def test_selected_tiles_preserve_geometry_and_match_every_edge_pair(self):
        path = ROOT / "assets/maps/water/art.json"
        manifest = json.loads(path.read_text(encoding="utf-8"))
        tiles = {}
        for item in manifest["pieces"]:
            if item["elementId"] not in (5001, 5019):
                continue
            with self.subTest(element=item["elementId"]):
                tile_file = ROOT / item["file"]
                self.assertEqual(hashlib.sha256(tile_file.read_bytes()).hexdigest(), item["sha256"])
                self.assertEqual([item["worldFrameWidth"], item["worldFrameHeight"]], [40, 40])
                self.assertEqual(item["footprintCells"], [1, 1])
                self.assertEqual(item["sourceMapElemOffsetRaw"], [0, 0])
                self.assertEqual(item["sourceGridAttr"], [3855])
                with Image.open(tile_file) as tile:
                    self.assertEqual((tile.mode, tile.size), ("RGBA", (160, 160)))
                    self.assertEqual(tile.getchannel("A").getextrema(), (255, 255))
                    tiles[item["elementId"]] = tile.copy()
        self.assertEqual(set(tiles), {5001, 5019})
        for first in tiles.values():
            for second in tiles.values():
                self.assertEqual(first.crop((159, 0, 160, 160)).tobytes(),
                                 second.crop((0, 0, 1, 160)).tobytes())
                self.assertEqual(first.crop((0, 159, 160, 160)).tobytes(),
                                 second.crop((0, 0, 160, 1)).tobytes())


if __name__ == "__main__":
    unittest.main()
