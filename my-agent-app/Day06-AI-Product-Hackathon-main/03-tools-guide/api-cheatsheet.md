# API cheatsheet

Hướng dẫn nhanh gọi API cho 3 provider phổ biến. Copy-paste và chạy được ngay.

## API keys — cách lấy

| Provider | Free tier | Link |
|---|---|---|
| OpenAI | $5 credit khi đăng ký mới | https://platform.openai.com/api-keys |
| Claude (Anthropic) | Free tier có giới hạn | https://console.anthropic.com/ |
| Gemini (Google) | Free tier generous | https://aistudio.google.com/apikey |

> Nếu chương trình cấp shared key, dùng key đó thay vì tạo mới.

---

## OpenAI

**Python:**
```python
from openai import OpenAI
client = OpenAI(api_key="sk-...")

response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Tóm tắt bài báo này trong 3 bullet points."}
    ],
    temperature=0.3
)
print(response.choices[0].message.content)
```

**JavaScript:**
```javascript
import OpenAI from "openai";
const client = new OpenAI({ apiKey: "sk-..." });

const response = await client.chat.completions.create({
  model: "gpt-4o-mini",
  messages: [
    { role: "system", content: "You are a helpful assistant." },
    { role: "user", content: "Tóm tắt bài báo này trong 3 bullet points." }
  ],
  temperature: 0.3
});
console.log(response.choices[0].message.content);
```

## Claude (Anthropic)

**Python:**
```python
import anthropic
client = anthropic.Anthropic(api_key="sk-ant-...")

message = client.messages.create(
    model="claude-sonnet-4-6",
    max_tokens=1024,
    system="You are a helpful assistant.",
    messages=[
        {"role": "user", "content": "Tóm tắt bài báo này trong 3 bullet points."}
    ]
)
print(message.content[0].text)
```

**JavaScript:**
```javascript
import Anthropic from "@anthropic-ai/sdk";
const client = new Anthropic({ apiKey: "sk-ant-..." });

const message = await client.messages.create({
  model: "claude-sonnet-4-6",
  max_tokens: 1024,
  system: "You are a helpful assistant.",
  messages: [
    { role: "user", content: "Tóm tắt bài báo này trong 3 bullet points." }
  ]
});
console.log(message.content[0].text);
```

## Gemini (Google)

**Python:**
```python
from google import genai
client = genai.Client(api_key="AIza...")

response = client.models.generate_content(
    model="gemini-2.0-flash",
    contents="Tóm tắt bài báo này trong 3 bullet points.",
    config={"system_instruction": "You are a helpful assistant."}
)
print(response.text)
```

**JavaScript:**
```javascript
import { GoogleGenAI } from "@google/genai";
const ai = new GoogleGenAI({ apiKey: "AIza..." });

const response = await ai.models.generateContent({
  model: "gemini-2.0-flash",
  contents: "Tóm tắt bài báo này trong 3 bullet points.",
  config: { systemInstruction: "You are a helpful assistant." }
});
console.log(response.text);
```

---

## System prompt structure

Cấu trúc system prompt hiệu quả:

```
ROLE:       Bạn là [vai trò cụ thể]
CONTEXT:    [Bối cảnh, thông tin nền]
TASK:       [Nhiệm vụ cần làm]
CONSTRAINTS:[Giới hạn: ngôn ngữ, độ dài, format]
OUTPUT:     [Định dạng output mong muốn]
```

## Lưu ý quan trọng

- **Rate limits:** Free tier thường 3-20 requests/phút. Nếu bị 429 error → đợi 1 phút rồi thử lại
- **Cost:** gpt-4o-mini và gemini-2.0-flash rẻ nhất (~$0.15/1M input tokens). Dùng model nhỏ cho prototype
- **Streaming:** Dùng `stream=True` (Python) khi muốn hiện kết quả từng phần — UX tốt hơn cho demo
