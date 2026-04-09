# 📊 Báo cáo Feedback Dự án Nhóm E6

## 1. Tổng quan dự án

Nhóm E6 xây dựng một hệ thống AI hỗ trợ trong lĩnh vực y tế.
Cụ thể, hệ thống thực hiện:

* Thu âm cuộc hội thoại giữa bác sĩ và bệnh nhân
* Chuyển đổi âm thanh thành văn bản (speech-to-text)
* Trích xuất các thông tin quan trọng từ hội thoại phục vụ lưu trữ và phân tích

Đây là một bài toán có tính ứng dụng cao, đặc biệt trong việc giảm tải công việc hành chính cho bác sĩ.

---

## 2. Đánh giá theo tiêu chí

| Tiêu chí             | Điểm (1-5) | Nhận xét                                                                                                                                                               |
| -------------------- | ---------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Problem-solution fit | 5          | Bài toán rõ ràng, xuất phát từ pain point thực tế trong ngành y tế. Giải pháp AI phù hợp và có tiềm năng ứng dụng cao trong việc giảm tải cho bác sĩ.                  |
| AI product thinking  | 4          | Đã xác định được hướng đi sản phẩm, tuy nhiên chưa có đánh giá đầy đủ về các trường thông tin cần trích xuất. Hiện mới dừng ở việc đánh giá chất lượng speech-to-text. |
| Demo quality         | 5          | Giao diện (UI) được thiết kế tốt, trực quan. Flow demo mượt mà, business case được trình bày rõ ràng và thuyết phục.                                                   |

---

## 3. Điểm mạnh

* **Xác định bài toán tốt:**
  Bài toán rõ ràng, có nhu cầu thực tế và cấp thiết trong lĩnh vực y tế.

* **Ứng dụng AI hợp lý:**
  Việc sử dụng speech-to-text và trích xuất thông tin là hướng đi phù hợp với bài toán.

* **UI/UX tốt:**
  Giao diện được đầu tư, dễ sử dụng, tạo cảm giác chuyên nghiệp.

* **Demo thuyết phục:**
  Flow trình bày rõ ràng, giúp người xem hiểu được giá trị sản phẩm dù hệ thống còn ở mức prototype.

---

## 4. Điểm cần cải thiện

* **Chưa đánh giá end-to-end pipeline:**
  Hiện tại mới chỉ đánh giá chất lượng của mô hình speech-to-text.

  → Cần bổ sung:

  * Đánh giá độ chính xác của các trường thông tin trích xuất
  * Xây dựng metric cụ thể (precision, recall, F1, v.v.)

* **Thiếu validation trên dữ liệu thực tế:**
  Chưa có test trên các tình huống hội thoại đa dạng (nhiễu, giọng địa phương, môi trường bệnh viện).

* **Vấn đề pháp lý và quyền riêng tư:**
  Việc ghi âm hội thoại cần:

  * Có sự đồng ý rõ ràng từ bệnh nhân
  * Tuân thủ các quy định về bảo mật dữ liệu y tế

  → Đây là yếu tố rất quan trọng nếu muốn triển khai thực tế

---

## 5. Gợi ý cải thiện

* **Bổ sung pipeline đánh giá hoàn chỉnh:**
  Không chỉ dừng ở speech-to-text mà cần:

  * Evaluate toàn bộ pipeline (audio → text → structured data)
  * So sánh với ground truth

* **Xây dựng bộ dữ liệu test:**

  * Thu thập hoặc giả lập các hội thoại đa dạng
  * Gắn nhãn các trường thông tin để đánh giá

* **Cải thiện AI product thinking:**

  * Xác định rõ output cuối cùng (ví dụ: form bệnh án tự động)
  * Đo lường giá trị mang lại (tiết kiệm bao nhiêu thời gian cho bác sĩ)

* **Xử lý vấn đề pháp lý:**

  * Thiết kế flow xin consent bệnh nhân
  * Ẩn danh dữ liệu (anonymization) nếu cần

---

## 6. Kết luận

Dự án có **problem-solution fit rất tốt** và mang tính thực tiễn cao.
Phần demo và UI đã giúp truyền tải rõ ràng giá trị sản phẩm.

Tuy nhiên, để tiến xa hơn (production-level), nhóm cần:

* Đánh giá đầy đủ pipeline AI
* Bổ sung dữ liệu và metric
* Xem xét kỹ yếu tố pháp lý

→ Nếu cải thiện các điểm này, dự án có tiềm năng phát triển thành một sản phẩm thực tế trong ngành y tế.
