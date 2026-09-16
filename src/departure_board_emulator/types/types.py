from typing import TypedDict


class Station(TypedDict):
    TIPLOC: str
    CRS: str
    Name: str
    TOC: list[str]
    HasAtoZ: bool


class GlyphPayload(TypedDict):
    identifier: str
    width: int
    bitmap: list[list[int]]


class FontPayload(TypedDict):
    name: str
    default_width: int
    spacing: int
    height: int
    markers: list[int]
    glyphs: dict[str, GlyphPayload]
