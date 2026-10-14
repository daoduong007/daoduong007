"""Tạo video hoạt hình thiếu nhi tự động bằng AI.

Ví dụ:
  python make_video.py "Chú thỏ học cách chia sẻ"
  python make_video.py "Gấu con sợ bóng tối" --format long --mode ai
  python make_video.py --batch topics.txt --format short
  python make_video.py --script output/xxx/script.json
"""
import argparse
import sys
import traceback
from pathlib import Path

from kidsvideo import pipeline
from kidsvideo.http import ApiError


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")  # để Windows in được tiếng Việt

    p = argparse.ArgumentParser(description="Tạo video hoạt hình thiếu nhi bằng AI")
    p.add_argument("topic", nargs="?", help="Chủ đề câu chuyện")
    p.add_argument("--format", choices=["short", "long"], default="short",
                   help="short = dọc 9:16 (~1 phút), long = ngang 16:9 (~8-10 phút)")
    p.add_argument("--mode", choices=["kenburns", "ai"], default="kenburns",
                   help="kenburns = ảnh + zoom/lia (rẻ), ai = Veo tạo chuyển động thật (đắt)")
    p.add_argument("--scenes", type=int, help="Số cảnh (mặc định: short 6, long 24)")
    p.add_argument("--script", help="Dùng file kịch bản JSON có sẵn")
    p.add_argument("--batch", help="File .txt, mỗi dòng một chủ đề")
    p.add_argument("--music", help="File nhạc nền (mặc định lấy file đầu tiên trong assets/music)")
    args = p.parse_args()

    if args.batch:
        topics = [t.strip() for t in Path(args.batch).read_text(encoding="utf-8").splitlines()
                  if t.strip() and not t.startswith("#")]
    elif args.topic or args.script:
        topics = [args.topic]
    else:
        p.error("Cần nhập chủ đề, --script hoặc --batch")

    failed = []
    for topic in topics:
        try:
            pipeline.make(topic, args.format, args.mode, args.scenes, args.script, args.music)
        except (ApiError, RuntimeError) as exc:
            print(f"\nLỖI ({topic}): {exc}")
            print("Sửa lỗi rồi chạy lại đúng lệnh cũ, các bước đã xong sẽ được bỏ qua.")
            failed.append(topic)
        except Exception:
            traceback.print_exc()
            failed.append(topic)
    if failed:
        sys.exit(1)


if __name__ == "__main__":
    main()
