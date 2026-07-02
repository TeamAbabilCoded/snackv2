import subprocess
import os
import config
import random
import json
import textwrap
import re
import time
from datetime import datetime, timedelta, timezone

os.environ["FFREPORT"] = "file=ffmpeg_log.txt:level=32"


# =========================
# CONFIG HELPER
# =========================

def cfg(name, default):
    return getattr(config, name, default)


# =========================
# TEXT HELPER
# =========================

def escape_text(text):
    return (
        text.replace("\\", "\\\\")
        .replace(":", "\\:")
        .replace("'", "\\'")
        .replace(",", "\\,")
        .replace("[", "\\[")
        .replace("]", "\\]")
    )


# =========================
# VIDEO INFO
# =========================

def get_video_info(filepath):
    cmd = [
        "ffprobe",
        "-v", "error",
        "-print_format", "json",
        "-show_streams",
        "-show_format",
        filepath
    ]

    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True
    )

    if result.returncode != 0:
        print(result.stderr)
        raise RuntimeError("Gagal membaca informasi video.")

    data = json.loads(result.stdout)

    video_stream = None

    for stream in data.get("streams", []):
        if stream.get("codec_type") == "video":
            video_stream = stream
            break

    if video_stream is None:
        raise RuntimeError("Stream video tidak ditemukan.")

    duration = float(data["format"].get("duration", 0))
    size = int(data["format"].get("size", 0))

    fps_text = video_stream.get("r_frame_rate", "0/1")

    try:
        num, den = fps_text.split("/")
        fps = round(float(num) / float(den), 2) if float(den) != 0 else 0
    except Exception:
        fps = 0

    return {
        "width": video_stream.get("width", 0),
        "height": video_stream.get("height", 0),
        "fps": fps,
        "duration": duration,
        "size": size
    }


def get_video_duration(filepath):
    return float(get_video_info(filepath)["duration"])


def format_duration(seconds):
    seconds = int(seconds)

    h = seconds // 3600
    m = (seconds % 3600) // 60
    s = seconds % 60

    return f"{h:02}:{m:02}:{s:02}"


def format_size(size):
    size = float(size)

    for unit in ["B", "KB", "MB", "GB", "TB"]:
        if size < 1024:
            return f"{size:.2f} {unit}"
        size /= 1024

    return f"{size:.2f} PB"


def print_video_info(filepath, info):
    print("\n" + "=" * 60)
    print("INFORMASI VIDEO INPUT")
    print("=" * 60)
    print(f"File       : {os.path.basename(filepath)}")
    print(f"Resolusi   : {info['width']}x{info['height']}")
    print(f"FPS        : {info['fps']}")
    print(f"Durasi     : {format_duration(info['duration'])}")
    print(f"Ukuran     : {format_size(info['size'])}")
    print("=" * 60 + "\n")


# =========================
# TIME + PROGRESS
# =========================

def get_jakarta_time():
    jakarta = timezone(timedelta(hours=7))
    return datetime.now(jakarta).strftime("%H:%M:%S")


