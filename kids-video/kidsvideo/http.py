"""Gọi HTTP có thử lại khi bị giới hạn tốc độ hoặc lỗi máy chủ."""
import time

import requests


class ApiError(RuntimeError):
    pass


def request(method, url, retries=4, timeout=180, **kwargs):
    for attempt in range(retries):
        try:
            resp = requests.request(method, url, timeout=timeout, **kwargs)
        except requests.RequestException as exc:
            if attempt == retries - 1:
                raise ApiError(f"Không kết nối được {url}: {exc}") from exc
            time.sleep(2 ** (attempt + 1))
            continue
        if resp.status_code in (429, 500, 502, 503, 504) and attempt < retries - 1:
            wait = 2 ** (attempt + 2)
            print(f"   ! {resp.status_code} từ máy chủ, thử lại sau {wait}s...")
            time.sleep(wait)
            continue
        if resp.status_code >= 400:
            raise ApiError(f"{resp.status_code} từ {url.split('?')[0]}: {resp.text[:500]}")
        return resp
    raise ApiError(f"Thất bại sau {retries} lần thử: {url}")


def gemini_headers(api_key):
    if not api_key:
        raise ApiError("Thiếu GEMINI_API_KEY trong file .env")
    return {"x-goog-api-key": api_key, "Content-Type": "application/json"}
