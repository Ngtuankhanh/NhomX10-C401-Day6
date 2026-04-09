import os, json, re, logging, asyncio
from pathlib import Path
from dotenv import load_dotenv
from openai import AsyncOpenAI

load_dotenv()

INPUT_DIR   = Path(r"D:\agent1\vinmec_extracted")
OUTPUT_DIR  = Path(r"D:\agent1\kg_json")
PROMPT_FILE = Path(r"D:\agent1\prompt.md")

MODEL       = "gpt-4o-mini"
TEMPERATURE = 0.1
CONCURRENCY = 20

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(OUTPUT_DIR / "_extract.log", encoding="utf-8"),
    ],
)
log = logging.getLogger(__name__)

# ──────────────────────────────────────────────
# INIT
# ──────────────────────────────────────────────
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise EnvironmentError("Không tìm thấy OPENAI_API_KEY trong .env")

client    = AsyncOpenAI(api_key=api_key)
semaphore = asyncio.Semaphore(CONCURRENCY)
log.info("Loaded OpenAI client")

# ──────────────────────────────────────────────
# HELPERS
# ──────────────────────────────────────────────
def load_prompt(path: Path) -> str:
    text = path.read_text(encoding="utf-8")
    return re.sub(
        r"Bây giờ hãy trích xuất Knowledge Graph từ văn bản sau:.*$",
        "", text, flags=re.DOTALL,
    ).strip()

async def call_api(system_prompt: str, user_text: str) -> str:
    resp = await client.chat.completions.create(
        model=MODEL,
        temperature=TEMPERATURE,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user",   "content": user_text},
        ],
    )
    return resp.choices[0].message.content.strip()

def parse_json(raw: str) -> dict:
    match = re.search(r"(\{.*\}|\[.*\])", raw, re.DOTALL)
    candidate = match.group(1) if match else re.sub(
        r"```(?:json)?", "", raw
    ).strip().strip("`")
    
    candidate = re.sub(r'\\(?!["\\/bfnrtu])', r'\\\\', candidate)
    
    return json.loads(candidate)

# ──────────────────────────────────────────────
# XỬ LÝ TỪNG FILE
# ──────────────────────────────────────────────
async def process_file(md_path: Path, system_prompt: str,
                       total: int, idx: int, failed_log: Path):
    out_path = OUTPUT_DIR / (md_path.stem + ".json")

    if out_path.exists():
        log.info(f"[{idx}/{total}] SKIP {md_path.name}")
        return

    log.info(f"[{idx}/{total}] Xử lý: {md_path.name}")
    user_text = md_path.read_text(encoding="utf-8")

    async with semaphore:
        try:
            raw = await call_api(system_prompt, user_text)
            kg  = parse_json(raw)
            out_path.write_text(
                json.dumps(kg, ensure_ascii=False, indent=2),
                encoding="utf-8"
            )
            log.info(
                f"✓ {out_path.name} | "
                f"{len(kg.get('nodes', []))} nodes | "
                f"{len(kg.get('relations', []))} relations"
            )

        except json.JSONDecodeError as e:
            log.error(f"✗ {md_path.name} JSON lỗi: {e}")
            with open(failed_log, "a", encoding="utf-8") as f:
                f.write(f"{md_path.name}\tJSON_ERROR\t{e}\n")

        except Exception as e:
            log.error(f"✗ {md_path.name} lỗi: {type(e).__name__}: {e}")
            with open(failed_log, "a", encoding="utf-8") as f:
                f.write(f"{md_path.name}\tAPI_ERROR\t{e}\n")

# ──────────────────────────────────────────────
# MAIN
# ──────────────────────────────────────────────
async def main():
    failed_log = OUTPUT_DIR / "_failed.txt"
    if not failed_log.exists():
        failed_log.write_text("file\terror_type\tdetail\n", encoding="utf-8")

    system_prompt = load_prompt(PROMPT_FILE)
    md_files      = sorted(INPUT_DIR.glob("*.md"))
    total         = len(md_files)
    log.info(f"{total} file .md → {OUTPUT_DIR}")

    await asyncio.gather(*[
        process_file(md_path, system_prompt, total, idx, failed_log)
        for idx, md_path in enumerate(md_files, 1)
    ])

    log.info("=" * 50)
    log.info("Hoàn tất!")

if __name__ == "__main__":
    asyncio.run(main())