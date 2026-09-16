import json

import departure_board_emulator.types.types as Types
from departure_board_emulator.font.font import Font
from departure_board_emulator.font.glyph import Glyph


def font_to_json(font: Font) -> str:
    payload: Types.FontPayload = {
        "name": font.name,
        "default_width": font.default_width,
        "spacing": font.default_spacing,
        "height": font.height,
        "markers": font.markers,
        "glyphs": {},
    }

    glyph: Glyph
    for glyph in font.glyphs:
        glyph_payload: Types.GlyphPayload = {
            "identifier": glyph.name,
            "width": glyph.width,
            "bitmap": glyph.grid,
        }
        payload["glyphs"][glyph_payload["identifier"]] = glyph_payload

    return json.dumps(payload)


def json_to_font(json_font: str) -> Font:
    decoded: Types.FontPayload = json.loads(json_font)

    markers: list[int] = decoded.get("markers") or []

    created_font = Font(
        decoded["name"],
        decoded["height"],
        decoded["spacing"],
        decoded["default_width"],
        markers,
    )

    glyph_data: Types.GlyphPayload
    for glyph_data in decoded["glyphs"].values():
        created_glyph = Glyph(
            glyph_data["identifier"], glyph_data["width"], created_font
        )
        created_glyph.grid = glyph_data["bitmap"]

    return created_font
