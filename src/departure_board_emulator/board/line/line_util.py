from enum import Enum
from departure_board_emulator.font import Font


class TextConstraint(Enum):
    Free = "Free"
    ReduceFontSize = "Reduce"
    Truncate = "Truncate"


class HorizontalAlignment(Enum):
    Left = "Left"
    Right = "Right"
    Centre = "Centre"


class VerticalAlignment(Enum):
    Up = "Up"
    Down = "Down"
    Centre = "Centre"


def parse_string_to_identifiers(text: str) -> list[str]:
    string_to_return: list[str] = []
    local_identifier = ""
    identifier_mode = False

    for letter in text:
        if letter == "%":
            if identifier_mode:
                if local_identifier == "" or " " in local_identifier:
                    string_to_return.append("%")
                    string_to_return.extend(list(local_identifier))
                    string_to_return.append("%")
                else:
                    string_to_return.append(f"%{local_identifier}%")

                local_identifier = ""
                identifier_mode = False
            else:
                identifier_mode = True
        else:
            if identifier_mode:
                local_identifier += letter
            else:
                string_to_return.append(letter)

    if identifier_mode:
        string_to_return.append("%")
        string_to_return.extend(list(local_identifier))

    return string_to_return


def find_text_width(font: Font, text: list[str]) -> int:
    predicted_width = -font.default_spacing

    for letter in text:
        glyph = font.find_glyph_from_letter(letter)
        if not glyph:
            continue
        predicted_width += glyph.width + font.default_spacing

    return max(0, predicted_width)


def determine_best_font(
    fonts: list[Font], text: list[str], width: int, constraint: TextConstraint
) -> Font:
    chosen_font = fonts[0]
    reversed_font_list = reversed(fonts)

    for font in reversed_font_list:
        calc_width = find_text_width(font, text)

        if calc_width <= width and constraint == TextConstraint.ReduceFontSize:
            chosen_font = font

    return chosen_font
