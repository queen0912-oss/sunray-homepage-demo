from __future__ import annotations

import math
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parent
STILLS = ROOT / "assets" / "video-stills"
OUT = ROOT / "assets" / "sunray-promo-intro.webp"
WIDTH, HEIGHT = 1280, 720
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


FONT_KICKER = font(25, True)
FONT_TITLE = font(52, True)
FONT_BODY = font(28)
FONT_LOGO = font(32, True)


def cover_resize(image: Image.Image) -> Image.Image:
    src_w, src_h = image.size
    ratio = max(WIDTH / src_w, HEIGHT / src_h) * 1.02
    resized = image.resize((math.ceil(src_w * ratio), math.ceil(src_h * ratio)), Image.Resampling.LANCZOS)
    left = (resized.width - WIDTH) // 2
    top = (resized.height - HEIGHT) // 2
    return resized.crop((left, top, left + WIDTH, top + HEIGHT))


def text_shadow(draw: ImageDraw.ImageDraw, xy: tuple[int, int], text: str, fnt: ImageFont.FreeTypeFont, fill: tuple[int, int, int, int]) -> None:
    x, y = xy
    for dx, dy in [(-2, 2), (2, 2), (0, 3)]:
        draw.text((x + dx, y + dy), text, font=fnt, fill=(0, 0, 0, min(fill[3], 160)))
    draw.text((x, y), text, font=fnt, fill=fill)


def fade_alpha(frame_index: int, total_frames: int) -> float:
    fade_frames = FPS
    in_alpha = min(1.0, frame_index / fade_frames)
    out_alpha = min(1.0, (total_frames - frame_index - 1) / fade_frames)
    return max(0.0, min(1.0, in_alpha, out_alpha))


def add_overlay(frame: Image.Image, kicker: str, title: str, body: str, alpha_ratio: float) -> Image.Image:
    overlay = Image.new("RGBA", frame.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    draw.rectangle((0, 0, WIDTH, HEIGHT), fill=(0, 0, 0, 38))
    for x in range(WIDTH):
        alpha = int(115 * max(0, 1 - x / (WIDTH * 0.68)))
        draw.line((x, 0, x, HEIGHT), fill=(1, 7, 12, alpha))

    a = int(255 * alpha_ratio)
    text_shadow(draw, (92, 452), kicker, FONT_KICKER, (96, 190, 255, a))
    text_shadow(draw, (92, 498), title, FONT_TITLE, (248, 250, 252, a))
    text_shadow(draw, (96, 588), body, FONT_BODY, (216, 224, 234, a))
    draw.line((92, 648, 460, 648), fill=(255, 138, 61, a), width=4)
    text_shadow(draw, (92, 672), "SUNRAY REINETSU", FONT_LOGO, (255, 255, 255, int(220 * alpha_ratio)))
    return Image.alpha_composite(frame.convert("RGBA"), overlay).convert("RGB")


def blend(a: Image.Image, b: Image.Image, amount: float) -> Image.Image:
    return Image.blend(a, b, amount)


def main() -> None:
    if OUT.exists():
        OUT.unlink()

    base_images = [cover_resize(Image.open(STILLS / f"scene-{i:02}.png").convert("RGB")) for i in range(1, 7)]
    frames: list[Image.Image] = []

    for scene_index, (kicker, title, body, seconds) in enumerate(SCENES):
        current = base_images[scene_index]
        next_image = base_images[min(scene_index + 1, len(base_images) - 1)]
        total = seconds * FPS
        crossfade_frames = FPS
        for i in range(total):
            image = current
            if scene_index < len(SCENES) - 1 and i >= total - crossfade_frames:
                image = blend(current, next_image, (i - (total - crossfade_frames)) / crossfade_frames)
            frames.append(add_overlay(image, kicker, title, body, fade_alpha(i, total)))

    frames[0].save(
        OUT,
        save_all=True,
        append_images=frames[1:],
        duration=round(1000 / FPS),
        loop=0,
        quality=74,
        method=3,
    )
    print(OUT)


if __name__ == "__main__":
    main()
