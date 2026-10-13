"""Bước 1: AI viết kịch bản (JSON) từ một chủ đề."""
import json
import re

from . import config
from .http import ApiError, gemini_headers, request

PROMPT = """Bạn là biên kịch phim hoạt hình cho trẻ em 3-6 tuổi người Việt.
Hãy viết một câu chuyện hoạt hình về chủ đề: "{topic}".

Yêu cầu:
- Đúng {scenes} cảnh. Mỗi cảnh có lời dẫn tiếng Việt dài {narration}.
- Câu ngắn, từ ngữ đơn giản, ấm áp, vui tươi; có thể lặp lại câu dễ nhớ.
- Cảnh 1 phải gây tò mò ngay. Cảnh cuối nêu bài học nhẹ nhàng.
- Không có nội dung đáng sợ, bạo lực, nguy hiểm, hay nhân vật có bản quyền.
- Tối đa 3 nhân vật, mỗi nhân vật có ngoại hình cố định, dễ nhận ra.
- image_prompt và motion_prompt viết bằng TIẾNG ANH; không yêu cầu chữ viết trong ảnh.

Chỉ trả về JSON hợp lệ, không giải thích, theo đúng mẫu:
{{
  "title": "Tiêu đề tiếng Việt",
  "moral": "Bài học của truyện",
  "style": "English art style used for every scene, e.g. cute 3D animated children's movie style, soft lighting, bright pastel colors",
  "characters": [
    {{"name": "Tên nhân vật", "appearance": "English: species, size, colors, clothes, distinctive features"}}
  ],
  "scenes": [
    {{
      "narration": "Lời dẫn tiếng Việt",
      "characters": ["Tên nhân vật có mặt trong cảnh"],
      "image_prompt": "English: setting, action, expressions, camera framing",
      "motion_prompt": "English: one simple movement for an 8-second clip"
    }}
  ]
}}"""


def build_prompt(topic, fmt, scenes=None):
    f = config.FORMATS[fmt]
    return PROMPT.format(topic=topic, scenes=scenes or f["scenes"], narration=f["narration"])


def parse_json(text):
    text = text.strip()
    fenced = re.search(r"```(?:json)?\s*(.*?)```", text, re.S)
    if fenced:
        text = fenced.group(1)
    start, end = text.find("{"), text.rfind("}")
    if start < 0 or end < 0:
        raise ApiError("AI không trả về JSON. Nội dung nhận được:\n" + text[:500])
    data = json.loads(text[start:end + 1])
    validate(data)
    return data


def validate(data):
    for key in ("title", "style", "characters", "scenes"):
        if key not in data:
            raise ApiError(f"Kịch bản thiếu trường '{key}'")
    for i, scene in enumerate(data["scenes"], 1):
        for key in ("narration", "image_prompt"):
            if not scene.get(key):
                raise ApiError(f"Cảnh {i} thiếu '{key}'")
        scene.setdefault("characters", [])
        scene.setdefault("motion_prompt", "gentle camera movement, characters move naturally")


def _openai(prompt):
    headers = {"Content-Type": "application/json"}
    if config.OPENAI_API_KEY:
        headers["Authorization"] = f"Bearer {config.OPENAI_API_KEY}"
    body = {"model": config.SCRIPT_MODEL, "temperature": 0.8,
            "messages": [{"role": "user", "content": prompt}]}
    resp = request("POST", f"{config.OPENAI_BASE_URL}/chat/completions", headers=headers, json=body)
    return resp.json()["choices"][0]["message"]["content"]


def _gemini(prompt):
    url = f"{config.GEMINI_BASE_URL}/models/{config.GEMINI_TEXT_MODEL}:generateContent"
    body = {"contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {"temperature": 0.8, "responseMimeType": "application/json"}}
    resp = request("POST", url, headers=gemini_headers(config.GEMINI_API_KEY), json=body)
    parts = resp.json()["candidates"][0]["content"]["parts"]
    return "".join(p.get("text", "") for p in parts)


def generate(topic, fmt, scenes=None):
    prompt = build_prompt(topic, fmt, scenes)
    provider = config.SCRIPT_PROVIDER
    if provider == "openai":
        text = _openai(prompt)
    elif provider == "gemini":
        text = _gemini(prompt)
    else:
        raise ApiError(f"SCRIPT_PROVIDER không hợp lệ: {provider}")
    return parse_json(text)
