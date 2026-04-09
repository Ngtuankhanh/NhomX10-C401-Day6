# ROI 3 kịch bản

Ước lượng ROI cho 3 trường hợp: conservative, realistic, optimistic. Không cần chính xác — quan trọng là tư duy "có đáng build không?"

---

## Template

|   | Conservative | Realistic | Optimistic |
|---|-------------|-----------|------------|
| **Assumption** |   |   |   |
| **Cost** |   |   |   |
| **Benefit** |   |   |   |
| **Net** |   |   |   |

**Kill criteria:** khi nào nên dừng? ___

---

## Ví dụ: AI phân loại email

|   | Conservative | Realistic | Optimistic |
|---|-------------|-----------|------------|
| **Assumption** | 100 user, 50% dùng thường xuyên | 500 user, 70% dùng thường xuyên | 2000 user, 85% dùng thường xuyên |
| **Cost** | $50/ngày (API + infra) | $200/ngày | $500/ngày |
| **Benefit** | Mỗi user tiết kiệm 15 phút/ngày → 12.5 giờ/ngày tổng | 58 giờ/ngày | 425 giờ/ngày |
| **Net** | Tiết kiệm ~$300/ngày − $50 = +$250 | +$1160/ngày | +$9750/ngày |

**Kill criteria:** acceptance rate <50% sau 1 tháng, hoặc cost > benefit 2 tháng liên tục.

---

## Hướng dẫn

- **Assumption:** số user, tỷ lệ adoption, mức sử dụng — điều chỉnh giữa 3 kịch bản
- **Cost:** inference API + infrastructure + nhân lực maintain
- **Benefit:** thời gian tiết kiệm, giảm nhân lực, tăng revenue, giảm churn — quy đổi ra tiền
- **Net:** benefit − cost. Nếu conservative đã dương → signal tốt
- **Kill criteria:** đặt TRƯỚC khi build — tránh sunk cost fallacy
- Nhớ: cost inference giảm nhanh (~100x trong 2 năm) — worst case hôm nay ≠ worst case 6 tháng sau

---

## Mở rộng (optional — bonus)

### Cost breakdown chi tiết

Chia nhỏ cost thay vì gộp 1 số:

| Hạng mục | Cách tính | Ước lượng |
|----------|-----------|-----------|
| API inference | $ per call × số call/ngày | |
| Infrastructure (hosting, DB) | | |
| Nhân lực maintain/monitor | giờ/tuần × hourly rate | |
| Data labeling / correction | | |
| **Tổng cost/ngày** | | |

### Benefit không quy đổi được ra tiền

Không phải benefit nào cũng là tiền — nhưng vẫn có giá trị:

| Benefit | Đo bằng gì | Tại sao quan trọng |
|---------|-----------|-------------------|
| *VD: User experience tốt hơn* | NPS, satisfaction score | Retention dài hạn |
| *VD: Data thu được từ user interaction* | Số correction/ngày, signal quality | Competitive moat — càng dùng càng tốt |
| *VD: Brand perception* | | Khách hàng coi công ty là innovative |

### Time-to-value

Mất bao lâu từ khi deploy đến khi thấy benefit?

```
Tuần 1-2: Onboarding, user học cách dùng → chưa thấy benefit rõ
Tuần 3-4: User quen → bắt đầu tiết kiệm thời gian
Tháng 2+:  Data flywheel kick in → AI chính xác hơn → benefit tăng dần
```

Vẽ timeline cho product của nhóm. Nhà đầu tư / stakeholder cần kiên nhẫn bao lâu?

### Competitive moat

Product có tạo được lợi thế cạnh tranh theo thời gian không?

- **Có moat:** càng nhiều user → càng nhiều data → AI càng tốt → càng nhiều user (network effect)
- **Không moat:** đổi sang competitor dễ, AI không cần data riêng

Product của nhóm thuộc loại nào? Data thu được có unique không hay competitor cũng có?

### Câu hỏi mở rộng

- Nếu API cost giảm 10x trong 6 tháng, kịch bản nào thay đổi nhiều nhất?
- Product có cần đạt critical mass (số user tối thiểu) để benefit kick in không?
- Kill criteria hiện tại có quá aggressive hay quá lỏng? Ai là người quyết định "dừng"?
