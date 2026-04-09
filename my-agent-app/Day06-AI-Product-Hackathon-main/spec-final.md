# SPEC — AI Product Hackathon

**Nhóm:** NhomX10

**Track:** ☐ VinFast · ☑ Vinmec · ☐ VinUni-VinSchool · ☐ XanhSM · ☐ Open

**Problem statement (1 câu):** Cả bệnh nhân và người chăm sóc thường mất nhiều thời gian, lo lắng vì đi nhầm khoa do không tự đánh giá được triệu chứng, Chatbot gợi ý chuyên khoa AI sẽ giúp phân tích triệu chứng để điều hướng đúng chuyên khoa và hỗ trợ đặt lịch khám tức thì.

---

## 1. AI Product Canvas

|   | Value | Trust | Feasibility |
|---|-------|-------|-------------|
| **Câu hỏi** | User nào? Pain gì? AI giải gì? | Khi AI sai thì sao? User sửa bằng cách nào? | Cost/latency bao nhiêu? Risk chính? |
| **Trả lời** | *Bệnh nhân/Caregiver không biết nên theo khám tại chuyên khoa nào. AI giúp phân tích nhanh dựa vào triệu chứng, cung cấp gợi ý chuyên khoa kèm confidence score và luồng book lịch tiện lợi.* | *Nếu AI gợi ý sai, User sẽ thấy lý do không hợp lý, có thể bỏ qua gợi ý để đổi khoa lúc xác nhận, hoặc chọn khám tổng quát. Có Emoji reaction để gửi report.* | *~$0.005/query bằng LLM. Latency < 3s. Risk: AI bỏ lỡ ca bệnh nguy hiểm, gợi ý chậm trễ thay vì yêu cầu cấp cứu lập tức.* |

**Automation hay augmentation?** ☐ Automation · ☑ Augmentation
Justify: *Augmentation — AI thu thập thông tin và giúp chẩn đoán sơ bộ (gợi ý), tuy nhiên quyền quyết định chọn khoa và xác nhận mức độ ưu tiên đặt lịch vẫn thuộc về người dùng, AI không tự áp đặt chuyên khoa.*

**Learning signal:**

1. User correction đi vào đâu? *Lịch sử các lần user tự tay chỉnh sửa lại chuyên khoa (tại form xác nhận) và nhấn phản hồi dislike (👎) đi thẳng vào Elasticsearch Logs.*
2. Product thu signal gì để biết tốt lên hay tệ đi? *Theo dõi sự gia tăng của tỉ lệ Book lịch thành công (Booking completion rate tăng) và giảm số case bệnh nhân bị đẩy viện nội bộ sau khi khám.*
3. Data thuộc loại nào? ☐ User-specific · ☑ Domain-specific · ☐ Real-time · ☑ Human-judgment · ☐ Khác: ___
   Có marginal value không? (Model đã biết cái này chưa?) *Có marginal value siêu lớn. Cơ sở dữ liệu và Mapping của Vinmec rất đặc thù theo danh mục chuyên khoa của bộ/viện, mô hình Base chưa thể map chuẩn 100% nếu không bổ sung Knowledge Graph này.*

---

## 2. User Stories — 4 paths

### Feature: Gợi ý chuyên khoa từ triệu chứng bệnh

**Trigger:** *Bệnh nhân nhập vào mô tả triệu chứng và yêu cầu giúp đỡ hướng đi khám qua chat widget.*

| Path | Câu hỏi thiết kế | Mô tả |
|------|-------------------|-------|
| Happy — AI đúng, tự tin | User thấy gì? Flow kết thúc ra sao? | *Hiển thị gợi ý VD: "Khoa THẦN KINH", tự tin cao. User xác nhận thấy đúng và bấm tiếp tục chuyển sang luồng Book Lịch.* |
| Low-confidence — AI không chắc | System báo "không chắc" bằng cách nào? User quyết thế nào? | *Agent 2 báo điểm đầy đủ thông tin (score) < 70. Bot phản hồi "Thông tin chưa đủ, bạn có bị thêm chứng ù tai không?". User bấm chọn Option bổ sung trên UI để làm rõ.* |
| Failure — AI sai | User biết AI sai bằng cách nào? Recover ra sao? | *AI map sai chuyên khoa do phân tích sai ngữ cảnh. User đọc mô tả thấy sai, lập tức click nút "Tìm chuyên khoa khác" hoặc yêu cầu "Tôi muốn khám Đa khoa".* |
| Correction — user sửa | User sửa bằng cách nào? Data đó đi vào đâu? | *User ấn 👎, chọn "Gợi ý sai", hệ thống mở ô input text tự do. Dữ liệu chạy vào hàng đợi (Queue) để Medical Reviewer cập nhật lại Knowledge Graph đồ thị y khoa.* |

