# Demo script — 5 phút trình bày + 5 phút Q&A

Cấu trúc demo cho demo round. Tổng 10 phút/nhóm: 5 phút trình bày + 5 phút Q&A từ peer và GV. Mỗi người trong nhóm nói ít nhất 1 phần.

---

## Structure (5 phút trình bày)

| Phần | Thời gian | Nội dung | Ai nói |
|------|-----------|----------|--------|
| **Problem + Before** | 45 giây | Ai gặp vấn đề gì? Flow hiện tại ra sao? Tại sao chưa đủ? | ___ |
| **Solution + After** | 45 giây | AI giải thế nào? Auto hay aug? Flow mới khác gì flow cũ? | ___ |
| **Live demo** | 120 giây | Show flow chính chạy thật. Input → AI xử lý → output → user thấy gì. Nếu kịp: show 1 edge case + cách handle | ___ |
| **Impact + Lessons** | 45 giây | Metric trước vs sau. Failure mode chính. Điều học được khi build. | ___ |

## Q&A (5 phút)

- Peer và GV hỏi — mỗi người trong nhóm phải trả lời được phần mình
- Câu hỏi thường gặp: "Auto hay aug?", "Failure mode chính?", "AI sai thì sao?", "Phần mình làm gì?"

---

## Tips

- **Show, don't tell:** demo chạy thật, không chỉ nói miệng
- **Nói chậm:** 5 phút ngắn hơn bạn nghĩ — nói nhanh = peer không hiểu
- **Mỗi người nói:** phân công rõ trước, không để 1 người nói hết
- **Chuẩn bị backup:** nếu demo crash → có screenshot/video backup
- **Mở sẵn mọi thứ:** trước khi peer đến, laptop mở sẵn demo, không để mất thời gian load

---

## Anti-patterns

- Đừng show code — peer cần thấy product, không cần thấy code
- Đừng giải thích API — "dùng GPT-4o" là đủ
- Đừng quá 5 phút — hard limit, còn 5 phút Q&A
- Đừng demo nhiều flow — 1 flow chính, demo tốt > demo nhiều

## Checklist trước demo

- [ ] Demo script viết ra giấy, mỗi người biết phần mình
- [ ] Dry run ít nhất 1 lần, bấm giờ
- [ ] Backup plan nếu demo crash
- [ ] Mỗi người trả lời được: "Auto hay aug?", "Failure mode chính?", "Phần mình làm gì?"

---

## Mở rộng (optional — bonus)

### Demo edge case

Ngoài happy path, demo thêm 1 tình huống AI xử lý chưa tốt — và show cách product handle:

| Phần | Thời gian | Nội dung |
|------|-----------|----------|
| **Happy path** | 40 giây | Flow chính, AI đúng, user hài lòng |
| **Edge case** | 20 giây | Input khó → AI không chắc hoặc sai → show UI handle: fallback, gợi ý thay thế, option escalate |

Tại sao? Peer và GV ấn tượng hơn rất nhiều khi nhóm biết product mình fail ở đâu và đã design cho nó.

### Before → After live comparison

Demo cả flow cũ (không AI) và flow mới (có AI) cạnh nhau:

1. **30 giây:** show flow cũ — user phải làm thủ công, mất bao lâu, bao nhiêu bước
2. **30 giây:** show flow mới — cùng task, AI hỗ trợ, nhanh hơn / ít bước hơn

So sánh trực tiếp tạo "aha moment" cho người xem.

### Hỏi peer thử ngay

Mời 1 peer ngồi thử demo ngay tại chỗ (thay vì chỉ nhìn nhóm demo):

- Đưa laptop/điện thoại cho peer
- Nói: "thử nhập triệu chứng của bạn xem AI gợi ý gì"
- Quan sát phản ứng — peer tự trải nghiệm ấn tượng hơn peer nghe kể

### Câu hỏi mở rộng

- Nếu demo crash giữa chừng, câu nói nào sẽ cứu tình huống? (Plan B nên chuẩn bị sẵn lời nói)
- Có 5 phút trình bày — nên show 1 flow sâu hay 2-3 flow ngắn?
- Peer hỏi "tại sao không dùng ChatGPT/Gemini trực tiếp?" — trả lời thế nào?
