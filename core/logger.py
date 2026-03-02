import json
from datetime import UTC, datetime
from pathlib import Path


def save_session_log(session: dict, out_dir: str = "data/logs") -> str:
    Path(out_dir).mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(UTC).strftime("%Y%m%d_%H%M%S")
    filename = f"session_{session.get('persona_name', 'persona').lower()}_{stamp}.json"
    path = Path(out_dir) / filename
    path.write_text(json.dumps(session, ensure_ascii=False, indent=2), encoding="utf-8")
    return str(path)
