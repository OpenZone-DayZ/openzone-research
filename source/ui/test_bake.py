"""Tests of the pure parts of bake.py: the colour bleed, the gutter, the packer, the manifest rules
and the ids. They need neither Chrome nor Node nor DayZ Tools.

    python -m unittest discover -s source/ui -v
"""
import tempfile
import unittest
from pathlib import Path

from PIL import Image

import bake

RED = (255, 0, 0, 255)
CLEAR = (0, 0, 0, 0)


def image(w, h, red_pixels):
    img = Image.new("RGBA", (w, h), CLEAR)
    for xy in red_pixels:
        img.putpixel(xy, RED)
    return img


def coloured(img, where):
    """The pixels of `img` for which `where(x, y)` holds and that have a colour (RGB is not 0,0,0)."""
    return [(x, y) for x in range(img.width) for y in range(img.height)
            if where(x, y) and img.getpixel((x, y))[:3] != (0, 0, 0)]


class Bleed(unittest.TestCase):
    def test_colour_spreads_exactly_radius_pixels_and_alpha_is_untouched(self):
        out = bake.bleed(image(14, 5, [(0, y) for y in range(5)]), 4)
        self.assertEqual(out.getpixel((0, 2)), RED)
        for x in range(1, 5):
            self.assertEqual(out.getpixel((x, 2)), (255, 0, 0, 0))
        for x in range(5, 14):
            self.assertEqual(out.getpixel((x, 2)), CLEAR)

    def test_colour_does_not_wrap_round_the_edge(self):
        # A red column at x=0 of a 14x5 image used to turn x=12 and 13 red: offset() wraps, the
        # margin was 1 px, and the loop ran 4 steps.
        out = bake.bleed(image(14, 5, [(0, y) for y in range(5)]), 4)
        self.assertEqual(coloured(out, lambda x, y: x > 4), [])
        out = bake.bleed(image(5, 14, [(x, 0) for x in range(5)]), 4)
        self.assertEqual(coloured(out, lambda x, y: y > 4), [])
        out = bake.bleed(image(14, 14, [(0, 0)]), 4)
        self.assertEqual(coloured(out, lambda x, y: max(x, y) > 4), [])
        out = bake.bleed(image(14, 14, [(13, 13)]), 4)
        self.assertEqual(coloured(out, lambda x, y: x < 9 or y < 9), [])

    def test_opaque_and_empty_images_come_back_as_they_are(self):
        opaque = Image.new("RGBA", (6, 6), RED)
        self.assertIs(bake.bleed(opaque, 4), opaque)
        empty = Image.new("RGBA", (6, 6), CLEAR)
        self.assertIs(bake.bleed(empty, 4), empty)


class Gutter(unittest.TestCase):
    def test_gutter_repeats_the_edge_pixels(self):
        img = Image.new("RGBA", (3, 2))
        for i, xy in enumerate([(0, 0), (1, 0), (2, 0), (0, 1), (1, 1), (2, 1)]):
            img.putpixel(xy, (10 * i, 20, 30, 255 - i))
        cell = bake.extend_edges(img, 2)
        self.assertEqual(cell.size, (7, 6))
        for y in range(6):
            for x in range(7):
                self.assertEqual(cell.getpixel((x, y)), img.getpixel((min(max(x - 2, 0), 2), min(max(y - 2, 0), 1))))


class Pack(unittest.TestCase):
    SIZES = [(44, 44)] * 5 + [(23, 23)] * 2 + [(32, 32), (296, 98), (296, 98), (130, 60)]

    def test_cells_are_disjoint_inside_a_power_of_two_atlas(self):
        (w, h), spots = bake.pack(self.SIZES, 2048)
        self.assertTrue(w & (w - 1) == 0 and h & (h - 1) == 0)
        boxes = [(x, y, x + sw, y + sh) for (x, y), (sw, sh) in zip(spots, self.SIZES)]
        for x0, y0, x1, y1 in boxes:
            self.assertTrue(x0 >= 0 and y0 >= 0 and x1 <= w and y1 <= h)
        for i, a in enumerate(boxes):
            for b in boxes[:i]:
                self.assertTrue(a[2] <= b[0] or b[2] <= a[0] or a[3] <= b[1] or b[3] <= a[1])

    def test_the_same_sizes_give_the_same_atlas(self):
        self.assertEqual(bake.pack(self.SIZES, 2048), bake.pack(list(self.SIZES), 2048))

    def test_more_than_atlas_max_holds_is_refused(self):
        with self.assertRaises(bake.BakeError):
            bake.pack([(300, 300)] * 3, 256)


class Manifest(unittest.TestCase):
    def test_a_css_entry_is_text_with_a_brace_a_semicolon_or_a_line_break_else_a_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp)
            (folder / "a.css").write_text("b { c: d }", encoding="utf-8")
            self.assertEqual(bake._css(["a.css", "x { y: z }", "color: red;", "a\nb"], folder, "css"),
                             "b { c: d }\nx { y: z }\ncolor: red;\na\nb")
            with self.assertRaisesRegex(bake.BakeError, "has no '{', ';' or line break"):
                bake._css("missing.css", folder, "css")

    def test_language_variants_make_two_sprites(self):
        items = bake._items([{"name": "stamp", "w": 10, "h": 5, "html_uk": "a", "html_en": "b"}], "sprite")
        self.assertEqual([(i.name, i.html) for i in items], [("stamp_uk", "a"), ("stamp_en", "b")])
        with self.assertRaises(bake.BakeError):
            bake._items([{"name": "stamp", "w": 10, "h": 5, "html_uk": "a"}], "sprite")


class Ids(unittest.TestCase):
    @staticmethod
    def item(name, html):
        return bake.Item(name, 10, 10, html)

    def test_an_id_used_by_two_pictures_is_refused(self):
        a = self.item("a", "<svg><linearGradient id='g'/></svg>")
        b = self.item("b", '<svg><rect fill="url(#g)"/><linearGradient ID = "g"/></svg>')
        with self.assertRaisesRegex(bake.BakeError, "'g' is used in a and in b"):
            bake.check_ids([a, b])

    def test_prefixed_ids_are_fine_and_so_are_attributes_that_only_end_in_id(self):
        bake.check_ids([self.item("a", "<i id='a_g' data-id='g'></i>"), self.item("b", "<i id='b_g' grid='g'></i>")])

    def test_the_ids_of_the_bake_are_refused(self):
        for ident in ("oz0", "oz17", "oz-sheet", "oz-canary"):
            with self.assertRaises(bake.BakeError):
                bake.check_ids([self.item("a", f"<i id='{ident}'></i>")])


if __name__ == "__main__":
    unittest.main()
