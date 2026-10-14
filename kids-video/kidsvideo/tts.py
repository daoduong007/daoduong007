"""Bước 3: AI đọc lời dẫn tiếng Việt."""
import asyncio
import base64
import wave

from . import config
from .http import ApiError, gemini_headers, request


def _edge(text, out):
    import edge_tts

    tmp = out.with_suffix(".tmp.mp3")

    async def run():
        await edge_tts.Communicate(text, config.EDGE_VOICE, rate=config.EDGE_RATE).save(str(tmp))

    # Ghi ra file tạm rồi mới đổi tên, để lỗi giữa chừng không để lại file rỗng
    # khiến lần chạy sau tưởng cảnh này đã xong. Edge thỉnh thoảng lỗi mạng nên thử lại.
    for attempt in range(3):
        try:
            asyncio.run(run())
            if tmp.stat().st_size > 0:
                tmp.replace(out)
                return
        except edge_tts.exceptions.NoAudioReceived:
            if attempt == 2:
                raise
        finally:
            tmp.unlink(missing_ok=True)
    raise ApiError("Edge TTS không trả về âm thanh")


def _gemini(text, out):
    url = f"{config.GEMINI_BASE_URL}/models/{config.GEMINI_TTS_MODEL}:generateContent"
    body = {
        "contents": [{"parts": [{"text": "Đọc chậm rãi, ấm áp, vui tươi như kể chuyện cho bé nghe: " + text}]}],
        "generationConfig": {
            "responseModalities": ["AUDIO"],
            "speechConfig": {"voiceConfig": {"prebuiltVoiceConfig": {"voiceName": config.GEMINI_TTS_VOICE}}},
        },
    }
    resp = request("POST", url, headers=gemini_headers(config.GEMINI_API_KEY), json=body)
    part = resp.json()["candidates"][0]["content"]["parts"][0]
    pcm = base64.b64decode((part.get("inlineData") or part["inline_data"])["data"])
    with wave.open(str(out), "wb") as wf:  # Gemini trả về PCM 16-bit, 24kHz, mono
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(24000)
        wf.writeframes(pcm)


def generate(text, out_stem):
    """Trả về đường dẫn file âm thanh đã tạo."""
    provider = config.TTS_PROVIDER
    if provider == "edge":
        out = out_stem.with_suffix(".mp3")
        _edge(text, out)
    elif provider == "gemini":
        out = out_stem.with_suffix(".wav")
        _gemini(text, out)
    else:
        raise ApiError(f"TTS_PROVIDER không hợp lệ: {provider}")
    return out