### Feature: Hỗ trợ đặt lịch khám tích hợp

**Trigger:** *Người dùng đã xác nhận mục tiêu và có nhu cầu lựa chọn lịch khung giờ, bác sĩ.*

| Path | Câu hỏi thiết kế | Mô tả |
|------|-------------------|-------|
| Happy — AI đúng, tự tin | User thấy gì? Flow kết thúc ra sao? | *Bot trích xuất chuẩn thời gian và tên bác sĩ, cung cấp Card bác sĩ. User bấm "Xác nhận đặt lịch", màn hình báo Success. Nhận Email.* |
| Low-confidence — AI không chắc | System báo "không chắc" bằng cách nào? User quyết thế nào? | *Ngày giờ cung cấp mơ hồ "Cuối tuần tới". Bot hỏi lại: "Bạn muốn khám vào T7 (18/4) hay CN (19/4)?". User chọn 1 slot hiển thị.* |
| Failure — AI sai | User biết AI sai bằng cách nào? Recover ra sao? | *Trích xuất Entity NER thất bại (Sai SĐT, nhầm ngày). User phát hiện lỗi trên màn hình Summary Card.* |
| Correction — user sửa | User sửa bằng cách nào? Data đó đi vào đâu? | *User click "[✏️ Sửa thông tin]" trên phần Summary Card và nhập liệu lại. Log report gửi về Developer để tinh chỉnh lại Prompt Entity Extraction.* |

---

## 3. Eval metrics + threshold

**Optimize precision hay recall?** ☑ Precision · ☐ Recall
Tại sao? *Giải quyết bài toán định tuyến (Routing). Giảm thiểu tối đa False Positive vì hành động định tuyến nhầm vào chuyên khoa sâu sai lệch khiến chi phí khám/chữa bị kéo dài, bác sĩ mất thì giờ, bệnh nhân thất vọng. Thà bỏ sót bệnh cụ thể và đẩy về Khoa Khám Nội Tổng Quát còn hơn là chẩn đoán tự tin nhưng sai lệch chuyên khoa ngách.*

| Metric | Threshold | Red flag (dừng khi) |
|--------|-----------|---------------------|
| *Symptom-to-Specialty Accuracy (Precision)* | *≥85%* | *<70% trong 1 tuần (Có thể do lỗi model update hoặc đồ thị y khoa bị lệch).* |
| *Booking Completion Rate* | *≥65%* | *<30% trong 3 ngày liên tiếp (Có lỗi UI/UX, hoặc Agent bắt bệnh nhân loop hỏi đáp quá dài gây nản).* |
| *Tỷ lệ Agent 2 ngắt luồng yêu cầu hỏi thêm triệu chứng* | *<40%* | *>60% (Model quá khắt khe hoặc lượng người dùng cung cấp thông tin rác lớn).* |

---

## 4. Top 3 failure modes

| # | Trigger | Hậu quả | Mitigation |
|---|---------|---------|------------|
| 1 | *Người dùng mô tả thông tin bệnh lý CẤP CỨU NGUY HIỂM (đau ngực khẩn cấp, mức độ đau vượt ngưỡng, co giật, nôn máu...)* | *AI định tuyến vào luồng đặt lịch khám thường quy vào mai/tuần sau. Gây rủi ro sinh mạng, kiện tụng pháp lý lớn.* | *Tách một Filter Scanner/Keyword Watcher bắt từ khóa khẩn cấp chặn đầu input. Nếu match (VD: đột quỵ), ép thoát luồng hoàn toàn, Alert đỏ khuyên gọi cấp cứu 115 ngay.* |
| 2 | *Phân tích rơi vào vòng lặp vô tận do kiến thức y khoa triệu chứng chồng chéo (ví dụ "mệt mỏi, sụt cân")* | *Agent phân tích quá lâu (hallucinate) hoặc suggest một khoa hiếm gặp sai lệch, làm mất uy tín bot.* | *Hệ thống thiết lập Max Loops = 3. Nếu completeness score quá trình hội thoại vẫn không tăng, fallback bắt buộc định vị bệnh nhân về Khám Nội Tổng Quát + hiển thị Disclaimer Y tế.* |
| 3 | *Người dùng cố ý nhập input rác, jailbreak system AI hoặc không mô tả bệnh lý.* | *Hệ thống mất API token để xử lý Knowledge Graph, ảnh hưởng tới load server và gây dirty log cho Elasticsearch.* | *Có Guardrail đo đạc "Medical Intent" ban đầu. Nếu hệ thống đánh giá Intent < 50%, bot từ chối cung cấp phản hồi và kết thúc chat sớm bảo vệ resource.* |

