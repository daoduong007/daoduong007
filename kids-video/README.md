# Máy làm phim hoạt hình thiếu nhi bằng AI

Nhập một chủ đề và chạy một lệnh, chương trình sẽ tự tạo ra file MP4 hoàn chỉnh:

```
"Chú thỏ học cách chia sẻ"
   → AI viết kịch bản (tiếng Việt)
   → AI vẽ nhân vật mẫu + ảnh từng cảnh
   → AI đọc lời dẫn
   → (tuỳ chọn) Veo tạo chuyển động thật
   → ffmpeg ghép: phụ đề + nhạc nền
   → video_short.mp4 + mô tả YouTube
```

| Định dạng | Khung hình | Độ dài | Dùng cho |
|---|---|---|---|
| `--format short` | dọc 9:16 | ~40-60 giây (6 cảnh) | YouTube Shorts, TikTok, Reels |
| `--format long` | ngang 16:9 | ~8-10 phút (24 cảnh) | YouTube thường |

| Chế độ | Cách làm | Chi phí |
|---|---|---|
| `--mode kenburns` (mặc định) | Ảnh AI + zoom/lia máy mượt | Rẻ, có thể gần như miễn phí |
| `--mode ai` | Veo biến từng ảnh thành clip chuyển động | Đắt hơn nhiều, nên thử với short trước |

Ở chế độ `ai`, nếu Veo lỗi ở cảnh nào thì cảnh đó tự chuyển sang zoom/lia, video vẫn ra đủ.

---

## Cài đặt (một lần)

1. **Python 3.10+**: <https://www.python.org/downloads/>. Trên Windows nhớ tick "Add Python to PATH".
2. **ffmpeg**
   - Windows: mở PowerShell, chạy `winget install ffmpeg`
   - macOS: `brew install ffmpeg`
3. **Thư viện**: mở terminal trong thư mục `kids-video` rồi chạy:
   ```
   pip install -r requirements.txt
   ```
4. **Cấu hình**: copy `.env.example` thành `.env` rồi điền key (xem mục dưới).

## Cấu hình theo tài khoản bạn đang có

**Lưu ý:** gói Claude Pro và ChatGPT Plus **không kèm API**, nên chương trình không thể tự gọi chúng. Có 3 cách dùng:

- **9router**: đặt `SCRIPT_PROVIDER=openai`, điền `OPENAI_BASE_URL`, `OPENAI_API_KEY` và `SCRIPT_MODEL` theo bảng điều khiển 9router. Nếu bạn đã nối 9router với tài khoản Claude, có thể đặt `SCRIPT_MODEL` là model Claude để Claude viết kịch bản.
- **Gemini trực tiếp**: đặt `SCRIPT_PROVIDER=gemini`.
- **Thủ công qua Claude Pro hoặc ChatGPT Plus**: đặt `SCRIPT_PROVIDER=manual`. Chương trình tạo file `prompt.txt`, bạn dán vào claude.ai, lưu câu trả lời thành `script.json` rồi chạy lại lệnh cũ. Đây là bước làm tay duy nhất.

**Ảnh, giọng đọc và Veo** cần gọi thẳng Gemini API vì 9router thường chỉ chuyển tiếp phần chat. Lấy key tại <https://aistudio.google.com/apikey> và điền vào `GEMINI_API_KEY`. Hãy kiểm tra bảng giá và hạn mức trên Google AI Studio: tạo ảnh và đặc biệt là Veo thường cần bật thanh toán.

Cấu hình rẻ nhất:

```
SCRIPT_PROVIDER=openai      # qua 9router
IMAGE_PROVIDER=gemini       # hoặc pollinations nếu muốn miễn phí hoàn toàn
TTS_PROVIDER=edge           # miễn phí
```

## Sử dụng

```bash
# Video short, ảnh + zoom (rẻ)
python make_video.py "Chú thỏ học cách chia sẻ"

# Video dài 16:9
python make_video.py "Gấu con không còn sợ bóng tối" --format long

# Chuyển động thật bằng Veo
python make_video.py "Vịt con học đếm" --mode ai

# Làm hàng loạt: mỗi dòng trong topics.txt là một video
python make_video.py --batch topics.txt

# Dùng kịch bản có sẵn (ví dụ mẫu trong thư mục examples/)
python make_video.py --script examples/tho-bong-chia-se.json
```

Kết quả nằm trong `output/<tên-truyện>/`:
- `*_short_kenburns.mp4`: video hoàn chỉnh
- `mo-ta-youtube.txt`: tiêu đề, mô tả và hashtag để đăng
- `script.json`, `images/`, `audio/`, `clips/`, `phude.srt`: các bước trung gian

**Chạy lại không tốn thêm tiền.** Bước nào đã có file thì được bỏ qua. Muốn làm lại một phần thì chỉ cần xoá file đó:
- Không ưng ảnh cảnh 3: xoá `images/canh_03.png` và `clips/*canh_03*`, rồi chạy lại.
- Muốn sửa lời dẫn: sửa `script.json`, xoá `audio/` và `clips/`, rồi chạy lại.
- Mỗi lần chạy có thể đổi `--format` hoặc `--mode` trên cùng một kịch bản.

**Nhạc nền:** chép một file nhạc không bản quyền (`.mp3`) vào `assets/music/`. Chương trình tự lấy file đầu tiên và vặn nhỏ âm lượng, hoặc bạn chỉ định bằng `--music đường/dẫn.mp3`. Có thể lấy nhạc từ YouTube Audio Library hoặc tạo bằng Suno.

## Khi đăng YouTube

- Chọn **"Có, nội dung này dành cho trẻ em"** (quy định COPPA).
- Nếu được hỏi về nội dung tạo bằng AI có hình ảnh chân thực, hãy khai báo đúng.
- Xem lại video trước khi đăng: AI đôi khi vẽ sai tay chân hoặc nhân vật bị lệch.

## Lỗi thường gặp

| Lỗi | Cách xử lý |
|---|---|
| `Chưa cài ffmpeg` | Cài ffmpeg, rồi mở lại terminal |
| `401` / `403` | Key sai hoặc chưa bật thanh toán cho model đó |
| `429` | Hết hạn mức. Đợi một lúc rồi chạy lại lệnh cũ |
| `404 ... models/...` | Tên model đã đổi, sửa tên model trong `.env` |
| `Gemini không trả về ảnh` | Prompt bị bộ lọc chặn. Sửa `image_prompt` trong `script.json` |
| Dựng chậm | Đặt `KENBURNS_SCALE=1.5` trong `.env` |
