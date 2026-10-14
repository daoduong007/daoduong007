"""Bước 2: AI vẽ ảnh nhân vật mẫu và ảnh từng cảnh."""
import base64
import random
import urllib.parse
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from . import config
from .http import ApiError, gemini_headers, request

NO_TEXT = "No text, no letters, no watermark. Safe and friendly for young children."


def character_prompt(story, char):
    return (f"Character reference sheet, full body, front view, plain white background. "
            f"{char['name']}: {char['appearance']}. Style: {story['style']}. {NO_TEXT}")


def scene_prompt(story, scene, aspect):
    chars = [c for c in story["characters"] if c["name"] in scene.get("characters", [])]
    desc = " ".join(f"{c['name']} is {c['appearance']}." for c in chars)
    framing = "vertical portrait composition" if aspect == "9:16" else "wide landscape composition"
    return (f"{scene['image_prompt']} {desc} Style: {story['style']}. "
            f"Keep each character exactly as in the reference images. {framing}. {NO_TEXT}")


def _gemini(prompt, aspect, refs, out):
    parts = [{"text": prompt}]
    for ref in refs:
        parts.append({"inline_data": {"mime_type": "image/png",
                                      "data": base64.b64encode(Path(ref).read_bytes()).decode()}})
    body = {"contents": [{"parts": parts}],
            "generationConfig": {"responseModalities": ["IMAGE"],
                                 "imageConfig": {"aspectRatio": aspect}}}
    url = f"{config.GEMINI_BASE_URL}/models/{config.GEMINI_IMAGE_MODEL}:generateContent"
    resp = request("POST", url, headers=gemini_headers(config.GEMINI_API_KEY), json=body)
    for cand in resp.json().get("candidates", []):
        for part in cand.get("content", {}).get("parts", []):
            blob = part.get("inlineData") or part.get("inline_data")
            if blob:
                _save(base64.b64decode(blob["data"]), out)
                return
    raise ApiError("Gemini không trả về ảnh (có thể prompt bị chặn): " + resp.text[:300])


def _openai(prompt, aspect, out):
    size = "1024x1536" if aspect == "9:16" else "1536x1024" if aspect == "16:9" else "1024x1024"
    headers = {"Content-Type": "application/json"}
    if config.OPENAI_API_KEY:
        headers["Authorization"] = f"Bearer {config.OPENAI_API_KEY}"
    body = {"model": config.OPENAI_IMAGE_MODEL, "prompt": prompt, "size": size, "n": 1}
    resp = request("POST", f"{config.OPENAI_BASE_URL}/images/generations", headers=headers, json=body)
    item = resp.json()["data"][0]
    if item.get("b64_json"):
        _save(base64.b64decode(item["b64_json"]), out)
    else:
        _save(request("GET", item["url"]).content, out)


def _pollinations(prompt, aspect, out):
    w, h = (768, 1365) if aspect == "9:16" else (1365, 768) if aspect == "16:9" else (1024, 1024)
    url = (f"https://image.pollinations.ai/prompt/{urllib.parse.quote(prompt)}"
           f"?width={w}&height={h}&nologo=true&seed={random.randint(1, 10**6)}")
    _save(request("GET", url, timeout=300).content, out)


def _placeholder(prompt, aspect, out):
    """Ảnh giả để chạy thử miễn phí, không cần mạng."""
    w, h = (1080, 1920) if aspect == "9:16" else (1920, 1080) if aspect == "16:9" else (1024, 1024)
    color = tuple(random.randint(90, 230) for _ in range(3))
    img = Image.new("RGB", (w, h), color)
    draw = ImageDraw.Draw(img)
    for _ in range(12):
        x, y, r = random.randint(0, w), random.randint(0, h), random.randint(40, 200)
        draw.ellipse((x - r, y - r, x + r, y + r), fill=tuple(random.randint(60, 255) for _ in range(3)))
    try:
        font = ImageFont.truetype("DejaVuSans.ttf", 36)
    except OSError:
        font = ImageFont.load_default()
    draw.multiline_text((40, 40), "\n".join(prompt[i:i + 45] for i in range(0, 270, 45)),
                        fill="black", font=font)
    img.save(out)


def _save(data, out):
    tmp = Path(out).with_suffix(".tmp")
    tmp.write_bytes(data)
    Image.open(tmp).convert("RGB").save(out, "PNG")
    tmp.unlink()


def generate(prompt, aspect, out, refs=()):
    provider = config.IMAGE_PROVIDER
    if provider == "gemini":
        _gemini(prompt, aspect, refs, out)
    elif provider == "openai":
        _openai(prompt, aspect, out)
    elif provider == "pollinations":
        _pollinations(prompt, aspect, out)
    elif provider == "placeholder":
        _placeholder(prompt, aspect, out)
    else:
        raise ApiError(f"IMAGE_PROVIDER không hợp lệ: {provider}")
