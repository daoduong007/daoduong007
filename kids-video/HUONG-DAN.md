# Hướng dẫn từng bước: làm video hoạt hình thiếu nhi bằng AI

Tài liệu này dành cho người chưa quen lập trình. Bạn chỉ cần làm theo đúng thứ tự.
Phần cài đặt chỉ làm **một lần**, mất khoảng 20-30 phút. Sau đó mỗi video chỉ cần **một lệnh**.

Mục lục:
1. [Cài phần mềm cần thiết](#1-cài-phần-mềm-cần-thiết)
2. [Tải chương trình về máy](#2-tải-chương-trình-về-máy)
3. [Lấy API key](#3-lấy-api-key)
4. [Điền cấu hình vào file .env](#4-điền-cấu-hình-vào-file-env)
5. [Chạy thử miễn phí](#5-chạy-thử-miễn-phí)
6. [Làm video thật](#6-làm-video-thật)
7. [Sửa video chưa ưng ý](#7-sửa-video-chưa-ưng-ý)
8. [Đăng lên YouTube / TikTok](#8-đăng-lên-youtube--tiktok)
9. [Gặp lỗi thì làm gì](#9-gặp-lỗi-thì-làm-gì)

---

## 1. Cài phần mềm cần thiết

Bạn cần 3 phần mềm: **Python**, **ffmpeg** và **Git**.

### Windows

1. **Python**
   - Vào <https://www.python.org/downloads/> và bấm nút tải bản mới nhất.
   - Mở file vừa tải. **Quan trọng:** tick ô **"Add python.exe to PATH"** ở màn hình đầu tiên, rồi bấm *Install Now*.
2. **ffmpeg và Git**
   - Bấm phím Windows, gõ `PowerShell` rồi mở lên.
   - Gõ từng lệnh, gõ xong mỗi lệnh thì Enter:
     ```
     winget install ffmpeg
     winget install Git.Git
     ```
3. **Đóng PowerShell rồi mở lại**, sau đó kiểm tra:
   ```
   python --version
   ffmpeg -version
   git --version
   ```
   Cả 3 lệnh đều in ra số phiên bản là được. Nếu báo "không nhận ra lệnh", hãy khởi động lại máy rồi thử lại.

### macOS

Mở **Terminal** rồi chạy:
```
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
brew install python ffmpeg git
```
Dòng đầu tiên cài Homebrew. Nếu máy đã có Homebrew thì bỏ qua dòng này.

> Từ đây trở đi, "mở terminal" nghĩa là mở **PowerShell** trên Windows hoặc **Terminal** trên macOS.

---

## 2. Tải chương trình về máy

Trong terminal, chạy lần lượt:
```
cd Desktop
git clone -b claude/animated-video-kids-wnf32s https://github.com/daoduong007/daoduong007.git
cd daoduong007/kids-video
pip install -r requirements.txt
```

Bây giờ trên Desktop có thư mục `daoduong007/kids-video`. Mọi lệnh ở các bước sau đều chạy **trong thư mục này**.
Lần sau mở terminal, bạn chỉ cần gõ:
```
cd Desktop/daoduong007/kids-video
```

---

## 3. Lấy API key

API key là "chìa khóa" để chương trình được dùng dịch vụ AI thay cho bạn. **Không chia sẻ key cho ai.**

### Key Gemini (bắt buộc nếu muốn ảnh đẹp hoặc video Veo)

1. Vào <https://aistudio.google.com/apikey> và đăng nhập bằng tài khoản Google.
2. Bấm **Create API key** rồi copy chuỗi bắt đầu bằng `AIza...`.
3. Tạo ảnh và đặc biệt là Veo thường **cần bật thanh toán** (Billing) cho key.
   - Trong AI Studio, mở mục *Billing* hoặc *Usage* để xem giá và hạn mức.
   - Nên đặt giới hạn chi tiêu để tránh tốn tiền ngoài ý muốn.

### 9router (để AI viết kịch bản)

1. Mở bảng điều khiển 9router của bạn.
2. Ghi lại 3 thông tin:
   - **Địa chỉ endpoint**, thường có dạng `http://localhost:20128/v1`
   - **API key** của 9router, nếu có
   - **Tên model** muốn dùng, ví dụ `gemini-2.5-flash`. Nếu đã nối 9router với tài khoản Claude, bạn có thể chọn model Claude.
3. Khi làm video, **9router phải đang chạy**.

### Không muốn dùng API cho kịch bản?

Gói Claude Pro và ChatGPT Plus không có API. Bạn vẫn dùng được chúng theo cách thủ công, xem [mục 6.4](#64-tự-viết-kịch-bản-bằng-claudeai-chế-độ-manual).

---

## 4. Điền cấu hình vào file .env

1. Trong thư mục `kids-video`, copy file `.env.example` rồi đổi tên bản copy thành `.env`.
   - Windows: nếu không thấy đuôi file, mở File Explorer, vào *View* và bật *File name extensions*.
   - Hoặc chạy lệnh: `copy .env.example .env` (Windows) / `cp .env.example .env` (macOS).
2. Mở `.env` bằng Notepad hoặc VS Code rồi sửa các dòng sau:

```
SCRIPT_PROVIDER=openai
OPENAI_BASE_URL=http://localhost:20128/v1     ← địa chỉ 9router của bạn
OPENAI_API_KEY=key-cua-9router                ← để trống nếu 9router không cần key
SCRIPT_MODEL=gemini-2.5-flash                 ← tên model trong 9router

GEMINI_API_KEY=AIza...                        ← key Gemini ở bước 3

IMAGE_PROVIDER=gemini
TTS_PROVIDER=edge
```

3. Lưu file. Không để dấu cách thừa hai bên dấu `=`.

### Chọn cấu hình theo ngân sách

| Mục tiêu | Thiết lập |
|---|---|
| **Miễn phí hoàn toàn** | `IMAGE_PROVIDER=pollinations`, `TTS_PROVIDER=edge`, chạy `--mode kenburns`. Nhân vật có thể hơi khác nhau giữa các cảnh. |
| **Rẻ mà đẹp** (khuyên dùng) | `IMAGE_PROVIDER=gemini`, `TTS_PROVIDER=edge`, chạy `--mode kenburns` |
| **Đẹp nhất** | `IMAGE_PROVIDER=gemini`, `TTS_PROVIDER=gemini`, chạy `--mode ai`. Nên thử với video short trước. |

### Đổi giọng đọc

| Giọng | Thiết lập |
|---|---|
| Nữ (mặc định) | `EDGE_VOICE=vi-VN-HoaiMyNeural` |
| Nam | `EDGE_VOICE=vi-VN-NamMinhNeural` |
| Đọc chậm hơn | `EDGE_RATE=-20%` |
| Đọc nhanh hơn | `EDGE_RATE=+0%` |

---

## 5. Chạy thử miễn phí

Lần chạy này không gọi AI, không tốn tiền, chỉ để kiểm tra máy đã cài đúng. Nó dùng kịch bản mẫu có sẵn và ảnh giả. Vẫn cần mạng để tạo giọng đọc.

**Windows (PowerShell):**
```
$env:IMAGE_PROVIDER="placeholder"; python make_video.py --script examples/tho-bong-chia-se.json
```

**macOS:**
```
IMAGE_PROVIDER=placeholder python make_video.py --script examples/tho-bong-chia-se.json
```

Nếu thấy dòng `XONG! Video: ...` thì mở thư mục `output/tho-bong-hoc-cach-chia-se/` để xem video. Ảnh là các hình tròn màu là bình thường, vì đây là ảnh giả.

Sau đó **xoá thư mục `output/`** để lần sau AI vẽ ảnh thật. Trên PowerShell, nếu vẫn còn biến tạm thì đóng rồi mở lại cửa sổ.

---

## 6. Làm video thật

### 6.1. Video short (dọc 9:16, khoảng 1 phút)

Dùng cho YouTube Shorts, TikTok và Reels.
```
python make_video.py "Chú thỏ học cách chia sẻ"
```

### 6.2. Video dài (ngang 16:9, khoảng 8-10 phút)

```
python make_video.py "Gấu con không còn sợ bóng tối" --format long
```
Muốn dài hoặc ngắn hơn thì thêm `--scenes`, ví dụ `--scenes 36` cho khoảng 13-15 phút.

### 6.3. Chuyển động thật bằng Veo

```
python make_video.py "Vịt con học đếm" --mode ai
```
- Mỗi cảnh mất 1-5 phút để tạo.
- Chi phí cao hơn nhiều so với chế độ mặc định.
- Nếu Veo lỗi ở cảnh nào, cảnh đó tự chuyển sang dạng zoom/lia ảnh.

### 6.4. Tự viết kịch bản bằng claude.ai (chế độ manual)

Cách này dùng gói Claude Pro hoặc ChatGPT Plus thay cho API.

1. Trong `.env`, đặt `SCRIPT_PROVIDER=manual`.
2. Chạy lệnh như bình thường:
   ```
   python make_video.py "Chú thỏ học cách chia sẻ"
   ```
3. Chương trình dừng lại và báo đường dẫn file `prompt.txt`. Mở file đó, copy toàn bộ nội dung rồi dán vào claude.ai.
4. Copy phần JSON Claude trả lời, bắt đầu bằng `{` và kết thúc bằng `}`. Dán vào một file mới tên `script.json` **trong cùng thư mục** với `prompt.txt`.
5. Chạy lại **đúng lệnh ở bước 2**. Chương trình sẽ tự làm tiếp các bước còn lại.

### 6.5. Làm nhiều video một lúc

1. Mở file `topics.txt` và viết mỗi dòng một chủ đề:
   ```
   Chú thỏ học cách chia sẻ
   Gấu con không còn sợ bóng tối
   Bé Mèo đánh răng mỗi tối
   ```
2. Chạy:
   ```
   python make_video.py --batch topics.txt
   ```
   Có thể thêm `--format long` hoặc `--mode ai`.
3. Có thể để máy chạy qua đêm. Nếu một chủ đề bị lỗi, chương trình vẫn làm tiếp các chủ đề khác.

### 6.6. Thêm nhạc nền

- Chép một file nhạc `.mp3` không bản quyền vào thư mục `assets/music/`. Chương trình tự dùng file đầu tiên và vặn nhỏ âm lượng.
- Nguồn nhạc: YouTube Studio có mục *Audio Library* miễn phí, hoặc tạo nhạc bằng Suno.
- Muốn dùng một bài khác cho video cụ thể: thêm `--music duong/dan/bai-hat.mp3` vào lệnh.

### 6.7. Tạo chuyển động bằng Flow (dùng gói Google AI Pro, không tốn tiền API)

Gói Google AI Pro cho dùng Veo trên web **Flow** (<https://labs.google/flow>) bằng credit hằng tháng. Gói này không gồm Gemini API, nên bạn tạo clip trên Flow bằng tay rồi đưa vào chương trình để ghép.

1. **Làm video bình thường trước** (chế độ mặc định) để có kịch bản, ảnh và giọng đọc:
   ```
   python make_video.py "Chú thỏ học cách chia sẻ"
   ```
2. **Xem mô tả chuyển động từng cảnh.** Mở `script.json` và tìm dòng `motion_prompt` của từng cảnh. Hoặc chạy lệnh này để in ra hết:
   ```
   python -c "import json,sys; [print(f'Cảnh {i:02}: {s[\"motion_prompt\"]}') for i,s in enumerate(json.load(open(sys.argv[1]))['scenes'],1)]" output/chu-tho-hoc-cach-chia-se/script.json
   ```
3. **Tạo clip trên Flow, làm từng cảnh một:**
   - Mở <https://labs.google/flow>, tạo project mới.
   - Chọn chế độ **Frames to Video** (tạo video từ ảnh) và tải lên ảnh `images/canh_01.png`.
   - Chọn đúng khung hình: **9:16** (dọc) cho video short, **16:9** (ngang) cho video dài.
   - Dán `motion_prompt` của cảnh đó, thêm vào cuối: `Gentle, cheerful children's cartoon animation. No text.`
   - Chọn model **Veo 3.1 Fast** hoặc **Lite** cho đỡ tốn credit. Quality đắt gấp 5-10 lần.
   - Bấm tạo. Ưng ý thì bấm **Download** và chọn MP4.
4. **Đổi tên và chép clip** vào thư mục `clips/` của video, đúng tên sau:
   ```
   output/chu-tho-hoc-cach-chia-se/clips/veo_canh_01.mp4
   output/chu-tho-hoc-cach-chia-se/clips/veo_canh_02.mp4
   ...
   ```
   Số cảnh luôn có 2 chữ số: `01`, `02`... `10`, `11`.
5. **Xoá các clip zoom/lia cũ** trong `clips/`, tức là các file bắt đầu bằng `kenburns_` hoặc `ai_`. Chỉ giữ lại `veo_canh_XX.mp4`.
6. **Ghép video:**
   ```
   python make_video.py "Chú thỏ học cách chia sẻ" --mode ai
   ```
   Video mới có tên kết thúc bằng `_short_ai.mp4`.

Lưu ý:
- **Phải có đủ clip cho mọi cảnh.** Cảnh nào thiếu `veo_canh_XX.mp4`, chương trình sẽ tự gọi Veo API. Nếu key `AIza` hợp lệ và đã bật Billing thì **sẽ bị tính tiền** cho cảnh đó. Nếu không có key, cảnh đó tự chuyển sang zoom/lia.
- Không cần lo clip dài hay ngắn. Tiếng trong clip Flow bị bỏ, chỉ giữ giọng đọc. Lời dẫn dài hơn clip thì khung hình cuối được giữ lại cho đủ.
- Credit Flow (tham khảo, có thể thay đổi): mỗi tài khoản có khoảng 50 credit/ngày, gói AI Pro thêm khoảng 1.000 credit/tháng. Một clip 8 giây tốn khoảng 10 credit (Lite), 20 (Fast) hoặc 100 (Quality).

### Kết quả nằm ở đâu?

```
output/chu-tho-hoc-cach-chia-se/
├── chu-tho-..._short_kenburns.mp4   ← VIDEO HOÀN CHỈNH
├── mo-ta-youtube.txt                ← tiêu đề, mô tả, hashtag để đăng
├── script.json                      ← kịch bản (sửa được)
├── phude.srt                        ← phụ đề riêng
├── images/                          ← ảnh nhân vật và từng cảnh
├── audio/                           ← giọng đọc từng cảnh
└── clips/                           ← clip từng cảnh
```

---

## 7. Sửa video chưa ưng ý

Chương trình **nhớ các bước đã xong**: chạy lại lệnh cũ thì chỉ làm lại phần còn thiếu, không tốn tiền gọi lại AI. Vì vậy muốn sửa phần nào, bạn **xoá file của phần đó** rồi chạy lại đúng lệnh cũ.

| Muốn sửa | Xoá những gì |
|---|---|
| Ảnh cảnh 3 xấu | `images/canh_03.png` và các file `clips/*canh_03*` |
| Nhân vật vẽ chưa đẹp, muốn vẽ lại cả bộ | Toàn bộ thư mục `images/` và `clips/` |
| Đổi lời dẫn | Sửa `narration` trong `script.json`, rồi xoá `audio/` và `clips/` |
| Đổi nội dung ảnh một cảnh | Sửa `image_prompt` của cảnh đó trong `script.json`, rồi xoá ảnh và clip của cảnh đó |
| Đổi giọng đọc | Sửa `.env`, rồi xoá `audio/` và `clips/` |
| Viết lại toàn bộ câu chuyện | Xoá cả thư mục của video trong `output/` |
| Làm thêm bản dọc từ video dài | Chạy lại với `--format short`. Kịch bản, ảnh và giọng được dùng lại. |

> Mẹo: sửa `script.json` bằng VS Code hoặc Notepad, giữ nguyên dấu ngoặc kép `"` và dấu phẩy để file không bị hỏng.

---

## 8. Đăng lên YouTube / TikTok

1. **Xem lại toàn bộ video trước khi đăng.** AI đôi khi vẽ sai tay chân, thêm chữ lạ, hoặc nhân vật bị lệch.
2. Mở `mo-ta-youtube.txt` để copy tiêu đề, mô tả và hashtag.
3. Trên YouTube:
   - Chọn **"Có, nội dung này dành cho trẻ em"**. Đây là quy định bắt buộc (COPPA).
   - Ở mục *Altered or synthetic content*, khai báo nếu được hỏi.
   - Video short dưới 3 phút, khung dọc, sẽ tự vào mục Shorts.
4. Nên làm ảnh thumbnail riêng cho video dài. Có thể dùng ảnh trong thư mục `images/` rồi thêm chữ bằng Canva.

**Mẹo để kênh phát triển:**
- Đăng đều đặn, ví dụ mỗi ngày 1 short và mỗi tuần 1 video dài.
- Giữ cùng một nhân vật qua nhiều tập để làm thành series. Chỉ cần dùng lại phần `characters` và `style` trong `script.json`.
- Chủ đề trẻ hay xem: thói quen tốt (đánh răng, ngủ sớm), học đếm, học màu, cảm xúc, an toàn, truyện cổ tích Việt Nam.

---

## 9. Gặp lỗi thì làm gì

Đọc dòng `LỖI ...` cuối cùng trên màn hình, rồi tra bảng dưới. Sửa xong thì **chạy lại đúng lệnh cũ**, phần đã xong sẽ không bị làm lại.

| Thông báo lỗi | Nguyên nhân | Cách sửa |
|---|---|---|
| `python không được nhận dạng` | Chưa tick "Add to PATH" | Cài lại Python, nhớ tick ô đó |
| `Chưa cài ffmpeg` | Thiếu ffmpeg | `winget install ffmpeg`, rồi mở lại terminal |
| `No module named ...` | Thiếu thư viện | `pip install -r requirements.txt` |
| `Thiếu GEMINI_API_KEY` | Chưa điền key hoặc chưa có file `.env` | Xem lại bước 4 |
| `Không kết nối được http://localhost...` | 9router chưa chạy | Bật 9router, kiểm tra địa chỉ trong `.env` |
| `401` hoặc `403` | Key sai, hoặc model cần bật thanh toán | Kiểm tra key, bật Billing trong AI Studio |
| `404 ... models/...` | Tên model đã thay đổi | Xem tên mới trên AI Studio hoặc 9router, sửa trong `.env` |
| `429` | Gọi quá nhiều, hết hạn mức | Đợi vài phút rồi chạy lại |
| `AI không trả về JSON` | AI trả lời sai định dạng | Chạy lại; nếu vẫn lỗi, thử model khác hoặc dùng chế độ manual |
| `Gemini không trả về ảnh` | Prompt bị bộ lọc an toàn chặn | Sửa `image_prompt` của cảnh đó trong `script.json` cho nhẹ nhàng hơn |
| `Veo lỗi, dùng zoom/lia...` | Veo không tạo được cảnh đó | Không cần làm gì, video vẫn ra. Muốn thử lại thì xoá clip cảnh đó. |
| Dựng video rất chậm | Máy yếu | Đặt `KENBURNS_SCALE=1.5` trong `.env` |
| Phụ đề bị ô vuông, mất dấu | Font không hỗ trợ tiếng Việt | Đặt `SUBTITLE_FONT=Arial` hoặc `Segoe UI` |

Vẫn không được? Copy toàn bộ nội dung lỗi trên màn hình và gửi cho Claude để được hỗ trợ.
