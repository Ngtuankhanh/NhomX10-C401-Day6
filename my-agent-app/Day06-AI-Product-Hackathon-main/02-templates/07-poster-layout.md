# Poster layout — 1 trang

Poster/slides tóm tắt trưng khi trình bày. Peer nhìn poster/slides trong lúc nghe demo.

---

## Sketch tổng thể

```
┌─────────────────────────────────────────────────────────────────┐
│                                                                 │
│           🏥  VINMEC AI TRIAGE — Gợi ý chuyên khoa              │
│                                                                 │
│   Bệnh nhân không biết khám chuyên khoa nào.                   │
│   Hiện tại: hỏi lễ tân, chờ 10 phút, chọn sai khoa = khám lại.│
│   → AI hỏi triệu chứng, gợi ý top 3 khoa phù hợp.            │
│                                                                 │
├────────────────────────────┬────────────────────────────────────┤
│                            │                                    │
│     ❌  BEFORE (hiện tại)   │      ✅  AFTER (với AI)            │
│                            │                                    │
│  ┌──────────┐              │  ┌──────────┐                      │
│  │ Bệnh nhân│              │  │ Bệnh nhân│                      │
│  └────┬─────┘              │  └────┬─────┘                      │
│       ↓                    │       ↓                            │
│  Xếp hàng lễ tân          │  Mở app / chatbot                  │
│       ↓                    │       ↓                            │
│  Mô tả triệu chứng       │  Nhập triệu chứng                  │
│  (nói miệng, dễ quên)     │  (text, có gợi ý)                  │
│       ↓                    │       ↓                            │
│  Lễ tân tra danh mục      │  AI phân tích                      │
│  (thủ công, 5-10 phút)    │  (2 giây)                          │
│       ↓                    │       ↓                            │
│  Chỉ 1 khoa               │  Top 3 khoa + confidence           │
│  (có thể sai)             │  + lý do gợi ý                     │
│       ↓                    │       ↓                            │
│  Sai → khám lại           │  User chọn hoặc                    │
│  (mất thêm 1-2 giờ)       │  hỏi lễ tân nếu chưa chắc         │
│                            │                                    │
│  📊 7 bước · 10-15 phút    │  📊 4 bước · 2 phút                │
│                            │                                    │
├────────────────────────────┴────────────────────────────────────┤
│                                                                 │
│                        💻  LIVE DEMO                             │
│                                                                 │
│   ┌─────────────────────────────────────────────────────────┐   │
│   │                                                         │   │
│   │  ┌─────────────────┐    ┌────────────────────────────┐  │   │
│   │  │ Nhập triệu chứng│    │  Kết quả AI               │  │   │
│   │  │                 │    │                            │  │   │
│   │  │ "Đau bụng dưới  │    │  1. Tiêu hóa    (78%) ●●● │  │   │
│   │  │  bên phải, sốt  │ →  │  2. Ngoại tổng  (65%) ●●  │  │   │
│   │  │  nhẹ 2 ngày"    │    │  3. Tiết niệu   (42%) ●   │  │   │
│   │  │                 │    │                            │  │   │
│   │  │ [Gửi]           │    │  ⚠ Không chắc? → Gặp lễ tân│  │   │
│   │  └─────────────────┘    └────────────────────────────┘  │   │
│   │                                                         │   │
│   │  Scan thử:  [QR CODE]   hoặc link: demo.example.com    │   │
│   │                                                         │   │
│   └─────────────────────────────────────────────────────────┘   │
│                                                                 │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│                        📊  IMPACT                                │
│                                                                 │
│   Thời gian chờ          10-15 phút ──→ 2 phút     ▼ 80%       │
│   Chọn đúng khoa         ~70% ─────────→ 85%       ▲ 15%       │
│   Cần hỏi lại lễ tân     100% ─────────→ 30%       ▼ 70%       │
│   Cost per triage         — ────────────→ $0.005    (API call)  │
│                                                                 │
├──────────────────────────────┬──────────────────────────────────┤
│                              │                                  │
│  ⚠  FAILURE MODES            │  🔄  LEARNING SIGNAL              │
│                              │                                  │
│  1. Triệu chứng mơ hồ      │  User chọn khoa nào              │
│     ("đau bụng") → gợi ý    │  sau gợi ý AI?                   │
│     quá rộng                 │       ↓                          │
│     → Hỏi thêm 1-2 câu     │  So sánh với khoa                │
│       để thu hẹp             │  thực tế khám                    │
│                              │       ↓                          │
│  2. Triệu chứng hiếm,      │  Correction signal               │
│     ngoài training data      │  → cải thiện model               │
│     → "Không đủ thông tin,  │                                  │
│       hãy gặp lễ tân"       │  📈 Càng dùng → càng chính xác   │
│                              │                                  │
└──────────────────────────────┴──────────────────────────────────┘
```

