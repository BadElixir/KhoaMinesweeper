# Minesweeper (FastAPI + AI Solver)

Project Minesweeper backend viết bằng FastAPI, có AI solver đơn giản trong `AI.py`, và giao diện web tại `index.html`.

## Yêu cầu

- Python 3.10+

## Cài đặt

```bash
pip install -r requirements.txt
```

## Chạy ứng dụng

```bash
python main.py
```

Server mặc định chạy tại:

- `http://127.0.0.1:3210/` (UI)
- `http://127.0.0.1:3210/docs` (Swagger UI)

## API chính

| Endpoint | Method | Mô tả |
| :--- | :--- | :--- |
| `/new-game` | POST | Khởi tạo game mới với kích thước và số mìn tùy chọn. |
| `/reveal` | POST | Mở một ô tại tọa độ (row, col). |
| `/flag` | POST | Cắm hoặc gỡ cờ tại tọa độ (row, col). |
| `/state` | GET | Lấy trạng thái hiện tại của bàn cờ (đối với các ô đã mở). |
| `/ai_move` | GET | Gọi AI Solver để lấy gợi ý nước đi tiếp theo. |

## Chạy test

Test dùng `pytest`, bao phủ:

- logic game (reveal/flag/win/validate input)
- API cơ bản (`/new-game`, `/state`)
- AI solver (`flag`, `reveal`, fallback random)

Chạy toàn bộ test:

```bash
pytest -q
```

Chạy test trong thư mục `tests`:

```bash
pytest -q tests
```

Chạy mô phỏng winrate:

```bash
python tests/test_winrate_random.py
python tests/test_winrate_fixed_cases.py
```

## Chế độ Auto-Test trong `main.py`

Khi chạy:

```bash
python main.py
```

và chọn chế độ `2: Auto-Test`, chương trình sẽ:

1. Chạy trước `pytest -q tests`.
2. Sau đó chạy mô phỏng Auto-Test theo cấu hình bạn chọn.
