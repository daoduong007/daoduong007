"""Chế độ --mode ai: Veo (Gemini API) biến ảnh cảnh thành clip chuyển động."""
import base64
import time
from pathlib import Path

from . import config
from .http import ApiError, gemini_headers, request


def generate(image, prompt, aspect, out, poll_every=10, max_wait=900):
    headers = gemini_headers(config.GEMINI_API_KEY)
    body = {
        "instances": [{
            "prompt": prompt + " Gentle, cheerful children's cartoon animation. No text.",
            "image": {"bytesBase64Encoded": base64.b64encode(Path(image).read_bytes()).decode(),
                      "mimeType": "image/png"},
        }],
        "parameters": {"aspectRatio": aspect},
    }
    url = f"{config.GEMINI_BASE_URL}/models/{config.VEO_MODEL}:predictLongRunning"
    op = request("POST", url, headers=headers, json=body).json()

    waited = 0
    while not op.get("done"):
        if waited >= max_wait:
            raise ApiError("Veo quá lâu chưa xong")
        time.sleep(poll_every)
        waited += poll_every
        op = request("GET", f"{config.GEMINI_BASE_URL}/{op['name']}", headers=headers).json()

    if "error" in op:
        raise ApiError(f"Veo báo lỗi: {op['error']}")
    try:
        uri = op["response"]["generateVideoResponse"]["generatedSamples"][0]["video"]["uri"]
    except (KeyError, IndexError) as exc:
        raise ApiError(f"Veo không trả về video (có thể bị bộ lọc an toàn chặn): {op}") from exc
    Path(out).write_bytes(request("GET", uri, headers=headers, timeout=600).content)
