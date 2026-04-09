import os
import re

# ==================== CẤU HÌNH ====================
INPUT_FOLDER  = r"D:\agent1\vinmec_diseases"
OUTPUT_FOLDER = r"D:\agent1\vinmec_extracted"

TARGET_SECTIONS = [
    "Triệu chứng bệnh",
    "Đối tượng nguy cơ",
]
# ===================================================


def remove_duplicate_lines(text: str) -> str:
    """
    Xóa dòng bị lặp liên tiếp (so sánh sau khi strip dấu '- ' ở đầu).
    """
    lines = text.splitlines()
    cleaned = []
    prev_core = None
    for line in lines:
        core = line.strip().lstrip("-").strip()
        if core and core == prev_core:
            continue  # bỏ dòng lặp
        cleaned.append(line)
        prev_core = core
    return "\n".join(cleaned)


def extract_sections(md_text: str, target_keywords: list) -> str:
    """
    Tách các section có heading ### chứa keyword.
    Mỗi block kết thúc khi gặp heading ## hoặc ### tiếp theo.
    """
    # Tách theo BẤT KỲ heading ## hoặc ### nào
    pattern = re.compile(r"(?=^#{2,3}\s)", re.MULTILINE)
    blocks = pattern.split(md_text)

    matched_blocks = []
    for block in blocks:
        if not block.strip():
            continue
        first_line = block.splitlines()[0]
        # Chỉ lấy heading ### (3 dấu #), bỏ qua ##
        if not first_line.startswith("###"):
            continue
        if any(kw.lower() in first_line.lower() for kw in target_keywords):
            cleaned = remove_duplicate_lines(block.strip())
            matched_blocks.append(cleaned)

    return "\n\n---\n\n".join(matched_blocks)


def process_folder(input_folder: str, output_folder: str):
    os.makedirs(output_folder, exist_ok=True)

    md_files = [f for f in os.listdir(input_folder) if f.endswith(".md")]
    if not md_files:
        print("Không tìm thấy file .md nào trong folder!")
        return

    print(f"Tìm thấy {len(md_files)} file .md\n")

    for filename in md_files:
        input_path  = os.path.join(input_folder, filename)
        output_path = os.path.join(output_folder, filename)

        with open(input_path, "r", encoding="utf-8") as f:
            content = f.read()

        extracted = extract_sections(content, TARGET_SECTIONS)

        if extracted:
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(f"# Trích xuất từ: {filename}\n\n")
                f.write(extracted)
            print(f"✅  {filename}  →  {output_path}")
        else:
            print(f"⚠️  {filename}  —  Không tìm thấy section phù hợp, bỏ qua.")

    print(f"\nHoàn tất! File đã lưu tại: {output_folder}")


if __name__ == "__main__":
    process_folder(INPUT_FOLDER, OUTPUT_FOLDER)