def progress_bar(percent, length=20):
    filled = int(length * percent // 100)
    return "█" * filled + "░" * (length - filled)


def run_ffmpeg_with_progress(command, duration, part):
    start_time = time.time()

    process = subprocess.Popen(
        command,
        stderr=subprocess.PIPE,
        stdout=subprocess.DEVNULL,
        text=True,
        universal_newlines=True
    )

    time_pattern = re.compile(r"time=(\d+):(\d+):(\d+\.\d+)")
    fps_pattern = re.compile(r"fps=\s*(\d+)")

    last_percent = -1
    fps_value = "0"

    while True:
        line = process.stderr.readline()

        if not line:
            break

        fps_match = fps_pattern.search(line)

        if fps_match:
            fps_value = fps_match.group(1)

        match = time_pattern.search(line)

        if match:
            h, m, s = match.groups()

            current_progress_time = (
                int(h) * 3600 +
                int(m) * 60 +
                float(s)
            )

            percent = min(
                100,
                int((current_progress_time / duration) * 100)
            )

            if percent != last_percent:
                elapsed = time.time() - start_time

                eta = (
                    (elapsed / percent) * (100 - percent)
                    if percent > 0 else 0
                )

                eta_str = time.strftime("%M:%S", time.gmtime(eta))
                bar = progress_bar(percent)
                jam = get_jakarta_time()

                print(
                    f"\r🕒 {jam} | "
                    f"PART {part} | "
                    f"{bar} {percent}% | "
                    f"⚡ {fps_value} FPS | "
                    f"⏱️ ETA {eta_str}",
                    end=""
                )

                last_percent = percent

    process.wait()
    print()

    return process.returncode


# =========================
# EMBED THUMBNAIL
# =========================

def embed_thumbnail(video_path):
    if not cfg("USE_EMBED_THUMBNAIL", True):
        return video_path

    thumb_path = cfg("THUMBNAIL_PATH", "assets/thumbnail.jpg")

    if not os.path.exists(thumb_path):
        print("⚠️ Thumbnail tidak ditemukan, skip.")
        return video_path

    temp_path = video_path.replace(".mp4", "_thumb.mp4")

    cmd = [
        "ffmpeg", "-y",
        "-hide_banner",
        "-loglevel", "error",
        "-i", video_path,
        "-i", thumb_path,
        "-map", "0",
        "-map", "1",
        "-c", "copy",
        "-c:v:1", "mjpeg",
        "-disposition:v:1", "attached_pic",
        "-movflags", "+faststart",
        temp_path
    ]

    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode == 0 and os.path.exists(temp_path):
        os.replace(temp_path, video_path)
        print("🖼️ Thumbnail berhasil ditanam")
    else:
        print("⚠️ Gagal tanam thumbnail")

        if result.stderr:
            print(result.stderr)

        if os.path.exists(temp_path):
            os.remove(temp_path)

    return video_path


# =========================
# MAIN CUTTER
# =========================

def process_video(filepath, judul):
    output_folder = cfg("OUTPUT_FOLDER", "cut")
    os.makedirs(output_folder, exist_ok=True)

    info = get_video_info(filepath)
    print_video_info(filepath, info)

    total_duration = int(info["duration"])

    current_time = 0
    part = 1
    outputs = []

    filename = os.path.splitext(os.path.basename(filepath))[0]
    judul = judul.title()

    # =========================
    # AUTO WRAP TITLE
    # =========================

    max_lines = 6

    wrapped_lines = textwrap.wrap(
        judul,
        width=24
    )

    if len(wrapped_lines) > max_lines:
        wrapped_lines = wrapped_lines[:max_lines]
        wrapped_lines[-1] += "..."

    line_count = len(wrapped_lines)

    # =========================
    # DYNAMIC FONT SIZE
    # =========================

    if line_count <= 2:
        dynamic_fontsize = config.FONT_SIZE
    elif line_count <= 4:
        dynamic_fontsize = int(config.FONT_SIZE * 0.85)
    else:
        dynamic_fontsize = int(config.FONT_SIZE * 0.72)

    # =========================
    # TEXT POSITION
    # =========================

    start_y = 0.10
    line_spacing = dynamic_fontsize + 12

    # =========================
    # STYLE FROM CONFIG
    # =========================

    bg_color = cfg("BG_COLOR", "black")
    font_color = cfg("FONT_COLOR", "white")
    part_font_color = cfg("PART_FONT_COLOR", "white")
    border_color = cfg("BORDER_COLOR", "black")
    shadow_color = cfg("SHADOW_COLOR", "black")

    # =========================
    # LOGO TOP
    # =========================

    logo_top_path = cfg("LOGO_TOP_PATH", "assets/logo_top.jpg")
    use_logo_top = os.path.exists(logo_top_path)

    # =========================
    # PROCESS LOOP
    # =========================

    while current_time < total_duration:
        duration = random.randint(
            config.MIN_DURATION,
            config.MAX_DURATION
        )

        remaining = total_duration - current_time

        if remaining <= config.MIN_DURATION:
            duration = remaining
        elif remaining < duration:
            duration = remaining

        if duration <= 0:
            break

        duration = int(duration)
        end_time = current_time + duration

        output_path = os.path.join(
            output_folder,
            f"cut_{part}_{filename}.mp4"
        )

        text_part = f"PART {part}"

        # =========================
        # TITLE DRAWTEXT
        # =========================

        drawtext_lines = []

        for i, line in enumerate(wrapped_lines):
            safe_line = escape_text(line)

            y_pos = (
                f"h*{start_y}+"
                f"{i * line_spacing}"
            )

            drawtext_lines.append(
                f"drawtext="
                f"fontfile={config.FONT_PATH}:"
                f"text='{safe_line}':"
                f"fontcolor={font_color}:"
                f"fontsize={dynamic_fontsize}:"
                f"x=(w-text_w)/2:"
                f"y={y_pos}:"
                f"borderw=2:"
                f"bordercolor={border_color}:"
                f"shadowcolor={shadow_color}:"
                f"shadowx=2:"
                f"shadowy=2"
            )

        judul_drawtext = ",".join(drawtext_lines)

        # =========================
        # PART DRAWTEXT
        # =========================

        drawtext = (
            judul_drawtext +
            "," +
            f"drawtext="
            f"fontfile={config.FONT_PATH}:"
            f"text='{text_part}':"
            f"fontcolor={part_font_color}:"
            f"fontsize={config.FONT_SIZE_PART}:"
            f"x=(w-text_w)/2:"
            f"y=h*0.82:"
            f"borderw=2:"
            f"bordercolor={border_color}:"
            f"shadowcolor={shadow_color}:"
            f"shadowx=2:"
            f"shadowy=2"
        )

        # =========================
        # EXTRA LOGO TOP
        # =========================

        extra_overlay = ""
        base_label = "[base]"

        if use_logo_top:
            extra_overlay = (
                f"[2:v]"
                f"scale=120:-1,"
                f"format=rgba,"
                f"colorchannelmixer=aa=0.8[wm2];"

                f"[base][wm2]"
                f"overlay=W-w-40:40[tmp1];"
            )

            base_label = "[tmp1]"

        # =========================
        # VIDEO FILTER
        # Output 720x1280
        # Video utama 720x720 di tengah
        # Background full dari BG_COLOR
        # =========================

        vf_filter = (
            f"color=c={bg_color}:s=720x1280:d={duration}[canvas];"

            f"[0:v]"
            f"trim=start={current_time}:end={end_time},"
            "setpts=PTS-STARTPTS,"
            "crop=ih:ih:(iw-ih)/2:0,"
            "scale=720:720[vclip];"

            "[canvas][vclip]"
            "overlay=0:(H-h)/2[base];"

            f"[0:a]"
            f"atrim=start={current_time}:end={end_time},"
            "asetpts=PTS-STARTPTS[aout];"

            + extra_overlay +

            f"[1:v]"
            f"scale={config.WM_SIZE}:-1,"
            "format=rgba,"
            f"colorchannelmixer=aa={config.WM_OPACITY}[wm];"

            f"{base_label}[wm]"
            f"overlay={config.WM_POS_X}:{config.WM_POS_Y},"

            + drawtext +

            "[vout]"
        )

        # =========================
        # INPUTS
        # =========================

        inputs = [
            "-i", filepath,
            "-i", "assets/logo.png"
        ]

        if use_logo_top:
            inputs += [
                "-i",
                logo_top_path
            ]

        # =========================
        # FFMPEG COMMAND
        # =========================

        command = [
            "ffmpeg",
            "-y",
            "-hide_banner",
            "-loglevel", "warning",

            *inputs,

            "-filter_complex", vf_filter,

            "-map", "[vout]",
            "-map", "[aout]",

            "-c:v", "libx264",
            "-preset", "ultrafast",
            "-crf", "28",

            "-pix_fmt", "yuv420p",
            "-profile:v", "baseline",
            "-level", "3.0",

            "-maxrate", cfg("VIDEO_BITRATE", "1500k"),
            "-bufsize", "4M",

            "-c:a", "aac",
            "-b:a", cfg("AUDIO_BITRATE", "128k"),
            "-ar", "44100",
            "-ac", "2",

            "-movflags", "+faststart",
            "-threads", "8",

            output_path
        ]

        result_code = run_ffmpeg_with_progress(
            command,
            duration,
            part
        )

        if result_code != 0:
            print(f"❌ PART {part} gagal")

        elif (
            os.path.exists(output_path)
            and os.path.getsize(output_path) > 1000
        ):
            embed_thumbnail(output_path)

            caption = f"{judul} - Part {part}"

            outputs.append(
                (
                    output_path,
                    caption
                )
            )

            print(
                f"✅ Part {part} berhasil "
                f"({duration} detik)"
            )

        else:
            print(f"❌ PART {part} gagal")

        current_time += duration
        part += 1

    return outputs
