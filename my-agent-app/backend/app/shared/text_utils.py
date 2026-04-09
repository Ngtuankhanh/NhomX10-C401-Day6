import re
import unicodedata
from datetime import datetime

PHONE_REGEX = re.compile(r"(0[35789]\d{8})")
EMAIL_REGEX = re.compile(r"^[^\s@]+@[^\s@]+\.[^\s@]+$")
OTP_REGEX = re.compile(r"\b(\d{6})\b")
AGE_REGEX = re.compile(r"\b(\d{1,3})\s*tuoi\b")

EMERGENCY_KEYWORDS = (
    "dau nguc", "kho tho", "kho tho dot ngot", "liet tay chan",
    "mat y thuc", "co giat", "non ra mau", "xuat huyet", "tai nan"
)

def normalize_text(value: str | None) -> str:
    if not value:
        return ""
    normalized = unicodedata.normalize(
        "NFD", value.lower().replace("đ", "d").replace("Đ", "d")
    )
    without_diacritics = "".join(
        char for char in normalized if unicodedata.category(char) != "Mn"
    )
    cleaned = re.sub(r"[^a-z0-9\s]", " ", without_diacritics)
    return re.sub(r"\s+", " ", cleaned).strip()

def title_case_words(value: str) -> str:
    return " ".join(part.capitalize() for part in value.split())

def yes_intent(message: str) -> bool:
    normalized = normalize_text(message)
    return normalized in {
        "co", "dong y", "ok", "oke", "duoc", "xac nhan dat lich",
        "xac nhan", "dat lich", "dat lich kham", "tiep tuc", "toi muon dat lich"
    }

def no_intent(message: str) -> bool:
    normalized = normalize_text(message)
    return normalized in {
        "khong", "khong can", "bo qua", "bo qua va tiep tuc",
        "de sau", "khong muon", "khong dat", "dung"
    }

def reset_intent(message: str) -> bool:
    normalized = normalize_text(message)
    return normalized in {"bat dau lai", "tao phien moi", "lam lai", "reset"}

def edit_intent(message: str) -> bool:
    normalized = normalize_text(message)
    return normalized in {"sua", "sua thong tin", "cap nhat thong tin"}

def resend_otp_intent(message: str) -> bool:
    normalized = normalize_text(message)
    return normalized in {"gui lai ma", "gui lai otp", "gui lai", "lay ma moi"}

def detect_gender(message: str) -> int | None:
    normalized = normalize_text(message)
    if normalized in {"nam", "male"}:
        return 1
    if normalized in {"nu", "female"}:
        return 2
    return None

def parse_age(message: str) -> int | None:
    match = AGE_REGEX.search(normalize_text(message))
    if not match: return None
    age = int(match.group(1))
    return age if 0 < age < 120 else None

def parse_phone_number(message: str) -> str | None:
    match = PHONE_REGEX.search(normalize_text(message))
    return match.group(1) if match else None

def parse_email(message: str) -> str | None:
    candidate = message.strip()
    return candidate if EMAIL_REGEX.match(candidate) else None

def parse_date_of_birth(message: str) -> str | None:
    raw = message.strip()
    for pattern in ("%Y-%m-%d", "%d/%m/%Y", "%d-%m-%Y"):
        try:
            return datetime.strptime(raw, pattern).date().isoformat()
        except ValueError:
            continue
    return None

def extract_otp(message: str) -> str | None:
    match = OTP_REGEX.search(message)
    return match.group(1) if match else None

def extract_name(message: str) -> str | None:
    cleaned = " ".join(message.strip().split())
    if len(cleaned) < 2: return None
    normalized = normalize_text(cleaned)
    if normalized in {"co", "khong", "ok", "dat lich"}: return None
    return cleaned

def is_emergency(message: str) -> bool:
    normalized = normalize_text(message)
    return any(keyword in normalized for keyword in EMERGENCY_KEYWORDS)
