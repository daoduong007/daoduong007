"""Đọc cấu hình từ file .env (xem .env.example)."""
import os
from pathlib import Path

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent.parent
load_dotenv(ROOT / ".env")


def env(name, default=""):
    value = os.getenv(name, default)
    return value.strip() if isinstance(value, str) else value


# --- Viết kịch bản ---
SCRIPT_PROVIDER = env("SCRIPT_PROVIDER", "openai")  # openai | gemini | manual
OPENAI_BASE_URL = env("OPENAI_BASE_URL", "http://localhost:20128/v1").rstrip("/")
OPENAI_API_KEY = env("OPENAI_API_KEY")
SCRIPT_MODEL = env("SCRIPT_MODEL", "gemini-2.5-flash")

# --- Gemini (gọi thẳng Google) ---
GEMINI_API_KEY = env("GEMINI_API_KEY")
GEMINI_BASE_URL = env("GEMINI_BASE_URL", "https://generativelanguage.googleapis.com/v1beta").rstrip("/")
GEMINI_TEXT_MODEL = env("GEMINI_TEXT_MODEL", "gemini-2.5-flash")

# --- Tạo ảnh ---
IMAGE_PROVIDER = env("IMAGE_PROVIDER", "gemini")  # gemini | openai | pollinations | placeholder
GEMINI_IMAGE_MODEL = env("GEMINI_IMAGE_MODEL", "gemini-2.5-flash-image")
OPENAI_IMAGE_MODEL = env("OPENAI_IMAGE_MODEL", "gpt-image-1")

# --- Giọng đọc ---
TTS_PROVIDER = env("TTS_PROVIDER", "edge")  # edge | gemini
EDGE_VOICE = env("EDGE_VOICE", "vi-VN-HoaiMyNeural")
EDGE_RATE = env("EDGE_RATE", "-10%")
GEMINI_TTS_MODEL = env("GEMINI_TTS_MODEL", "gemini-2.5-flash-preview-tts")
GEMINI_TTS_VOICE = env("GEMINI_TTS_VOICE", "Kore")

# --- Video AI (chế độ --mode ai) ---
VEO_MODEL = env("VEO_MODEL", "veo-3.0-fast-generate-001")

# --- Dựng phim ---
SUBTITLE_FONT = env("SUBTITLE_FONT", "Arial")
KENBURNS_SCALE = float(env("KENBURNS_SCALE", "2"))
FPS = 30

FORMATS = {
    # khung hình, số cảnh mặc định, độ dài lời dẫn mỗi cảnh
    "short": {"size": (1080, 1920), "aspect": "9:16", "scenes": 6,
              "narration": "1-2 câu ngắn (khoảng 15-25 từ)"},
    "long": {"size": (1920, 1080), "aspect": "16:9", "scenes": 24,
             "narration": "3-4 câu (khoảng 40-60 từ)"},
}
