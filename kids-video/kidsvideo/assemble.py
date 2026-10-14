"""Bước 4: ffmpeg ghép ảnh/clip + giọng đọc + phụ đề + nhạc nền thành MP4."""
import re
import shutil
import subprocess
from pathlib import Path

from . import config

TAIL = 0.8  # giây nghỉ sau lời dẫn mỗi cảnh


def check_ffmpeg():
    if not shutil.which("ffmpeg") or not shutil.which("ffprobe"):
        raise SystemExit("Chưa cài ffmpeg. Xem mục 'Cài đặt' trong README.md")


def run(cmd, cwd=None):
    proc = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, encoding="utf-8", errors="replace")
    if proc.returncode != 0:
        raise RuntimeError("ffmpeg lỗi:\n" + proc.stderr[-2000:])


def duration(path):
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                          "-of", "default=nw=1:nk=1", str(path)], capture_output=True, text=True)
    return float(out.stdout.strip())


def _encode_args(dur):
    return ["-c:v", "libx264", "-preset", "veryfast", "-crf", "20", "-pix_fmt", "yuv420p",
            "-r", str(config.FPS), "-c:a", "aac", "-b:a", "160k", "-ar", "44100", "-ac", "2",
            "-t", f"{dur:.3f}"]


def kenburns_clip(image, audio, out, size, index):
    w, h = size
    dur = duration(audio) + TAIL
    frames = int(dur * config.FPS)
    s = config.KENBURNS_SCALE
    # Xen kẽ các kiểu chuyển động để video đỡ đơn điệu.
    zoom, x, y = [
        ("1+0.20*on/{n}", "iw/2-(iw/zoom/2)", "ih/2-(ih/zoom/2)"),            # zoom vào
        ("1.20-0.20*on/{n}", "iw/2-(iw/zoom/2)", "ih/2-(ih/zoom/2)"),         # zoom ra
        ("1.15", "(iw-iw/zoom)*on/{n}", "ih/2-(ih/zoom/2)"),                  # lia sang phải
        ("1.15", "(iw-iw/zoom)*(1-on/{n})", "ih/2-(ih/zoom/2)"),              # lia sang trái
    ][index % 4]
    n = max(frames - 1, 1)
    vf = (f"scale={int(w * s)}:{int(h * s)}:force_original_aspect_ratio=increase,"
          f"crop={int(w * s)}:{int(h * s)},"
          f"zoompan=z='{zoom.format(n=n)}':x='{x.format(n=n)}':y='{y.format(n=n)}'"
          f":d={frames}:s={w}x{h}:fps={config.FPS},setsar=1")
    run(["ffmpeg", "-y", "-i", str(image), "-i", str(audio),
         "-filter_complex", f"[0:v]{vf}[v];[1:a]apad[a]", "-map", "[v]", "-map", "[a]",
         *_encode_args(dur), str(out)])


def video_clip(video, audio, out, size):
    """Dùng clip AI; nếu lời dẫn dài hơn clip thì giữ khung hình cuối."""
    w, h = size
    dur = duration(audio) + TAIL
    vf = (f"scale={w}:{h}:force_original_aspect_ratio=increase,crop={w}:{h},fps={config.FPS},"
          f"tpad=stop_mode=clone:stop_duration={dur:.3f},trim=duration={dur:.3f},"
          f"setpts=PTS-STARTPTS,setsar=1")
    run(["ffmpeg", "-y", "-i", str(video), "-i", str(audio),
         "-filter_complex", f"[0:v]{vf}[v];[1:a]apad[a]", "-map", "[v]", "-map", "[a]",
         *_encode_args(dur), str(out)])


def _chunks(text, max_words=10):
    """Chia lời dẫn thành các dòng phụ đề ngắn."""
    sentences = [s.strip() for s in re.split(r"(?<=[.!?…])\s+", text) if s.strip()]
    lines = []
    for sentence in sentences:
        words = sentence.split()
        while len(words) > max_words:
            cut = max_words
            for i in range(max_words, max_words // 2, -1):  # ưu tiên ngắt ở dấu phẩy
                if words[i - 1].endswith(","):
                    cut = i
                    break
            lines.append(" ".join(words[:cut]))
            words = words[cut:]
        if words:
            lines.append(" ".join(words))
    return lines


def _ts(sec):
    ms = int(round(sec * 1000))
    return f"{ms // 3600000:02}:{ms // 60000 % 60:02}:{ms // 1000 % 60:02},{ms % 1000:03}"


def write_srt(scenes, out, max_words):
    """scenes: list (lời dẫn, độ dài giọng đọc, độ dài clip)."""
    entries, start = [], 0.0
    for narration, speech, clip in scenes:
        lines = _chunks(narration, max_words)
        total = sum(len(line) for line in lines) or 1
        t = start
        for line in lines:
            d = speech * len(line) / total
            entries.append((t, t + d, line))
            t += d
        start += clip
    with open(out, "w", encoding="utf-8") as f:
        for i, (a, b, line) in enumerate(entries, 1):
            f.write(f"{i}\n{_ts(a)} --> {_ts(b)}\n{line}\n\n")


def final(clips, srt, out, size, music=None, music_volume=0.12):
    workdir = Path(out).parent
    listfile = workdir / "clips.txt"
    listfile.write_text("".join(f"file '{Path(c).resolve().as_posix()}'\n" for c in clips), encoding="utf-8")
    joined = workdir / "joined.mp4"
    run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(listfile), "-c", "copy", str(joined)])

    vertical = size[1] > size[0]
    style = (f"FontName={config.SUBTITLE_FONT},FontSize={10 if vertical else 18},Bold=1,"
             f"PrimaryColour=&H00FFFFFF,OutlineColour=&H00000000,BorderStyle=1,Outline=2,Shadow=1,"
             f"Alignment=2,MarginV={60 if vertical else 25}")
    # Chạy trong thư mục output để tránh lỗi đường dẫn Windows trong bộ lọc subtitles.
    cmd = ["ffmpeg", "-y", "-i", joined.name]
    filters = f"[0:v]subtitles={Path(srt).name}:force_style='{style}'[v]"
    if music:
        cmd += ["-stream_loop", "-1", "-i", str(Path(music).resolve())]
        filters += (f";[1:a]volume={music_volume}[m];"
                    f"[0:a][m]amix=inputs=2:duration=first:dropout_transition=0:normalize=0[a]")
        amap = "[a]"
    else:
        amap = "0:a"
    cmd += ["-filter_complex", filters, "-map", "[v]", "-map", amap,
            "-c:v", "libx264", "-preset", "medium", "-crf", "20", "-pix_fmt", "yuv420p",
            "-c:a", "aac", "-b:a", "160k", "-movflags", "+faststart", Path(out).name]
    run(cmd, cwd=workdir)
    joined.unlink(missing_ok=True)
    listfile.unlink(missing_ok=True)