---

## 5. ROI 3 kịch bản

|   | Conservative | Realistic | Optimistic |
|---|-------------|-----------|------------|
| **Assumption** | *Thử nghiệm 1 chi nhánh nhỏ: 200 lượt/ngày, 60% completion* | *Rollout chuỗi 3 chi nhánh: 1000 lượt/ngày, 75% completion* | *Rollout toàn hệ thống chuỗi viện: 5000 lượt/ngày, 85% completion* |
| **Cost** | *$10/ngày (Inference, Sever)* | *$50/ngày* | *$200/ngày* |
| **Benefit** | *Giảm chi phí sức lực của Tổng đài viên 4 giờ/ngày (~$20)* | *Tiết kiệm 25h làm việc (khoảng 3 NV trực) (~$120)* | *Giảm tải 100h làm việc, tăng lượt hiển thị tích cực, thu mới 5% KH qua trải nghiệm số (~$1500)* |
| **Net** | *+ $10 / ngày* | *+ $70 / ngày* | *+ $1300 / ngày* |

**Kill criteria:** *Cost chạy server vượt xa giá trị Benefit đo lường sau 3 tuần liên tiếp / Số phản hồi khiếu nại "Gợi ý Khám sai khoa" đến tổng đài viên cao hơn 5% trong tổng Booking / Phát sinh kiện tụng về cung cấp thông tin.*

---

## 6. Mini AI spec (1 trang)

**Medical Symptom Chatbot** là sản phẩm giải quyết bài toán "Đi khám không biết nên chọn khoa nào" của nhóm Bệnh nhân, và bài toán "Tốn thời gian sàng lọc định tuyến / Quá tải tổng đài" của phía Bệnh viện Vinmec. Giải pháp được thiết kế dưới dạng khung giao diện Embeddable Web Chat Widget, qua đó tạo ra một hành trình khép kín tinh gọn từ Hỏi Bệnh ➔ Gợi Ý Khoa ➔ Chốt Lịch Khám chỉ trong vòng 3 đến 5 phút thay vì quy trình truyền thống. 

Hệ thống tuân thủ triệt để nguyên lý **Augmentation**, công nghệ AI thu thập dữ liệu và khớp mô hình, đóng vai trò trợ lý chuyên đưa ra lời khuyên đi kèm chỉ số tự tin. Cú "Chốt chặn - Lựa chọn đi tiếp và Đặt lịch" luôn được yêu cầu sự quyết định xác nhận từ bệnh nhân, bảo vệ bot khỏi việc sai sót thay thế quyền chẩn đoán y khoa chuyên nghiệp. Về mặt kiến trúc lõi, dự án sử dụng định dạng 2 luồng Agents: Main Agent chịu trách nhiệm dẫn dắt câu chuyện UI thân thiện (Orchestrator); và Specialist Agent đứng phía sau rà soát triệu chứng trên Knowledge Graph nội bộ nhằm đảm bảo không "Bịa kiến thức" như một LLM Base thông thường.

Nhóm ưu tiên tối ưu hóa chỉ số **Precision** (Symptom-to-Specialty Accuracy). Theo triết lý sản phẩm, định tuyến bệnh nhân sai ở chuyên khoa hẹp khiến hao tốn tiền của đôi bên một cách cực kỳ vô ích. Vì vậy, hệ thống thà từ chối đưa ra kết luận hẹp để bệnh nhân đi Khám bệnh Nội tổng quát ban đầu (an toàn), còn hơn cố gắng đoán nếu tỷ lệ chắc chắn (score completeness) chưa đủ cao. 

