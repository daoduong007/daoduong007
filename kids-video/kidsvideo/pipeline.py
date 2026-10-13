"""Chạy toàn bộ quy trình. Mỗi bước lưu kết quả vào thư mục output/<tên>/,
nên chạy lại sẽ bỏ qua phần đã xong (không tốn tiền gọi AI lần nữa)."""
import json
import shutil
import unicodedata
from pathlib import Path

from . import assemble, config, images, motion, script, tts
from .http import ApiError


def slugify(text):
    text = text.replace("đ", "d").replace("Đ", "D")
    text = unicodedata.normalize("NFD", text)
    text = "".join(c for c in text if unicodedata.category(c) != "Mn").lower()
    slug = "".join(c if c.isalnum() else "-" for c in text)
    return "-".join(filter(None, slug.split("-")))[:60] or "video"


def find_music(music):
    if music:
        return Path(music)
    folder = config.ROOT / "assets" / "music"
    files = sorted(p for p in folder.glob("*") if p.suffix.lower() in (".mp3", ".wav", ".m4a", ".ogg"))
    return files[0] if files else None


def step(msg):
    print(f"\n==> {msg}")


def load_or_write_script(topic, fmt, scenes, script_path, out_root):
    if script_path:
        story = script.parse_json(Path(script_path).read_text(encoding="utf-8"))
        out_dir = out_root / slugify(story["title"])
        out_dir.mkdir(parents=True, exist_ok=True)
        target = out_dir / "script.json"
        if Path(script_path).resolve() != target.resolve():
            shutil.copy(script_path, target)
        return story, out_dir

    out_dir = out_root / slugify(topic)
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / "script.json"
    if path.exists():
        print(f"   (dùng lại kịch bản đã có: {path})")
        return script.parse_json(path.read_text(encoding="utf-8")), out_dir

    if config.SCRIPT_PROVIDER == "manual":
        prompt_file = out_dir / "prompt.txt"
        prompt_file.write_text(script.build_prompt(topic, fmt, scenes), encoding="utf-8")
        print(f"""
   Chế độ thủ công: mở {prompt_file}
   1) Copy toàn bộ nội dung, dán vào claude.ai hoặc ChatGPT.
   2) Copy đoạn JSON AI trả lời, lưu thành {path}
   3) Chạy lại đúng lệnh vừa rồi để tiếp tục.""")
        return None, out_dir

    story = script.generate(topic, fmt, scenes)
    path.write_text(json.dumps(story, ensure_ascii=False, indent=2), encoding="utf-8")
    return story, out_dir


def write_description(story, out_dir):
    tags = "#hoathinh #truyenthieunhi #chobe #phimhoathinh #truyencotich"
    text = (f"{story['title']}\n\n{story.get('moral', '')}\n\n"
            f"Truyện hoạt hình dành cho các bé 3-6 tuổi.\n\n{tags}\n")
    (out_dir / "mo-ta-youtube.txt").write_text(text, encoding="utf-8")


def make(topic=None, fmt="short", mode="kenburns", scenes=None, script_path=None,
         music=None, out_root=None):
    assemble.check_ffmpeg()
    f = config.FORMATS[fmt]
    size, aspect = f["size"], f["aspect"]
    out_root = Path(out_root or config.ROOT / "output")

    step("1/5 Viết kịch bản")
    story, out_dir = load_or_write_script(topic, fmt, scenes, script_path, out_root)
    if story is None:
        return None
    print(f"   {story['title']} — {len(story['scenes'])} cảnh")

    img_dir, audio_dir, clip_dir = (out_dir / d for d in ("images", "audio", "clips"))
    for d in (img_dir, audio_dir, clip_dir):
        d.mkdir(exist_ok=True)

    refs = {}
    if config.IMAGE_PROVIDER == "gemini":
        step("2/5 Vẽ nhân vật mẫu (giúp nhân vật giống nhau ở mọi cảnh)")
        for i, char in enumerate(story["characters"], 1):
            path = img_dir / f"nhanvat_{i}.png"
            if not path.exists():
                print(f"   {char['name']}")
                images.generate(images.character_prompt(story, char), "1:1", path)
            refs[char["name"]] = path

    step("3/5 Vẽ từng cảnh")
    for i, scene in enumerate(story["scenes"], 1):
        path = img_dir / f"canh_{i:02}.png"
        if not path.exists():
            print(f"   Cảnh {i}/{len(story['scenes'])}")
            scene_refs = [refs[n] for n in scene.get("characters", []) if n in refs]
            images.generate(images.scene_prompt(story, scene, aspect), aspect, path, scene_refs)

    step("4/5 Đọc lời dẫn")
    audio_files = []
    for i, scene in enumerate(story["scenes"], 1):
        stem = audio_dir / f"canh_{i:02}"
        existing = [p for p in (stem.with_suffix(".mp3"), stem.with_suffix(".wav")) if p.exists()]
        audio_files.append(existing[0] if existing else tts.generate(scene["narration"], stem))

    step(f"5/5 Dựng video (chế độ {mode})")
    clips, timing = [], []
    for i, scene in enumerate(story["scenes"], 1):
        image, audio = img_dir / f"canh_{i:02}.png", audio_files[i - 1]
        clip = clip_dir / f"{mode}_{fmt}_canh_{i:02}.mp4"
        if not clip.exists():
            print(f"   Cảnh {i}/{len(story['scenes'])}")
            ai_video = clip_dir / f"veo_canh_{i:02}.mp4"
            if mode == "ai" and not ai_video.exists():
                try:
                    print("     Veo đang tạo chuyển động (1-5 phút)...")
                    motion.generate(image, scene["motion_prompt"], aspect, ai_video)
                except ApiError as exc:
                    print(f"     ! Veo lỗi, dùng zoom/lia cho cảnh này: {exc}")
            if mode == "ai" and ai_video.exists():
                assemble.video_clip(ai_video, audio, clip, size)
            else:
                assemble.kenburns_clip(image, audio, clip, size, i - 1)
        clips.append(clip)
        timing.append((scene["narration"], assemble.duration(audio), assemble.duration(clip)))

    srt = out_dir / "phude.srt"
    assemble.write_srt(timing, srt, max_words=7 if fmt == "short" else 10)
    final = out_dir / f"{slugify(story['title'])}_{fmt}_{mode}.mp4"
    music_file = find_music(music)
    if music_file:
        print(f"   Nhạc nền: {music_file.name}")
    assemble.final(clips, srt, final, size, music_file)
    write_description(story, out_dir)
    print(f"\nXONG! Video: {final}")
    return final
