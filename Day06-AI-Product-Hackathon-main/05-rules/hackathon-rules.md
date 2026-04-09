# Hackathon rules

Luật chơi hackathon AI Thực Chiến. Đọc kỹ trước khi bắt đầu.

---

## Timeline

```
DAY 5
16:00-16:30   Phổ biến rules, scoring, POC options
16:30-17:00   Chia nhóm + chọn track + chia zone
17:00-18:00   Working time — align hướng, bắt đầu Canvas
              Tối (optional): topic + Canvas draft

DAY 6
09:00-09:30   M1 — Canvas check
09:30-11:00   Build POC
11:00-11:15   M2 — Checkpoint "show 1 thứ chạy được"
11:15-13:00   Build tiếp (có break)
14:00-15:30   Polish POC + chuẩn bị demo
15:30-16:00   M3 — Demo prep done + dry run
16:00-17:00   M4 — Demo round (peer feedback)
17:00-18:00   M5 — Top teams present + closing
```

---

## Milestones

### M1 — Canvas check (Day 6, 9:00)

GV check nhanh mỗi nhóm. Canvas draft yêu cầu tối thiểu:

- **Value:** user là ai, pain gì, AI giải gì
- **Trust:** automation hay augmentation? Khi AI sai thì sao?
- **Feasibility:** POC option nào (A/B/C)? Risk chính?
- **Learning signal:** product thu data gì để cải thiện?

Có Canvas → vào build ngay. Chưa có → 30 phút bổ sung, phải xong trước 9:30.

### M2 — Checkpoint (Day 6, 11:00)

GV đi vòng check ~2 phút/nhóm:

- Có gì chạy được (dù rough)?
- Mỗi thành viên nói được đang làm gì?
- Biết sẽ demo flow nào?

Chưa pass → GV giúp simplify scope. Code không kịp → chuyển option B ngay.

### M3 — Demo prep done (Day 6, 15:30)

Checklist trước demo round:

- [ ] POC chạy được hoặc mock flow ready
- [ ] Demo script 5 phút: ai nói gì, show gì, thứ tự nào
- [ ] Poster/slides tóm tắt: Problem → Solution → Auto/Aug → Demo
- [ ] Mỗi người trả lời được: "Auto hay aug?", "Failure mode chính?", "Phần mình làm gì?"
- [ ] Feedback forms nhận đủ

15:30-16:00: dry run trong nhóm + setup station.

### M4 — Demo round (Day 6, 16:00-17:00)

Peer demo + structured feedback trong zone (xem chi tiết bên dưới).

### M5 — Top teams + closing (Day 6, 17:00-18:00)

- Đếm điểm feedback → announce top mỗi zone
- Top teams present 5 phút + Q&A 2-3 phút
- Trao giải + recap + closing

---

## POC options

| Option | Mô tả | Cho ai |
|---|---|---|
| **A: Prompt-based** | Agent/chatbot chạy 1 flow chính, dùng API có sẵn | Mọi nhóm |
| **B: Mock flow** | Clickable prototype (Figma/slides) + 1 prompt test thật | Mọi nhóm |
| **C: Working code** | Agent end-to-end | Nhóm mạnh, bonus |

- Chọn A hoặc B. Bonus nếu làm được C.
- Option B vẫn **phải có ít nhất 1 prompt/AI call test thật** — không được 100% mock.

---

## Vibe-coding rule

> **Không hiểu code = 0 điểm demo.**

"Hiểu code" nghĩa là: mỗi thành viên giải thích được **phần mình làm**. Không cần hiểu hết toàn bộ codebase.

Khi demo, GV/peer có thể hỏi bất kỳ thành viên nào: "Phần này hoạt động thế nào?" Nếu không trả lời được → coi như không hiểu.

Dùng AI tools (Cursor, Copilot, v0) để code: **OK.** Nhưng phải hiểu output của tool.

---

## Demo round rules (M5)

**Format:** lần lượt trình bày trong zone (~5 team/zone), 10 phút/nhóm.

**Cách chơi:**

1. Các nhóm trong zone **lần lượt trình bày**, các nhóm còn lại ngồi nghe + feedback
2. Mỗi nhóm: **5 phút trình bày** + **5 phút Q&A và feedback** từ peer + GV
3. Sau mỗi nhóm trình bày, các nhóm khác **điền feedback form**

**Deliverable:** mỗi nhóm nộp đủ feedback forms cho tất cả team đã xem. Không nộp đủ → trừ điểm.

**Chấm 2 chiều:**

1. **Team được review:** tổng điểm feedback từ peer → chọn top mỗi zone
2. **Team đi review:** chất lượng feedback (comment cụ thể, không chấm bừa) → cũng được chấm

---

## Feedback form

| Mục | Nội dung |
|---|---|
| Team được đánh giá | Tên nhóm: ___ |
| 1. Problem-solution fit | ○1 ○2 ○3 ○4 ○5 |
| 2. AI product thinking | ○1 ○2 ○3 ○4 ○5 |
| 3. Demo quality | ○1 ○2 ○3 ○4 ○5 |
| 1 điều làm tốt | ___ |
| 1 gợi ý cải thiện | ___ |

---

## Scoring tổng hợp

| Touchpoint | Ai chấm | Chấm gì |
|---|---|---|
| Canvas (M1) | GV | Có/không + chất lượng |
| Checkpoint (M2) | GV | Có gì chạy, phân công rõ, hướng demo rõ |
| Demo — team được review (M4) | Peer teams | 3 tiêu chí × 1-5 + qualitative |
| Demo — team đi review (M4) | GV/TA | Chất lượng feedback |
| Top present (M5) | GV + lớp | Bonus cho top teams |

---

## Zone assignment

| Zone | Teams |
|---|---|
| Zone 1 | _(GV điền khi chia nhóm)_ |
| Zone 2 | ___ |
| Zone 3 | ___ |
| Zone 4 | ___ |
| Zone 5 | ___ |
| Zone 6 | ___ |

---

## Rời lớp Day 5, mỗi nhóm phải có

1. Track đã chọn (VinFast / Vinmec / VinUni-VinSchool / XanhSM / Open)
2. Problem statement 1 câu: "Ai gặp vấn đề gì, hiện giải thế nào, AI giúp được gì"
3. Phân công ai làm phần nào trong Canvas
