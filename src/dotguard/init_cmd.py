from __future__ import annotations
import sys
from pathlib import Path

def generate_example(env_path: Path) -> str:
    lines = []
    with env_path.open(encoding="utf-8") as fh:
        for raw_line in fh:
            line = raw_line.rstrip("\n")
            stripped = line.strip()
            if not stripped or stripped.startswith("#") or "=" not in stripped:
                lines.append(line)
                continue
            key, _, _ = stripped.partition("=")
            lines.append(f"{key.strip()}=")
    return "\n".join(lines) + "\n"

def cmd_init(env: str, output: str, force: bool) -> int:
    env_path, output_path = Path(env), Path(output)
    if not env_path.exists():
        print(f"dotguard init: error: env file not found: {env_path}", file=sys.stderr)
        return 2
    if output_path.exists() and not force:
        print(f"dotguard init: error: {output_path} already exists. Use --force to overwrite.", file=sys.stderr)
        return 1
    output_path.write_text(generate_example(env_path), encoding="utf-8")
    print(f"dotguard init: created {output_path} from {env_path}")
    return 0