Dữ liệu sẽ vận hành dưới dạng luồng **Data Flywheel** thông minh dựa vào Human-judgment. Người dùng khi phát hiện điểm lỗi, tự thay đổi chuyên khoa lúc chốt đơn xác nhận và kèm click 👎, log sẽ chuyển thẳng vào Queue. Ban Y Khoa (Medical Reviewers) có thể dễ dàng update từ vựng và Knowledge Graph. 

Ba rủi ro hạch tâm nhất bao gồm: rủi ro bỏ sót lời kêu cứu cấp cứu ngầm, sự nhiễu loạn hội thoại vòng lặp vô hạn, và rác Guardrail Intent. Giải pháp Mitigation được áp chặt: **Keyword Watchers Rule-based** cắt quyền AI ép buộc cảnh báo quy trình cấp cứu khi gặp input như "nôn máu/đột quỵ", khóa Hard-limit số lượt hỏi (Max = 3 lần/Session), và kiểm soát chuẩn hóa Medical Intent rành mạch. Kết hợp tất cả, Medical Booking Chatbot hứa hẹn mang giá trị cực cao với rủi ro tiệm cận thấp nhất.

---

## 7. Beyond The Hackathon (Tầm nhìn phát triển mở rộng)

*(Phần bổ sung thể hiện AI Product Thinking cho Demo Day nhằm cho thấy khả năng Scale của sản phẩm ra khỏi phạm vi một cuộc thi)*

Hệ thống kiến trúc Multi-Agent của Chatbot hiện tại chỉ là lớp móng đầu tiên của một hệ sinh thái **Trợ lý Y tế Toàn năng (Super Health Hub)** trong tương lai:

**1. Lộ trình Triển khai Mở rộng (Roadmap):**
- **MVP (Hiện tại):** Chatbot Web-based tập trung vào xử lý Text NLP để định tuyến chuyên khoa và đặt lịch khám nội bộ.
- **Phase 2 (Đa kênh & Cá nhân hóa):** Mở rộng trên kênh Zalo OA / App Vinmec. Tích hợp trực tiếp với Hồ sơ Bệnh án điện tử (EHR) của bệnh viện để Bot tự hiểu tiền sử bệnh mà không cần hỏi lại. Xây dựng tính năng gọi điện tự động nhắc lịch tái khám.
- **Phase 3 (AI Đa phương thức - Multimodal):** Nâng cấp Vision Agent cho phép người bệnh gửi ảnh vùng tổn thương (chăm sóc da liễu, chấn thương ngoài) để chẩn đoán. Mở rộng bot đọc hiểu Kết quả Xét nghiệm tuyến dưới bằng hệ thống OCR chuyên dụng.
- **Phase 4 (Chăm sóc Y tế Chủ động - Proactive Care):** Vượt ra khỏi việc "Chờ bệnh nhân chat", hệ thống kết nối với thiết bị Wearables (Apple Watch) để thu thập sinh hiệu. Khi phát hiện nhịp tim bất thường / té ngã mạch, AI chủ động điều động xe cứu thương tự động theo tọa độ GPS.

**2. Kiến trúc Tổ hợp Đa tác tử tương lai (Multi-Agent Ecosystem):**
Hệ thống không dừng lại ở mức 2 Agent như hiện tại, mà hướng tới một **Trung tâm Điều phối (Central Orchestrator)** với hàng chục Agent chuyên trách:
- Thiết kế Omni model bao phủ tất cả các loại dữ liệu.
- Lõi điều phối sử dụng LangGraph để routing công việc linh hoạt về các ban ngành siêu ngách:
  - *Visual Agent:* Phụ trách phân tích màu sắc da, mức độ nghiêm trọng vết thương.
  - *Voice Agent:* Thay thế tổng đài CSKH, chăm sóc sức khỏe tâm thần bằng phân tích biểu cảm giọng nói.
  - *IoT Watcher Agent:* Agent trực thức 24/7 chỉ để lắng nghe các chỉ số y tế khẩn cấp, sẵn sàng Bypass mọi quyền kiểm soát để kích hoạt luồng "Cấp cứu 115" (Emergency Flow).