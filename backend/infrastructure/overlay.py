import logging
import os
import subprocess
import tempfile
from typing import List, Tuple, cast

from domain.models import Checkpoint, FontSize, OverlayPosition, OverlayTemplate, Style

logger = logging.getLogger("checkpoint_overlay")

FONT_BOLD = [
    "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
    "/Library/Fonts/Arial Bold.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
]
FONT_REGULAR = [
    "/System/Library/Fonts/Supplemental/Arial.ttf",
    "/Library/Fonts/Arial.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
]

FONT_SIZE_MULTIPLIERS = {
    FontSize.small: 0.75,
    FontSize.medium: 1.0,
    FontSize.large: 1.30,
}

STYLE_CONFIGS = {
    Style.clean: {
        "text_color": (255, 255, 255, 255),
        "bg_color":   (10, 10, 10, 165),
        "font_scale": 0.042,
        "bold": True,
    },
    Style.cinematic: {
        "text_color": (240, 232, 210, 255),
        "bg_color":   (0, 0, 0, 105),
        "font_scale": 0.033,
        "bold": False,
    },
    Style.bold: {
        "text_color": (255, 245, 0, 255),
        "bg_color":   (0, 0, 0, 215),
        "font_scale": 0.052,
        "bold": True,
    },
    Style.minimal: {
        "text_color": (255, 255, 255, 255),
        "bg_color":   (0, 0, 0, 60),
        "font_scale": 0.028,
        "bold": False,
    },
}


def get_video_info(video_path: str) -> Tuple[int, int, float, bool]:
    """Returns (width, height, duration, has_audio)."""
    import json as _json
    cmd = [
        "ffprobe", "-v", "quiet",
        "-print_format", "json",
        "-show_streams", "-show_format",
        video_path,
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, check=True)
    info = _json.loads(result.stdout)
    duration = float(info["format"]["duration"])
    width, height = 1920, 1080
    has_audio = False
    for stream in info.get("streams", []):
        if stream.get("codec_type") == "video":
            width = int(stream.get("width", 1920))
            height = int(stream.get("height", 1080))
        elif stream.get("codec_type") == "audio":
            has_audio = True
    return width, height, duration, has_audio


def _load_font(size: int, bold: bool = False):
    from PIL import ImageFont
    candidates = FONT_BOLD if bold else FONT_REGULAR
    for path in candidates:
        if os.path.exists(path):
            try:
                return ImageFont.truetype(path, size)
            except Exception:
                continue
    try:
        return ImageFont.load_default(size)
    except Exception:
        return ImageFont.load_default()


def _anchor(
    position: OverlayPosition,
    width: int,
    height: int,
    box_w: int,
    box_h: int,
) -> Tuple[int, int]:
    h_pad = 40
    v_top = 80
    v_bottom = height - box_h - 70
    cx = (width - box_w) // 2
    cy = (height - box_h) // 2

    table = {
        OverlayPosition.top_left:     (h_pad, v_top),
        OverlayPosition.top_center:   (cx, v_top),
        OverlayPosition.top_right:    (width - box_w - h_pad, v_top),
        OverlayPosition.bottom_left:  (h_pad, v_bottom),
        OverlayPosition.bottom_center:(cx, v_bottom),
        OverlayPosition.bottom_right: (width - box_w - h_pad, v_bottom),
        OverlayPosition.center:       (cx, cy),
    }
    ax, ay = table.get(position, (h_pad, v_top))
    ax = max(10, min(ax, width - box_w - 10))
    ay = max(10, min(ay, height - box_h - 10))
    return ax, ay


# ─── Template renderers ────────────────────────────────────────────────────────

