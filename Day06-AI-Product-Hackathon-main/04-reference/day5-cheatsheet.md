# Day 5 cheatsheet — 1 trang recap

Tra cứu nhanh trong lúc làm hackathon.

## Domino chain

```
AI = probabilistic (luôn có sai số)
  → Automation hay augmentation?
    → 3 trụ: Requirement / UX / Eval
      → Canvas (gộp 3 trụ vào 1 trang)
        → Feedback loop + Data flywheel
          → ROI 3 kịch bản
```

---

## Automation vs augmentation

| | Automation | Augmentation |
|---|---|---|
| AI làm gì | Làm thay user | Gợi ý, user quyết |
| Khi AI sai | Thiệt hại đã xảy ra — user không kịp can thiệp | User bỏ qua, không thiệt hại |
| Accuracy cần | Rất cao (99%+) | Chấp nhận thấp hơn (Copilot: 30%) |
| UX cần | Monitoring, alert, undo | Suggestion UI — accept/reject |
| Trust risk | Over-trust (không verify) | Under-trust (bỏ qua hết) |

Thực tế: bắt đầu aug → tăng dần auto khi data đủ (V1 routing → V2 copilot → V3 tự động).

---

## Precision vs recall

- **Precision:** AI nói "có" → đúng bao nhiêu? Ưu tiên khi sai nhầm = thiệt hại lớn
- **Recall:** trong số đúng thật → AI tìm được bao nhiêu? Ưu tiên khi bỏ sót = thiệt hại lớn
- User THẤY & sửa được → recall ok. User KHÔNG thấy → precision cao
- PM chọn precision/recall = product decision, không phải technical decision

---

## Feedback loop — 3 loại signal

| Loại | Mô tả | Ví dụ |
|------|-------|-------|
| Implicit | User behavior, không biết đang cho feedback | Click, skip, dwell time |
| Explicit | User chủ động | Thumbs up/down, rating, report |
| Correction | User sửa output AI | Kéo email sang nhãn đúng, edit text AI viết |

Qualitative > quantitative: "accuracy 87%" không nói sai ở đâu — cần nhìn output bằng mắt.
