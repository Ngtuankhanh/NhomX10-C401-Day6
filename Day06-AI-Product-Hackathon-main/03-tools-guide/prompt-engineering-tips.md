# Prompt engineering tips

10 tips viết prompt hiệu quả cho hackathon. Tổng hợp từ [OpenAI prompt engineering guide](https://platform.openai.com/docs/guides/prompt-engineering) và [Anthropic prompt engineering guide](https://docs.anthropic.com/en/docs/build-with-claude/prompt-engineering/overview).

---

## 1. Cấu trúc system prompt rõ ràng

Chia system prompt thành 5 phần: role → context → task → constraints → output format. ([OpenAI: write clear instructions](https://platform.openai.com/docs/guides/prompt-engineering#write-clear-instructions))

```
You are a [vai trò cụ thể] working at [bối cảnh].
Context: [thông tin nền cần biết]
Task: [nhiệm vụ chính]
Constraints:
- Trả lời bằng tiếng Việt
- Tối đa 3 bullet points
- Không đưa lời khuyên y tế
Output format: JSON with keys: summary, confidence, sources
```

---

## 2. Dùng delimiters / XML tags để tách phần

OpenAI khuyến nghị dùng `"""`, ` ``` `, `---` để tách input khỏi instruction. Anthropic khuyến nghị dùng XML tags — Claude xử lý XML rất tốt. ([Anthropic: use XML tags](https://docs.anthropic.com/en/docs/build-with-claude/prompt-engineering/use-xml-tags))

```
Tóm tắt nội dung trong <document> bên dưới thành 3 bullet points.

<document>
[paste nội dung dài ở đây]
</document>

<rules>
- Mỗi bullet tối đa 20 từ
- Giữ nguyên thuật ngữ chuyên ngành
- Trả lời bằng tiếng Việt
</rules>
```

Tip: đặt context/document DÀI lên trước, instruction ngắn ở sau. ([Anthropic: long context tips](https://docs.anthropic.com/en/docs/build-with-claude/prompt-engineering/long-context-tips))

---

## 3. Few-shot examples — dạy bằng ví dụ

Khi output cần format cụ thể, cho 2-3 ví dụ trong prompt. ([OpenAI: provide examples](https://platform.openai.com/docs/guides/prompt-engineering#provide-examples))

```
Phân loại email thành: urgent / normal / spam.

Ví dụ:
Email: "Hệ thống sập, cần fix gấp" → urgent
Email: "Báo cáo tháng 3 đính kèm" → normal  
Email: "Bạn trúng thưởng 1 tỷ" → spam

Phân loại email sau: "Server production down từ 2h sáng"
```

---

## 4. Chain-of-thought — bắt AI suy nghĩ từng bước

Thêm "Think step by step" khi bài toán cần logic phức tạp. ([Anthropic: chain of thought](https://docs.anthropic.com/en/docs/build-with-claude/prompt-engineering/chain-of-thought))

```
User muốn hoàn đồ đã mua 35 ngày trước. Chính sách: hoàn trong 30 ngày.

Think step by step:
1. Kiểm tra thời hạn hoàn đồ
2. So sánh với ngày mua
3. Đưa ra quyết định + giải thích cho user
```

Khi nào dùng: bài toán nhiều bước, so sánh, tính toán, hoặc cần AI giải thích reasoning.

Tip (Anthropic): dùng `<thinking>` tag để tách phần suy nghĩ khỏi câu trả lời cuối cùng:

```
Trước khi trả lời, suy nghĩ từng bước trong <thinking> tags.

<thinking>
[AI suy nghĩ ở đây — user có thể đọc hoặc ẩn đi]
</thinking>

Câu trả lời cuối: ...
```

---

## 5. Output format control — kiểm soát format trả về

Chỉ định rõ format output để dễ xử lý trong code. ([OpenAI: specify output format](https://platform.openai.com/docs/guides/prompt-engineering#specify-the-desired-length-of-the-output))

```python
response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[{
        "role": "system",
        "content": """Phân tích review sản phẩm.
Trả về JSON với format:
{
  "sentiment": "positive" | "negative" | "neutral",
  "topics": ["topic1", "topic2"],
  "confidence": 0.0-1.0
}
Chỉ trả JSON, không thêm text."""
    }, {
        "role": "user",
        "content": "Sản phẩm tốt nhưng giao hàng chậm quá, đợi 2 tuần."
    }]
)
```

Tip (Anthropic): dùng [prefill](https://docs.anthropic.com/en/docs/build-with-claude/prompt-engineering/prefill-claudes-response) — điền sẵn đầu assistant response để ép format:

```python
message = client.messages.create(
    model="claude-sonnet-4-6",
    messages=[
        {"role": "user", "content": "Phân tích review: 'Sản phẩm tốt nhưng giao chậm'"},
        {"role": "assistant", "content": "{"}  # prefill để ép JSON
    ]
)
```

---

## 6. Temperature — chỉnh độ sáng tạo

| Temperature | Khi nào dùng | Ví dụ |
|---|---|---|
| 0 | Cần output nhất quán, đúng | Phân loại, trích xuất data, Q&A factual |
| 0.3-0.5 | Cân bằng | Tóm tắt, viết email, dịch thuật |
| 0.7-1.0 | Cần sáng tạo, đa dạng | Brainstorm, viết content, tạo ý tưởng |

```python
# Phân loại → temperature thấp
client.chat.completions.create(model="gpt-4o-mini", temperature=0, ...)

# Brainstorm → temperature cao
client.chat.completions.create(model="gpt-4o-mini", temperature=0.8, ...)
```

---

## 7. Cung cấp reference text — giảm hallucination

Cho AI đọc tài liệu rồi mới trả lời, thay vì để AI tự bịa. ([OpenAI: provide reference text](https://platform.openai.com/docs/guides/prompt-engineering#provide-reference-text))

```
Trả lời câu hỏi dựa HOÀN TOÀN vào context bên dưới.
Nếu context không đủ thông tin → trả lời "Tôi không có đủ thông tin để trả lời."
KHÔNG được bịa thêm thông tin ngoài context.

Context: [paste nội dung tham khảo]
Câu hỏi: [câu hỏi của user]
```

---

## 8. Chia task phức tạp thành subtasks

Đừng nhồi mọi thứ vào 1 prompt. Chia thành pipeline nhỏ, mỗi bước 1 prompt. ([OpenAI: split complex tasks](https://platform.openai.com/docs/guides/prompt-engineering#split-complex-tasks-into-simpler-subtasks))

```python
# Bước 1: Trích xuất thông tin
extract_prompt = "Trích xuất tên, ngày, số tiền từ hóa đơn sau: ..."
info = call_api(extract_prompt)

# Bước 2: Validate
validate_prompt = f"Kiểm tra thông tin sau có hợp lệ không: {info}"
validation = call_api(validate_prompt)

# Bước 3: Tạo response
response_prompt = f"Dựa trên thông tin đã validate: {validation}, viết email xác nhận."
final = call_api(response_prompt)
```

Tip: mỗi bước nhỏ dễ debug hơn. Khi output sai, biết ngay sai ở bước nào.

---

## 9. Role prompting chi tiết

Không chỉ "You are a helpful assistant" — cho AI một persona cụ thể với expertise và constraints rõ ràng. ([Anthropic: give Claude a role](https://docs.anthropic.com/en/docs/build-with-claude/prompt-engineering/system-prompts#give-claude-a-role))

```
You are a senior customer support agent at a Vietnamese e-commerce company.
You have 5 years of experience handling returns and complaints.
You always:
- Respond in Vietnamese, polite but concise
- Check order status before giving advice
- Escalate to manager if refund > 5,000,000 VND
You never:
- Promise refund without checking policy
- Share internal system details with customer
```

---

## 10. Iterate nhanh — test và sửa prompt

Quy trình: viết prompt → test 5 cases → xem output sai ở đâu → sửa prompt → test lại. ([Anthropic: prompt engineering overview](https://docs.anthropic.com/en/docs/build-with-claude/prompt-engineering/overview))

```python
# Test nhanh 1 prompt với nhiều input
test_cases = [
    "Sản phẩm tốt, giao nhanh",           # expected: positive
    "Hàng lỗi, không hoàn tiền",           # expected: negative
    "Giao hàng bình thường",               # expected: neutral
    "Tuyệt vời!!! 10 điểm",               # expected: positive (strong)
    "Không có gì đặc biệt, tạm được"      # expected: neutral (edge case)
]

for case in test_cases:
    result = classify(case)  # gọi API
    print(f"{case[:30]:30s} → {result}")
```

Tip: log lại prompt version + kết quả test. Khi sửa prompt, so sánh với version trước.

---

## Tham khảo thêm

- [OpenAI prompt engineering guide](https://platform.openai.com/docs/guides/prompt-engineering) — full guide với examples
- [Anthropic prompt engineering guide](https://docs.anthropic.com/en/docs/build-with-claude/prompt-engineering/overview) — đặc biệt tốt cho Claude
- [Anthropic prompt library](https://docs.anthropic.com/en/prompt-library/library) — prompt mẫu cho nhiều use cases
- [OpenAI cookbook](https://cookbook.openai.com/) — code examples thực tế
