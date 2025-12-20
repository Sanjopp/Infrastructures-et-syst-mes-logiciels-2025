import json
from pathlib import Path

from backend.models.tricount import Tricount
from backend.utils.utils import tricount_from_dict, tricount_to_dict

DATA_FILE = Path("data/tricounts.json")


def save_tricounts(tricounts: list[Tricount]) -> None:
    DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
    data = [tricount_to_dict(tricount=tricount) for tricount in tricounts]
    with DATA_FILE.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def load_tricounts() -> list[Tricount]:
    if not DATA_FILE.exists() or DATA_FILE.stat().st_size == 0:
        return []

    try:
        with DATA_FILE.open("r", encoding="utf-8") as f:
            raw = json.load(f)
    except json.JSONDecodeError:
        return []
    return [tricount_from_dict(data=data) for data in raw]
