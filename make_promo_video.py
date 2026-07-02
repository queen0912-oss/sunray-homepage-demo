from __future__ import annotations

import math
from pathlib import Path

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parent
STILLS = ROOT / "assets" / "video-stills"
OUT = ROOT / "assets" / "sunray-promo-demo.mp4"
OUT_WEBP = ROOT / "assets" / "sunray-promo-demo.webp"
WIDTH, HEIGHT = 1920, 1080
FPS = 30
WEBP_WIDTH, WEBP_HEIGHT = 1280, 720
WEBP_FPS = 12

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


FONT_KICKER = font(32, True)
FONT_TITLE = font(72, True)
FONT_BODY = font(34)
FONT_LOGO = font(42, True)


def cover_resize(image: Image.Image, scale: float, width: int = WIDTH, height: int = HEIGHT) -> Image.Image:
    src_w, src_h = image.size
    ratio = max(width / src_w, height / src_h) * scale
    resized = image.resize((math.ceil(src_w * ratio), math.ceil(src_h * ratio)), Image.Resampling.LANCZOS)
    left = (resized.width - width) // 2
    top = (resized.height - height) // 2
    return resized.crop((left, top, left + width, top + height))


def text_shadow(draw: ImageDraw.ImageDraw, xy: tuple[int, int], text: str, fnt: ImageFont.FreeTypeFont, fill: str) -> None:
    x, y = xy
    for dx, dy in [(-2, 2), (2, 2), (0, 3)]:
        draw.text((x + dx, y + dy), text, font=fnt, fill=(0, 0, 0, 180))
    draw.text((x, y), text, font=fnt, fill=fill)


def add_overlay(frame: Image.Image, kicker: str, title: str, body: str, scene_alpha: float) -> Image.Image:
    overlay = Image.new("RGBA", frame.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)

    draw.rectangle((0, 0, WIDTH, HEIGHT), fill=(0, 0, 0, 72))
    for x in range(WIDTH):
        alpha = int(210 * max(0, 1 - x / (WIDTH * 0.75)))
        draw.line((x, 0, x, HEIGHT), fill=(1, 7, 12, alpha))

    content_alpha = int(255 * scene_alpha)
    fill_blue = (96, 190, 255, content_alpha)
    fill_white = (248, 250, 252, content_alpha)
    fill_muted = (205, 214, 224, content_alpha)

    text_shadow(draw, (120, 685), kicker, FONT_KICKER, fill_blue)
    text_shadow(draw, (120, 735), title, FONT_TITLE, fill_white)
    text_shadow(draw, (124, 840), body, FONT_BODY, fill_muted)
    draw.line((120, 920, 560, 920), fill=(255, 138, 61, content_alpha), width=5)
    text_shadow(draw, (120, 955), "SUNRAY REINETSU", FONT_LOGO, (255, 255, 255, int(220 * scene_alpha)))

    return Image.alpha_composite(frame.convert("RGBA"), overlay).convert("RGB")


def add_overlay_small(frame: Image.Image, kicker: str, title: str, body: str, scene_alpha: float) -> Image.Image:
    scale_x = WEBP_WIDTH / WIDTH
    scale_y = WEBP_HEIGHT / HEIGHT
    overlay = Image.new("RGBA", frame.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    draw.rectangle((0, 0, WEBP_WIDTH, WEBP_HEIGHT), fill=(0, 0, 0, 72))
    for x in range(WEBP_WIDTH):
        alpha = int(210 * max(0, 1 - x / (WEBP_WIDTH * 0.75)))
        draw.line((x, 0, x, WEBP_HEIGHT), fill=(1, 7, 12, alpha))

    content_alpha = int(255 * scene_alpha)
    small_kicker = font(23, True)
    small_title = font(47, True)
    small_body = font(24)
    small_logo = font(29, True)

    def pos(x: int, y: int) -> tuple[int, int]:
        return int(x * scale_x), int(y * scale_y)

    text_shadow(draw, pos(120, 685), kicker, small_kicker, (96, 190, 255, content_alpha))
    text_shadow(draw, pos(120, 735), title, small_title, (248, 250, 252, content_alpha))
    text_shadow(draw, pos(124, 840), body, small_body, (205, 214, 224, content_alpha))
    draw.line((*pos(120, 920), *pos(560, 920)), fill=(255, 138, 61, content_alpha), width=4)
    text_shadow(draw, pos(120, 955), "SUNRAY REINETSU", small_logo, (255, 255, 255, int(220 * scene_alpha)))
    return Image.alpha_composite(frame.convert("RGBA"), overlay).convert("RGB")


def fade_alpha(frame_index: int, total_frames: int) -> float:
    fade_frames = FPS
    in_alpha = min(1.0, frame_index / fade_frames)
    out_alpha = min(1.0, (total_frames - frame_index - 1) / fade_frames)
    return max(0.0, min(1.0, in_alpha, out_alpha))


def main() -> None:
    images = [Image.open(STILLS / f"scene-{i:02}.png").convert("RGB") for i in range(1, 7)]
    writer = cv2.VideoWriter(str(OUT), cv2.VideoWriter_fourcc(*"mp4v"), FPS, (WIDTH, HEIGHT))
    if not writer.isOpened():
        raise RuntimeError("Could not open MP4 writer")

    for scene_index, (kicker, title, body, seconds) in enumerate(SCENES):
        image = images[scene_index]
        total = seconds * FPS
        for i in range(total):
            progress = i / max(1, total - 1)
            scale = 1.035 + progress * 0.055
            frame = cover_resize(image, scale)
            frame = add_overlay(frame, kicker, title, body, fade_alpha(i, total))
            writer.write(cv2.cvtColor(np.asarray(frame), cv2.COLOR_RGB2BGR))

    writer.release()
    webp_frames = []
    for scene_index, (kicker, title, body, seconds) in enumerate(SCENES):
        image = images[scene_index]
        total = seconds * WEBP_FPS
        for i in range(total):
            progress = i / max(1, total - 1)
            scale = 1.035 + progress * 0.055
            frame = cover_resize(image, scale, WEBP_WIDTH, WEBP_HEIGHT)
            frame = add_overlay_small(frame, kicker, title, body, fade_alpha(int(i * FPS / WEBP_FPS), int(total * FPS / WEBP_FPS)))
            webp_frames.append(frame)
    webp_frames[0].save(
        OUT_WEBP,
        save_all=True,
        append_images=webp_frames[1:],
        duration=round(1000 / WEBP_FPS),
        loop=0,
        quality=78,
        method=4,
    )
    print(OUT)
    print(OUT_WEBP)


if __name__ == "__main__":
    main()
