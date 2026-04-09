# Prototyping tools

Chọn tool theo level prototype của nhóm. Không cần dùng hết — chọn 1-2 tool quen nhất.

---

## 3 levels prototype

| Level | Mô tả | Ví dụ | Điểm |
|-------|-------|-------|------|
| **Sketch** | Vẽ/draft flow trên giấy, slides, whiteboard. Chưa build gì. | Vẽ user journey trên giấy A3: user mở app → nhập triệu chứng → AI gợi ý khoa → user chọn → đặt lịch | Đủ điểm |
| **Mock prototype** | UI/flow build được (HTML, app) nhưng chưa gắn AI thật. Dùng tools: Claude Artifacts, v0, Figma... | App HTML có form nhập triệu chứng, hiện kết quả mẫu, flow click được — nhưng chưa gọi API AI | **Bonus** |
| **Working prototype** | Có AI chạy thật. Input → AI xử lý → output. Demo live được. | App gọi Gemini API: user nhập triệu chứng → AI phân tích → trả gợi ý khoa + confidence score | **Bonus ++** |

**Lưu ý:**
- Sketch + Mock: vẫn phải có ít nhất 1 prompt/AI call chạy thật kèm theo (chạy riêng, show bên cạnh)
- Working prototype: dùng vibe-coding tools (Claude Code, Antigravity, Cursor...) hoàn toàn OK
- Mọi level: mỗi người giải thích được phần mình làm. Không hiểu = 0 điểm demo

---

## Tools cho mock prototype

Build UI/flow nhanh, chưa cần gắn AI.

### Claude Artifacts

Mô tả UI trong Claude chat → Claude generate HTML/React chạy trực tiếp trong conversation. Copy code ra file hoặc screenshot.

- **Tốt cho:** mock nhanh 1-2 màn hình, iterate bằng chat
- **Bắt đầu:** vào claude.ai → mô tả màn hình muốn tạo → Claude render artifact

### v0 (Vercel)

Generate React UI từ text prompt. Paste mô tả → ra component chạy được. Deploy free.

- **Tốt cho:** frontend đẹp mà không rành React
- **Bắt đầu:** vào v0.dev → mô tả UI → chỉnh sửa → deploy

### Figma

Design tool tạo clickable prototype. Vẽ màn hình → nối flow → share link test.

- **Tốt cho:** show trải nghiệm user hoàn chỉnh, đặc biệt mobile app
- **Bắt đầu:** tạo account free → dùng template có sẵn → Prototype mode

### Canva

Tạo mock screens nhanh bằng drag-and-drop. Template sẵn cho mobile app, web, slides.

- **Tốt cho:** poster, slides, mock UI đơn giản
- **Bắt đầu:** chọn template "Mobile App" hoặc "Presentation"

---

## Tools cho working prototype

Build prototype có AI chạy thật.

### Claude Code

AI coding agent chạy trong terminal. Mô tả feature bằng text → Claude Code viết code, tạo file, chạy command, debug — toàn bộ flow trong terminal.

- **Tốt cho:** nhóm có dev experience, build full-stack prototype nhanh
- **Bắt đầu:** cài CLI → mở terminal trong project folder → mô tả app muốn build

### Antigravity (Google)

AI app builder — mô tả app bằng text, Antigravity generate full web app có AI tích hợp. Kéo thả chỉnh sửa, deploy trực tiếp.

- **Tốt cho:** working prototype nhanh, không cần code, có thể gắn Gemini API
- **Bắt đầu:** mô tả app → chỉnh layout + logic → connect AI → deploy/share link

### Cursor

VS Code + AI coding. Viết code nhanh với AI autocomplete, chat, và Composer (multi-file edit).

- **Tốt cho:** nhóm có dev experience, project phức tạp hơn
- **Bắt đầu:** download → mở project → Cmd+K generate code

### Google AI Studio (Gemini)

Test prompt Gemini trực tiếp trên web. Tạo structured prompt, few-shot examples, tune parameter. Share link prompt.

- **Tốt cho:** test nhanh Gemini models, không cần code
- **Bắt đầu:** vào aistudio.google.com → New prompt → chọn model → test

### ChatGPT Custom GPTs

Tạo custom GPT với system prompt + knowledge files. Share link cho người dùng thử.

- **Tốt cho:** chatbot, Q&A, trợ lý chuyên ngành
- **Bắt đầu:** ChatGPT → Explore GPTs → Create → viết instructions

### Claude Projects

Tạo Claude project với system prompt + knowledge files. Invite người khác dùng thử.

- **Tốt cho:** chatbot, phân tích, tổng hợp document
- **Bắt đầu:** claude.ai → Projects → New → thêm instructions + files

### Streamlit

Framework Python tạo web app từ 1 file. Deploy free trên Streamlit Cloud.

- **Tốt cho:** UI đẹp hơn chat, cần custom logic
- **Bắt đầu:** `pip install streamlit` → viết `app.py` → `streamlit run app.py`

### Google Colab

Jupyter notebook online, free GPU. Chạy Python + gọi API trực tiếp.

- **Tốt cho:** demo xử lý data, gọi API, show kết quả inline
- **Bắt đầu:** colab.research.google.com → New notebook → code

---

## Tools hỗ trợ

| Tool | Dùng cho |
|------|----------|
| **Loom** | Record màn hình + giọng — backup demo phòng internet chết |
| **Excalidraw** | Vẽ diagram, flow nhanh trên web (free, hand-drawn style) |
| **Mermaid.js** | Vẽ flowchart bằng code — render trên GitHub, mermaid.live |

---

## Gợi ý chọn nhanh

| Nhóm kiểu | Tool đề xuất | Level |
|------------|-------------|-------|
| Chưa biết code | Claude Artifacts / v0 / Figma | Mock prototype |
| Biết prompt, chưa biết code | AI Studio / Custom GPT / Claude Project | Working prototype |
| Biết Python cơ bản | Streamlit / Colab + API | Working prototype |
| Dev experience | Claude Code / Antigravity / Cursor | Working prototype |

Bất kể chọn gì: phải demo được trong 5 phút + mỗi người giải thích được phần mình.

---

*Prototyping tools — Hackathon Day 6 — VinUni A20 — AI Thực Chiến · 2026*