def _render_corner_badge(
    draw, text: str, sub_text: str | None,
    cfg: dict, position: OverlayPosition,
    width: int, height: int,
) -> None:
    from PIL import Image, ImageDraw as _ID
    font_size = max(20, int(height * cfg["font_scale"]))
    sub_size  = max(15, int(font_size * 0.68))
    pad = max(12, int(font_size * 0.38))
    radius = max(6, pad // 2)
    bold = cfg["bold"]

    main_font = _load_font(font_size, bold=bold)
    sub_font  = _load_font(sub_size,  bold=False)

    scratch = _ID.Draw(Image.new("RGBA", (1, 1)))
    mb = scratch.textbbox((0, 0), text, font=main_font)
    mw, mh = mb[2] - mb[0], mb[3] - mb[1]

    sw, sh = 0, 0
    if sub_text:
        sb = scratch.textbbox((0, 0), sub_text, font=sub_font)
        sw, sh = int(sb[2] - sb[0]), int(sb[3] - sb[1])

    gap = 6 if sub_text else 0
    box_w = int(max(mw, sw) + 2 * pad)
    box_h = int(mh + (sh + gap if sub_text else 0) + 2 * pad)
    ax, ay = _anchor(position, width, height, box_w, box_h)

    draw.rounded_rectangle([ax, ay, ax + box_w, ay + box_h], radius=radius, fill=cfg["bg_color"])
    tx, ty = ax + pad, ay + pad
    draw.text((tx, ty), text, fill=cfg["text_color"], font=main_font)
    if sub_text:
        sub_color = cfg["text_color"][:3] + (int(cfg["text_color"][3] * 0.78),)
        draw.text((tx, ty + mh + gap), sub_text, fill=sub_color, font=sub_font)


def _render_lower_third(
    draw, img, text: str, sub_text: str | None,
    cfg: dict, width: int, height: int,
) -> None:
    """Full-width gradient bar at the bottom — TV news / documentary style."""
    from PIL import Image, ImageDraw as _ID
    font_size = max(24, int(height * cfg["font_scale"] * 1.1))
    sub_size  = max(16, int(font_size * 0.62))
    v_pad = int(font_size * 0.5)
    h_pad = int(width * 0.04)

    main_font = _load_font(font_size, bold=True)
    sub_font  = _load_font(sub_size,  bold=False)

    scratch = _ID.Draw(Image.new("RGBA", (1, 1)))
    mb = scratch.textbbox((0, 0), text, font=main_font)
    mh = mb[3] - mb[1]
    sh = 0
    if sub_text:
        sb = scratch.textbbox((0, 0), sub_text, font=sub_font)
        sh = int(sb[3] - sb[1])

    gap = 6 if sub_text else 0
    bar_h = int(mh + (sh + gap if sub_text else 0) + 2 * v_pad)
    bar_y = height - bar_h - 60

    # Gradient: opaque on the left, transparent on the right
    gradient = Image.new("RGBA", (width, bar_h), (0, 0, 0, 0))
    for x in range(width):
        alpha = int(cfg["bg_color"][3] * max(0.0, 1.0 - (x / width) ** 1.5))
        for y in range(bar_h):
            gradient.putpixel((x, y), cfg["bg_color"][:3] + (alpha,))
    img.alpha_composite(gradient, (0, bar_y))

    # Accent left stripe
    draw.rectangle([0, bar_y, 6, bar_y + bar_h], fill=cfg["text_color"])

    ty = bar_y + v_pad
    draw.text((h_pad, ty), text, fill=cfg["text_color"], font=main_font)
    if sub_text:
        sub_color = cfg["text_color"][:3] + (int(cfg["text_color"][3] * 0.72),)
        draw.text((h_pad, ty + mh + gap), sub_text, fill=sub_color, font=sub_font)


def _render_chyron(
    draw, text: str,
    cfg: dict, width: int, height: int,
) -> None:
    """Thin full-width subtitle band at the very bottom."""
    from PIL import Image, ImageDraw as _ID
    font_size = max(18, int(height * cfg["font_scale"] * 0.82))
    pad_v = int(font_size * 0.35)

    font = _load_font(font_size, bold=False)
    scratch = _ID.Draw(Image.new("RGBA", (1, 1)))
    mb = scratch.textbbox((0, 0), text, font=font)
    mw, mh = mb[2] - mb[0], mb[3] - mb[1]

    band_h = mh + 2 * pad_v
    band_y = height - band_h - 20

    bg = (0, 0, 0, int(cfg["bg_color"][3] * 1.1))
    draw.rectangle([0, band_y, width, band_y + band_h], fill=bg)

    tx = (width - mw) // 2
    draw.text((tx, band_y + pad_v), text, fill=cfg["text_color"], font=font)


def _render_cinematic_title(
    draw, text: str, sub_text: str | None,
    cfg: dict, width: int, height: int,
) -> None:
    """Centred pill with horizontal rules — chapter / transition marker."""
    from PIL import Image, ImageDraw as _ID
    font_size = max(22, int(height * cfg["font_scale"] * 1.05))
    sub_size  = max(14, int(font_size * 0.65))

    main_font = _load_font(font_size, bold=True)
    sub_font  = _load_font(sub_size,  bold=False)

    scratch = _ID.Draw(Image.new("RGBA", (1, 1)))
    mb = scratch.textbbox((0, 0), text, font=main_font)
    mw, mh = mb[2] - mb[0], mb[3] - mb[1]

    pill_pad_h = int(font_size * 0.65)
    pill_pad_v = int(font_size * 0.32)
    pill_w = mw + 2 * pill_pad_h
    pill_h = mh + 2 * pill_pad_v
    pill_r = pill_h // 2
    pill_x = (width - pill_w) // 2
    pill_y = (height - pill_h) // 2

    draw.rounded_rectangle(
        [pill_x, pill_y, pill_x + pill_w, pill_y + pill_h],
        radius=pill_r, fill=cfg["bg_color"],
    )
    draw.text(
        (pill_x + pill_pad_h, pill_y + pill_pad_v),
        text.upper(), fill=cfg["text_color"], font=main_font,
    )

    line_y = pill_y + pill_h // 2
    line_col = cfg["text_color"][:3] + (70,)
    margin = 28
    draw.line([(margin, line_y), (pill_x - 14, line_y)], fill=line_col, width=2)
    draw.line([(pill_x + pill_w + 14, line_y), (width - margin, line_y)], fill=line_col, width=2)

    if sub_text:
        sb = scratch.textbbox((0, 0), sub_text, font=sub_font)
        sw = sb[2] - sb[0]
        sub_col = cfg["text_color"][:3] + (int(cfg["text_color"][3] * 0.65),)
        draw.text(((width - sw) // 2, pill_y + pill_h + 10), sub_text, fill=sub_col, font=sub_font)


def _render_pill(
    draw, text: str, sub_text: str | None,
    cfg: dict, position: OverlayPosition,
    width: int, height: int,
) -> None:
    """Compact pill — like corner_badge but always centred horizontally."""
    from PIL import Image, ImageDraw as _ID
    font_size = max(18, int(height * cfg["font_scale"] * 0.88))
    sub_size  = max(13, int(font_size * 0.68))
    pad_h = int(font_size * 0.55)
    pad_v = int(font_size * 0.28)

    main_font = _load_font(font_size, bold=True)
    sub_font  = _load_font(sub_size,  bold=False)

    scratch = _ID.Draw(Image.new("RGBA", (1, 1)))
    mb = scratch.textbbox((0, 0), text, font=main_font)
    mw, mh = mb[2] - mb[0], mb[3] - mb[1]
    sw, sh = 0, 0
    if sub_text:
        sb = scratch.textbbox((0, 0), sub_text, font=sub_font)
        sw, sh = int(sb[2] - sb[0]), int(sb[3] - sb[1])

    gap = 4 if sub_text else 0
    pill_w = int(max(mw, sw) + 2 * pad_h)
    pill_h = int(mh + (sh + gap if sub_text else 0) + 2 * pad_v)
    pill_r = pill_h // 2
    ax, ay = _anchor(position, width, height, pill_w, pill_h)

    draw.rounded_rectangle([ax, ay, ax + pill_w, ay + pill_h], radius=pill_r, fill=cfg["bg_color"])
    tx = ax + (pill_w - mw) // 2
    draw.text((tx, ay + pad_v), text, fill=cfg["text_color"], font=main_font)
    if sub_text:
        stx = ax + (pill_w - sw) // 2
        sub_col = cfg["text_color"][:3] + (int(cfg["text_color"][3] * 0.78),)
        draw.text((stx, ay + pad_v + mh + gap), sub_text, fill=sub_col, font=sub_font)


# ─── Dispatcher ────────────────────────────────────────────────────────────────

def _render_overlay(
    text: str,
    sub_text: str | None,
    cfg: dict,
    position: OverlayPosition,
    width: int,
    height: int,
    out_path: str,
    template: OverlayTemplate = OverlayTemplate.corner_badge,
) -> None:
    from PIL import Image, ImageDraw

    img = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    if template == OverlayTemplate.lower_third:
        _render_lower_third(draw, img, text, sub_text, cfg, width, height)
    elif template == OverlayTemplate.chyron:
        _render_chyron(draw, text, cfg, width, height)
    elif template == OverlayTemplate.cinematic_title:
        _render_cinematic_title(draw, text, sub_text, cfg, width, height)
    elif template == OverlayTemplate.pill:
        _render_pill(draw, text, sub_text, cfg, position, width, height)
    else:
        _render_corner_badge(draw, text, sub_text, cfg, position, width, height)

    img.save(out_path, "PNG")


# ─── Main export function ──────────────────────────────────────────────────────

def apply_overlays(
    input_path: str,
    output_path: str,
    checkpoints: List[Checkpoint],
    style: Style,
    font_size: FontSize = FontSize.medium,
    progress_callback=None,
) -> None:
    width, height, duration, has_audio = get_video_info(input_path)
    logger.info("apply_overlays: %dx%d %.1fs %d checkpoints", width, height, duration, len(checkpoints))

    size_mult = FONT_SIZE_MULTIPLIERS.get(font_size, 1.0)
    style_cfg = dict(STYLE_CONFIGS[style])
    style_cfg["font_scale"] = cast(float, style_cfg["font_scale"]) * size_mult

    if not checkpoints:
        cmd = ["ffmpeg", "-y", "-i", input_path,
               "-c:v", "libx264", "-crf", "22", "-preset", "fast"]
        if has_audio:
            cmd += ["-c:a", "copy"]
        cmd += ["-movflags", "+faststart", output_path]
        r = subprocess.run(cmd, capture_output=True, text=True)
        if r.returncode != 0:
            raise RuntimeError(f"FFmpeg failed: {r.stderr[-600:]}")
        return

    # Sort: chapters first (lowest z), then content, then subtitles on top
    layer_order = {"chapters": 0, "content": 1, "subtitles": 2}
    sorted_cps = sorted(checkpoints, key=lambda c: layer_order.get(c.layer, 1))

    tmp_dir = tempfile.mkdtemp(prefix="chk_overlay_")
    png_paths: List[str] = []

    try:
        if progress_callback:
            progress_callback("Rendering overlay images...")

        for i, cp in enumerate(sorted_cps):
            p = os.path.join(tmp_dir, f"ovr_{i:04d}.png")
            _render_overlay(
                text=cp.text,
                sub_text=cp.sub_text,
                cfg=style_cfg,
                position=cp.position,
                width=width,
                height=height,
                out_path=p,
                template=cp.template,
            )
            png_paths.append(p)
            logger.debug("rendered %d: [%s/%s] '%s'", i, cp.layer, cp.template, cp.text)

        if progress_callback:
            progress_callback("Running FFmpeg overlay pass...")

        cmd = ["ffmpeg", "-y", "-i", input_path]
        for p in png_paths:
            cmd += ["-i", p]

        n = len(png_paths)
        parts: List[str] = []
        for i, cp in enumerate(sorted_cps):
            t_start = cp.timestamp
            t_end = min(t_start + cp.duration, duration - 0.05)
            src = "[0:v]" if i == 0 else f"[v{i}]"
            dst = "[vout]" if i == n - 1 else f"[v{i + 1}]"
            parts.append(
                f"{src}[{i + 1}:v]overlay=0:0:enable='between(t,{t_start:.3f},{t_end:.3f})'{dst}"
            )

        cmd += ["-filter_complex", ";".join(parts), "-map", "[vout]"]
        if has_audio:
            cmd += ["-map", "0:a", "-c:a", "copy"]
        cmd += ["-c:v", "libx264", "-crf", "22", "-preset", "fast",
                "-movflags", "+faststart", output_path]

        logger.info("ffmpeg command: %s ...", " ".join(cmd[:14]))
        r = subprocess.run(cmd, capture_output=True, text=True)
        if r.returncode != 0:
            logger.error("ffmpeg stderr: %s", r.stderr[-800:])
            raise RuntimeError(f"FFmpeg failed: {r.stderr[-600:]}")
        logger.info("apply_overlays: done → %s", output_path)

    finally:
        for p in png_paths:
            try:
                os.unlink(p)
            except Exception:
                pass
        try:
            os.rmdir(tmp_dir)
        except Exception:
            pass
