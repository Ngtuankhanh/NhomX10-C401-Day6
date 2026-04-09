# Reflection Cá Nhân — Hackathon Day 06

**Họ và Tên:** Cao Chí Hải  
**Mã Học Viên:** 2A202600011

---

## 1. Role cụ thể trong nhóm

Technical Developer kiêm AI Engineer. Phụ trách toàn bộ pipeline xây dựng và vận hành Knowledge Graph cho hệ thống chẩn đoán y tế: từ thu thập dữ liệu (crawling), chuẩn hóa dữ liệu, xây dựng Knowledge Graph bằng LLM, thiết kế Agent Pipeline (MedicalKGAgent), đến xây dựng benchmark và evaluation hệ thống.

---

## 2. Phần phụ trách cụ thể (Có output rõ ràng)

- **Output 1:** Thiết kế và triển khai toàn bộ Phase 1 & 2 — Crawling + Knowledge Graph Construction. Bao gồm: Scrapy Spider cho Vinmec, Medlatec, Bệnh viện 108; script chuẩn hóa `normalize_md.py`; prompt chuyên sâu để trích xuất KG và script xử lý batch bất đồng bộ `kg_builder.py` (sử dụng GPT-4o-mini).

- **Output 2:** Xây dựng hoàn chỉnh Agent Pipeline (`MedicalKGAgent`) với 4 bước: `KGExtractor → KGSearcher → DiseaseScorer → DiagnosisSynthesizer`. Tích hợp `KGStore`, `SpecialtyMapper` từ file `chuyenkhoa.json`, cùng cơ chế fallback và tính `completeness_score`.

- **Output 3:** Thiết kế và thực hiện toàn bộ Phase 4 — Benchmark hệ thống. Bao gồm: xây dựng `test_set.csv`, script chạy benchmark so sánh **LLM Baseline** vs **Agent + KG**, pipeline tính metrics (Top-1 Accuracy, Latency), template annotation cho human evaluator và script tổng hợp kết quả sau khi có human annotation.

---

## 3. Đánh giá phần SPEC

- **Mạnh nhất:** Phần thiết kế **Knowledge Graph Schema** và **Agent Pipeline 4 bước**. Việc định nghĩa rõ ràng Node Types, Relation Types cùng cơ chế `context_weight` giúp hệ thống có khả năng truy vấn và chấm điểm bệnh chính xác, có cơ sở giải thích (explainable). Đây là nền tảng quan trọng để Agent vượt trội hơn LLM thuần.

- **Yếu nhất:** Phần **Benchmark & Evaluation**. Test set hiện tại chủ yếu được sinh tự động từ KG, chưa đủ đa dạng và khó khăn (edge cases như triệu chứng mơ hồ, bệnh hiếm, triệu chứng chồng chéo nhiều chuyên khoa). Việc thu thập thêm test case thực tế từ bác sĩ hoặc bệnh án sẽ giúp đánh giá khách quan và đáng tin cậy hơn.

---

## 4. Các đóng góp cụ thể khác

- Viết và hoàn thiện toàn bộ tài liệu kỹ thuật chi tiết (`reflection.md` này) bao gồm kiến trúc tổng quan, cấu trúc thư mục dự án, checklist triển khai từng phase và các script hỗ trợ (validate KG, build specialty map, normalize data…).
- Xây dựng cơ chế validate KG tự động (`validate_kg.py`) và script sinh draft `chuyenkhoa.json` từ KG.
- Test và debug end-to-end pipeline với nhiều case thực tế: viêm màng não, thoái hóa đốt sống cổ, nhồi máu cơ tim nghi ngờ, nhiễm khuẩn tiết niệu…

---

## 5. Một điều học được mới

Trước hackathon tôi nghĩ việc xây dựng Knowledge Graph chỉ đơn giản là “dùng LLM parse text ra JSON”. Sau khi làm mới nhận ra: chất lượng KG phụ thuộc rất lớn vào **prompt engineering** và **data normalization**. Một prompt tốt + cấu trúc .md thống nhất có thể nâng độ chính xác trích xuất lên đáng kể. Ngoài ra, cơ chế `context_weight` và `weighted scoring` trong DiseaseScorer là kỹ thuật rất hiệu quả để tăng độ tin cậy của chẩn đoán so với keyword matching thông thường.

---

## 6. Nếu làm lại, bạn sẽ thay đổi điều gì?

Tôi sẽ **thu thập và chuẩn hóa dữ liệu từ nhiều nguồn song song ngay từ đầu** thay vì tập trung chủ yếu vào Vinmec. Ngoài ra, nên xây dựng một bộ **Golden Dataset** (khoảng 30–50 bệnh có annotation thủ công bởi bác sĩ) ngay từ Phase 1 để dùng làm reference khi validate prompt và KG. Điều này sẽ giúp phát hiện sớm các vấn đề về chất lượng dữ liệu và prompt thay vì phải sửa sau khi đã crawl và extract hàng trăm file.

---

## 7. AI giúp gì và AI "sai" ở đâu?

- **AI giúp:** Claude & GPT-4o hỗ trợ rất tốt trong việc viết Scrapy Spider, thiết kế schema KG chi tiết (Node & Relation types), generate prompt extraction chuyên sâu, và đặc biệt là gợi ý các edge case triệu chứng cũng như cách thiết kế fallback mechanism khi LLM không trả về kết quả.

- **AI sai/nhiễu:** Khi yêu cầu generate code cho Agent Pipeline phức tạp, AI hay đưa ra thiết kế quá phức tạp (thêm quá nhiều layer, graph không cần thiết). Tôi phải tinh chỉnh nhiều lần để giữ cho pipeline vẫn đơn giản, dễ debug và phù hợp với thời gian hackathon. Bài học: AI giỏi gợi ý ý tưởng nhưng vẫn cần con người kiểm soát chặt chẽ scope và độ phức tạp thực tế.