"""Generate the multi-resolution Windows icon used by PyInstaller."""

from pathlib import Path

from PIL import Image, ImageDraw


SCALE = 4
SIZE = 256


def scaled_box(values: tuple[int, int, int, int]) -> tuple[int, int, int, int]:
    return tuple(value * SCALE for value in values)


def main() -> None:
    canvas = Image.new("RGBA", (SIZE * SCALE, SIZE * SCALE), (0, 0, 0, 0))
    draw = ImageDraw.Draw(canvas)
    draw.rounded_rectangle(
        scaled_box((0, 0, 255, 255)),
        radius=54 * SCALE,
        fill=(7, 74, 139, 255),
    )
    draw.rounded_rectangle(
        scaled_box((24, 24, 231, 231)),
        radius=40 * SCALE,
        fill=(9, 111, 222, 120),
    )
    draw.rounded_rectangle(
        scaled_box((35, 68, 221, 210)),
        radius=27 * SCALE,
        fill=(4, 25, 47, 105),
    )
    draw.rounded_rectangle(
        scaled_box((45, 57, 211, 199)),
        radius=24 * SCALE,
        fill=(12, 79, 136, 255),
        outline=(188, 228, 255, 255),
        width=7 * SCALE,
    )
    draw.polygon(
        [
            (106 * SCALE, 82 * SCALE),
            (106 * SCALE, 176 * SCALE),
            (183 * SCALE, 129 * SCALE),
        ],
        fill=(245, 252, 255, 255),
    )
    draw.ellipse(scaled_box((60, 75, 74, 89)), fill=(85, 239, 172, 255))
    draw.rounded_rectangle(
        scaled_box((65, 212, 191, 223)),
        radius=6 * SCALE,
        fill=(123, 197, 255, 190),
    )

    icon = canvas.resize((SIZE, SIZE), Image.Resampling.LANCZOS)
    destination = Path(__file__).resolve().parent.parent / "assets" / "app_icon.ico"
    destination.parent.mkdir(parents=True, exist_ok=True)
    icon.save(destination, format="ICO", sizes=[(16, 16), (24, 24), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)])
    print(f"Generated {destination}")


if __name__ == "__main__":
    main()