Đây là ví dụ cho track Vinmec. Nhóm **thay nội dung** theo product của mình, giữ **cấu trúc 5 phần**.

---

## 5 phần bắt buộc

| # | Phần | Mục đích | Ghi chú |
|---|------|----------|---------|
| 1 | **Tên product + problem statement** | Peer biết ngay product làm gì | 1 câu, font lớn nhất |
| 2 | **Before \| After** | So sánh flow cũ vs flow mới | 2 cột, có flow diagram + số liệu (bước, thời gian) |
| 3 | **Live demo** | Peer thấy product chạy thật | Screenshot UI + QR code hoặc link để peer thử ngay |
| 4 | **Impact** | Chứng minh product có giá trị | Số cụ thể: thời gian, accuracy, cost — trước vs sau |
| 5 | **Failure modes \| Learning signal** | Nhóm hiểu giới hạn + hướng cải thiện | 2 cột: khi AI sai thì sao \| product học gì từ user |

---

## Tips

- Font lớn, đọc được từ 1-2 mét — peer đứng xem
- Ít chữ, nhiều hình — screenshot, diagram, flow > mô tả text
- Dùng Canva template "poster" nếu muốn design nhanh
- Không cần đẹp, cần rõ: peer nhìn 10 giây hiểu product làm gì
- Before/After nên dùng flow diagram thay vì chỉ viết text
- QR code trỏ đến live demo → peer scan thử ngay = ấn tượng hơn

---

## Mở rộng (optional — bonus)

### Before/After chi tiết hơn

Thay vì chỉ mô tả text, show bằng hình:

| | Before (hiện tại) | After (với AI) |
|---|---|---|
| **Screenshot / sketch** | *(ảnh flow cũ)* | *(ảnh flow mới)* |
| **Số bước** | *VD: 7 bước, 10 phút* | *VD: 3 bước, 2 phút* |
| **Pain point chính** | *VD: phải chờ lễ tân* | *VD: AI trả lời ngay* |
| **Ai quyết định** | *VD: lễ tân tra thủ công* | *VD: AI gợi ý, user chọn* |

### QR code đến live demo

In QR code trên poster → peer scan = thử demo ngay trên điện thoại. Ấn tượng hơn nhiều so với chỉ nhìn screenshot.

- Dùng bất kỳ QR generator nào (free) trỏ đến link deploy
- Nếu chưa deploy: QR trỏ đến video recording demo

### Impact dashboard mock

Sketch 1 dashboard nhỏ trên poster, show metric trước và sau:

```
┌─────────────────────────────────┐
│ Thời gian trung bình    10m → 2m │
│ Độ chính xác           — → 85%  │
│ User hài lòng          3/5 → 4/5│
└─────────────────────────────────┘
```

Dùng số thật từ test (nếu có) hoặc ước lượng có cơ sở.

### Câu hỏi mở rộng

- Peer chỉ nhìn poster 10 giây — thông tin nào PHẢI thấy đầu tiên?
- Poster có thể "đứng một mình" (không cần người giải thích) không?
- Nếu phải bỏ 1 phần trên poster, bỏ phần nào? Tại sao?
