from __future__ import annotations

import math
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont


ROOT = Path(__file__).resolve().parent
STILLS = ROOT / "assets" / "video-stills"
OUT = ROOT / "assets" / "sunray-promo-demo.webp"
LOGO = ROOT / "assets" / "sunray-logo.png"
WIDTH, HEIGHT = 960, 540
FPS = 8

SCENES = [
    ("Combustion", "火炎を、技術で制御する。", "燃焼の安定性と安全性を、現場ごとに設計する。", 4),
    ("Equipment", "装置の細部に、技術が宿る。", "バーナー、配管、制御盤、計器を精密に組み合わせる。", 5),
    ("Engineering", "装置を、現場に合わせて組み上げる。", "図面、組立、検査。用途に合わせて一台ずつ設計する。", 6),
    ("Environment", "クリーンな生産環境へ。", "排ガス処理・脱臭・省エネを支える技術。", 7),
    ("Support", "導入後も、現場を止めない。", "点検、更新、改造、トラブル対応まで支える。", 5),
    ("Sunray Reinetsu", "燃焼技術で、産業と環境の未来を支える。", "サンレー冷熱株式会社", 3),
]


def font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    candidates = [
        Path("C:/Windows/Fonts/meiryob.ttc" if bold else "C:/Windows/Fonts/meiryo.ttc"),
        Path("C:/Windows/Fonts/YuGothB.ttc" if bold else "C:/Windows/Fonts/YuGothR.ttc"),
        Path("C:/Windows/Fonts/msgothic.ttc"),
    ]
    for candidate in candidates:
        if candidate.exists():
            return ImageFont.truetype(str(candidate), size=size)
    return ImageFont.load_default()


FONT_KICKER = font(20, True)
FONT_TITLE = font(40, True)
FONT_BODY = font(21)
FONT_LOGO = font(24, True)
FONT_TAGLINE = font(26, True)


def cover_resize(image: Image.Image, scale: float) -> Image.Image:
    src_w, src_h = image.size
    ratio = max(WIDTH / src_w, HEIGHT / src_h) * scale
    resized = image.resize((math.ceil(src_w * ratio), math.ceil(src_h * ratio)), Image.Resampling.LANCZOS)
    left = (resized.width - WIDTH) // 2
    top = (resized.height - HEIGHT) // 2
    return resized.crop((left, top, left + WIDTH, top + HEIGHT))


def text_shadow(draw: ImageDraw.ImageDraw, xy: tuple[int, int], text: str, fnt: ImageFont.FreeTypeFont, fill: tuple[int, int, int, int]) -> None:
    x, y = xy
    for dx, dy in [(-2, 2), (2, 2), (0, 3)]:
        draw.text((x + dx, y + dy), text, font=fnt, fill=(0, 0, 0, min(fill[3], 170)))
    draw.text((x, y), text, font=fnt, fill=fill)


def fade_alpha(frame_index: int, total_frames: int) -> float:
    fade_frames = FPS
    in_alpha = min(1.0, frame_index / fade_frames)
    out_alpha = min(1.0, (total_frames - frame_index - 1) / fade_frames)
    return max(0.0, min(1.0, in_alpha, out_alpha))


