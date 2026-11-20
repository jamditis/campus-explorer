"""Draw the paint textures for the scripted build: lane lines, stalls, crosswalks and the football
field.

Markings are paint, never geometry: every painted surface gets one or more texture sheets (layout.py
decides which and where), drawn here from the plan's markings and nothing else. No aerial or
photo pixels are used.

usage: python3 blender/scripted/paint.py DATA_DIR [--areas NAME,NAME]     (system Python, Pillow)
Writes DATA_DIR/authored/authored_<area>_<surface>_<n>.png for every area (p<surface number>, or
d<building part number> for the paint on a deck's roof level). DATA_DIR must be outside the
repository.
"""

import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import geom  # noqa: E402
import layout  # noqa: E402

SS = 2  # supersampling
# sRGB. Asphalt and turf tones are what the viewer shows after its own texture is multiplied in.
BASE = {
    "asphalt": (121, 121, 119),
    "turf": (38, 94, 50),
    "concrete": (177, 175, 169),
    "brick": (150, 84, 66),
    "lawn": (74, 112, 52),  # painted lawn is a mown ball field
    "gravel": (176, 138, 104),  # painted gravel is an infield skin: clay
}
PAINT = {
    "white": (238, 238, 232),
    "yellow": (232, 186, 40),
    "red": (172, 30, 38),
    "blue": (40, 80, 170),
}
YD, FT = 0.9144, 0.3048
ROOF = "#8f9194"  # a flat roof's colour when the part gives none (building.py, `roof_colour`)


class Sheet:
    """One texture sheet: maps model metres to pixels and draws paint primitives."""

    def __init__(self, sheet, kind, base=None):
        self.s = sheet
        self.k = sheet["w"] / (sheet["u1"] - sheet["u0"]) * SS
        self.to_local = geom.frame((0.0, 0.0), sheet["angle"])[0]
        self.im = Image.new(
            "RGB", (sheet["w"] * SS, sheet["h"] * SS), base or BASE.get(kind, (128, 128, 128))
        )
        self.dr = ImageDraw.Draw(self.im)

    def px(self, p):
        u, v = self.to_local(p[0], p[1])
        return ((u - self.s["u0"]) * self.k, (self.s["v1"] - v) * self.k)

    def visible(self, pts):
        xs, ys = zip(*pts, strict=True)
        return (
            max(xs) >= 0 and min(xs) <= self.im.width and max(ys) >= 0 and min(ys) <= self.im.height
        )

    def line(self, line, width, colour):
        pts = [self.px(p) for p in line]
        if self.visible(pts):
            self.dr.line(
                pts,
                fill=PAINT.get(colour, colour),
                width=max(1, round(width * self.k)),
                joint="curve",
            )

    def area(self, ring, colour):
        pts = [self.px(p) for p in ring]
        if self.visible(pts):
            self.dr.polygon(pts, fill=PAINT.get(colour, colour))

    def text(self, text, centre, right_angle, height, width, colour, outline=None):
        """Letters `height` m tall over `width` m, centred at `centre`, reading toward `right_angle`
        (deg from east).
        """
        c = self.px(centre)
        if not (-2000 < c[0] < self.im.width + 2000 and -2000 < c[1] < self.im.height + 2000):
            return
        font = ImageFont.load_default(size=200)
        box = font.getbbox(text)
        pad = 24
        tile = Image.new("L", (box[2] - box[0] + 2 * pad, box[3] - box[1] + 2 * pad), 0)
        ImageDraw.Draw(tile).text((pad - box[0], pad - box[1]), text, fill=255, font=font)
        edge = None
        if outline:
            edge = Image.new("L", tile.size, 0)
            ImageDraw.Draw(edge).text(
                (pad - box[0], pad - box[1]), text, fill=255, font=font, stroke_width=14
            )
        sx = width * self.k / (box[2] - box[0])
        sy = height * self.k / (box[3] - box[1])
        size = (max(1, round(tile.width * sx)), max(1, round(tile.height * sy)))
        rot = right_angle - self.s["angle"]
        for mask, col in ((edge, outline), (tile, colour)):
            if mask is None:
                continue
            m = mask.resize(size, Image.LANCZOS).rotate(rot, expand=True, resample=Image.BICUBIC)
            self.im.paste(
                PAINT.get(col, col), (round(c[0] - m.width / 2), round(c[1] - m.height / 2)), m
            )

    def save(self, folder):
        out = self.im.resize((self.s["w"], self.s["h"]), Image.LANCZOS)
        out.save(Path(folder) / f"{self.s['name']}.png")
        return out.size


