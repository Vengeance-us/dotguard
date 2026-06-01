from __future__ import annotations
import re
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path

SENSITIVE_PATTERNS = re.compile(
    r"(password|passwd|secret|token|api[_-]?key|auth|credential|private[_-]?key"
    r"|access[_-]?key|signing[_-]?key|encryption[_-]?key|jwt|oauth|cert|ssl)",
    re.IGNORECASE,
)

class Severity(str, Enum):
    ERROR = "ERROR"
    WARNING = "WARNING"

@dataclass
class Issue:
    severity: Severity
    key: str
    message: str
    def __str__(self):
        return f"[{self.severity.value}] {self.key}: {self.message}"

@dataclass
class ValidationResult:
    issues: list[Issue] = field(default_factory=list)
    @property
    def errors(self):
        return [i for i in self.issues if i.severity == Severity.ERROR]
    @property
    def warnings(self):
        return [i for i in self.issues if i.severity == Severity.WARNING]
    @property
    def passed(self):
        return len(self.errors) == 0
    def add(self, severity, key, message):
        self.issues.append(Issue(severity=severity, key=key, message=message))

def parse_env_file(path: Path) -> dict:
    env = {}
    with path.open(encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, _, raw = line.partition("=")
            key = key.strip()
            if not key:
                continue
            raw = raw.strip()
            if raw and raw[0] in ('"', "'"):
                q = raw[0]
                end = raw.find(q, 1)
                env[key] = raw[1:end] if end != -1 else raw[1:]
            else:
                env[key] = raw.split("#")[0].rstrip()
    return env

def is_sensitive(key: str) -> bool:
    return bool(SENSITIVE_PATTERNS.search(key))

def validate(env_path: Path, example_path: Path) -> ValidationResult:
    result = ValidationResult()
    env = parse_env_file(env_path)
    example = parse_env_file(example_path)
    for key in sorted(set(example) - set(env)):
        result.add(Severity.ERROR, key, "missing from .env (required by .env.example)")
    for key in sorted(set(env) - set(example)):
        result.add(Severity.WARNING, key, "present in .env but not in .env.example")
    for key in sorted(set(example) & set(env)):
        if env[key] == "":
            if is_sensitive(key):
                result.add(Severity.ERROR, key, "sensitive key has no value")
            else:
                result.add(Severity.WARNING, key, "value is empty")
    return result