def add_overlay(frame: Image.Image, kicker: str, title: str, body: str, alpha_ratio: float) -> Image.Image:
    overlay = Image.new("RGBA", frame.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    draw.rectangle((0, 0, WIDTH, HEIGHT), fill=(0, 0, 0, 72))
    for x in range(WIDTH):
        alpha = int(210 * max(0, 1 - x / (WIDTH * 0.75)))
        draw.line((x, 0, x, HEIGHT), fill=(1, 7, 12, alpha))

    a = int(255 * alpha_ratio)
    text_shadow(draw, (72, 338), kicker, FONT_KICKER, (96, 190, 255, a))
    text_shadow(draw, (72, 374), title, FONT_TITLE, (248, 250, 252, a))
    text_shadow(draw, (74, 445), body, FONT_BODY, (205, 214, 224, a))
    draw.line((72, 492, 330, 492), fill=(255, 138, 61, a), width=4)
    text_shadow(draw, (72, 512), "SUNRAY REINETSU", FONT_LOGO, (255, 255, 255, int(220 * alpha_ratio)))
    return Image.alpha_composite(frame.convert("RGBA"), overlay).convert("RGB")


def load_red_logo() -> Image.Image:
    logo = Image.open(LOGO).convert("RGBA")
    pixels = logo.load()
    for y in range(logo.height):
        for x in range(logo.width):
            r, g, b, a = pixels[x, y]
            keep = r > 90 and r > g * 1.45 and r > b * 1.45
            pixels[x, y] = (214, 13, 35, a if keep else 0)
    bbox = logo.getbbox()
    if bbox:
        logo = logo.crop(bbox)
    target_w = int(WIDTH * 0.58)
    scale = target_w / logo.width
    return logo.resize((target_w, int(logo.height * scale)), Image.Resampling.LANCZOS)


def add_logo_scene(logo: Image.Image, progress: float, alpha_ratio: float) -> Image.Image:
    frame = Image.new("RGB", (WIDTH, HEIGHT), (3, 6, 10))
    overlay = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    draw.rectangle((0, 0, WIDTH, HEIGHT), fill=(0, 0, 0, 72))
    for x in range(WIDTH):
        glow = int(48 * max(0, 1 - abs(x - WIDTH * 0.5) / (WIDTH * 0.5)))
        draw.line((x, 0, x, HEIGHT), fill=(18, 31, 43, glow))

    appear = min(1.0, progress / 0.22)
    a = int(255 * alpha_ratio * appear)
    x = (WIDTH - logo.width) // 2
    y = int(HEIGHT * 0.38) - logo.height // 2

    logo_layer = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    logo_base = logo.copy()
    logo_base.putalpha(logo_base.getchannel("A").point(lambda p: int(p * a / 255)))
    logo_layer.alpha_composite(logo_base, (x, y))

    mask = Image.new("L", (WIDTH, HEIGHT), 0)
    mask.paste(logo_base.getchannel("A"), (x, y))
    glow_mask = mask.filter(ImageFilter.GaussianBlur(7))
    glow_layer = Image.new("RGBA", (WIDTH, HEIGHT), (255, 54, 62, int(140 * alpha_ratio * appear)))
    overlay = Image.alpha_composite(overlay, Image.composite(glow_layer, Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0)), glow_mask))

    sweep_center = int((progress * 1.22 - 0.12) * WIDTH)
    sweep = Image.new("L", (WIDTH, HEIGHT), 0)
    sweep_draw = ImageDraw.Draw(sweep)
    sweep_draw.rectangle((sweep_center - 54, 0, sweep_center + 20, HEIGHT), fill=210)
    sweep = sweep.filter(ImageFilter.GaussianBlur(18))
    sweep = Image.composite(sweep, Image.new("L", (WIDTH, HEIGHT), 0), mask)
    sweep_layer = Image.new("RGBA", (WIDTH, HEIGHT), (255, 246, 212, int(235 * alpha_ratio)))
    overlay = Image.alpha_composite(overlay, logo_layer)
    overlay = Image.alpha_composite(overlay, Image.composite(sweep_layer, Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0)), sweep))

    draw = ImageDraw.Draw(overlay)
    tagline = "燃焼技術で、産業と環境の未来を支える。"
    tag_w = draw.textbbox((0, 0), tagline, font=FONT_TAGLINE)[2]
    text_shadow(draw, ((WIDTH - tag_w) // 2, int(HEIGHT * 0.58)), tagline, FONT_TAGLINE, (248, 250, 252, int(230 * alpha_ratio * appear)))
    draw.line((int(WIDTH * 0.34), int(HEIGHT * 0.69), int(WIDTH * 0.66), int(HEIGHT * 0.69)), fill=(214, 13, 35, int(190 * alpha_ratio * appear)), width=3)

    return Image.alpha_composite(frame.convert("RGBA"), overlay).convert("RGB")


def main() -> None:
    old = OUT
    if old.exists():
        old.unlink()
    images = [Image.open(STILLS / f"scene-{i:02}.png").convert("RGB") for i in range(1, 7)]
    red_logo = load_red_logo()
    frames: list[Image.Image] = []
    for scene_index, (kicker, title, body, seconds) in enumerate(SCENES):
        image = images[scene_index]
        total = seconds * FPS
        for i in range(total):
            if scene_index == len(SCENES) - 1:
                progress = i / max(1, total - 1)
                frames.append(add_logo_scene(red_logo, progress, fade_alpha(i, total)))
                continue
            progress = i / max(1, total - 1)
            frame = cover_resize(image, 1.035 + progress * 0.055)
            frames.append(add_overlay(frame, kicker, title, body, fade_alpha(i, total)))

    frames[0].save(
        OUT,
        save_all=True,
        append_images=frames[1:],
        duration=round(1000 / FPS),
        loop=0,
        quality=72,
        method=3,
    )
    print(OUT)


if __name__ == "__main__":
    main()