def football_extras(sheet, ff):
    """Numerals and the lettering seen in the May 2025 drone photographs. Typeface and letter sizes
    UNVERIFIED.
    """
    to_model = geom.frame(ff["centre"], ff["angle"])[1]
    ang = ff["angle"]
    half_w = 80 * FT
    # numerals: 6 ft tall, 4 ft wide each, tops 9 yd in from the sideline, read from the nearer
    # sideline (NCAA)
    for i, n in zip(range(-4, 5), (10, 20, 30, 40, 50, 40, 30, 20, 10), strict=True):
        u = i * 10 * YD
        tens, units = str(n)
        for side, facing in ((1, ang + 180), (-1, ang)):
            v = side * (half_w - 9 * YD - 3 * FT)
            first, second = (units, tens) if side > 0 else (tens, units)  # as laid out along +u
            sheet.text(first, to_model(u - 3.2 * FT, v), facing, 6 * FT, 4 * FT, "white")
            sheet.text(second, to_model(u + 3.2 * FT, v), facing, 6 * FT, 4 * FT, "white")
    # white team-area bands outside both sidelines between the 25 yd lines (extent read from the
    # photo: UNVERIFIED)
    for side in (-1, 1):
        a, b = side * (half_w + 6 * FT), side * (half_w + 12 * FT)
        sheet.area(
            [
                to_model(-25 * YD, a),
                to_model(25 * YD, a),
                to_model(25 * YD, b),
                to_model(-25 * YD, b),
            ],
            "white",
        )
    # end lettering: +u end and -u end; the southern end carries RED HAWKS, the northern apron
    # MONTCLAIR STATE
    south = 1 if to_model(1, 0)[1] < to_model(0, 0)[1] else -1
    hl = 60 * YD
    sheet.text(
        "RED HAWKS", to_model(south * (hl + 6.5), 0), ang - 90 * south, 3.4, 27.0, "red", "white"
    )
    north = -south
    # the north apron: beyond the cross walk (3 to 6 m past the end line) the turf runs on to about
    # 15.7 m, and carries MONTCLAIR over STATE, read from the field (photo 0151)
    sheet.text(
        "MONTCLAIR",
        to_model(north * (hl + 11.2), 0),
        ang - 90 * north + 180,
        2.8,
        22.0,
        "red",
        "white",
    )
    sheet.text(
        "STATE", to_model(north * (hl + 8.0), 0), ang - 90 * north + 180, 2.0, 9.0, "red", "white"
    )


def draw(sheet, marks):
    """Paint primitives onto one sheet: areas first, then lines, then words on top."""
    for m in marks:
        if "ring" in m:
            sheet.area(m["ring"], m["colour"])
    for m in marks:
        if "line" in m:
            sheet.line(m["line"], m["width"], m["colour"])
    for m in marks:
        if "text" in m:
            sheet.text(m["text"], m["at"], m["right_angle"], m["height"], m["width"], m["colour"])


def hex_rgb(h):
    return tuple(int(h.lstrip("#")[i : i + 2], 16) for i in (0, 2, 4))


def main():
    args = sys.argv[1:]
    data = Path(args[0]).resolve()
    if HERE.parents[1] in data.parents or data == HERE.parents[1]:
        sys.exit("refusing to write textures inside the repository")
    out = data / "authored"
    out.mkdir(parents=True, exist_ok=True)
    n = 0
    for plan_dir in layout.areas(args):
        for old in out.glob(f"authored_{plan_dir.name}_*.png"):
            old.unlink()
        lay = layout.load(plan_dir)
        for s in lay["surfaces"]:
            for sh in s["sheets"] or []:
                sheet = Sheet(sh, s["kind"])
                on_field = s["kind"] == "turf"
                draw(sheet, [m for m in lay["markings"] if on_field or not m.get("field")])
                if on_field and lay["field_frame"]:
                    football_extras(sheet, lay["field_frame"])
                print(sh["name"], sheet.save(out), f"{sheet.k / SS:.1f} px/m")
                n += 1
        for b in lay["buildings"]:  # paint on a deck's roof level (layout.roof_paint)
            for sh in b.get("sheets") or []:
                sheet = Sheet(sh, "concrete", hex_rgb(b.get("roof_colour", ROOF)))
                draw(sheet, b["paint"])
                print(sh["name"], sheet.save(out), f"{sheet.k / SS:.1f} px/m")
                n += 1
    print("sheets", n, "in", out)


if __name__ == "__main__":
    main()
