from __future__ import annotations
import textwrap
from pathlib import Path
import pytest
from dotguard.validator import Severity, is_sensitive, parse_env_file, validate
from dotguard.cli import main
from dotguard.init_cmd import generate_example

def write(tmp_path, filename, content):
    p = tmp_path / filename
    p.write_text(textwrap.dedent(content), encoding="utf-8")
    return p

class TestParseEnvFile:
    def test_simple_key_value(self, tmp_path):
        f = write(tmp_path, ".env", "FOO=bar\n")
        assert parse_env_file(f) == {"FOO": "bar"}
    def test_empty_value(self, tmp_path):
        f = write(tmp_path, ".env", "FOO=\n")
        assert parse_env_file(f) == {"FOO": ""}
    def test_inline_comment_stripped(self, tmp_path):
        f = write(tmp_path, ".env", "FOO=bar # comment\n")
        assert parse_env_file(f) == {"FOO": "bar"}
    def test_comment_lines_skipped(self, tmp_path):
        f = write(tmp_path, ".env", "# comment\nFOO=bar\n")
        assert parse_env_file(f) == {"FOO": "bar"}

class TestIsSensitive:
    @pytest.mark.parametrize("key", ["DATABASE_PASSWORD", "API_KEY", "SECRET_KEY", "AUTH_TOKEN", "JWT_SECRET"])
    def test_sensitive_keys(self, key):
        assert is_sensitive(key) is True
    @pytest.mark.parametrize("key", ["APP_NAME", "PORT", "DEBUG", "LOG_LEVEL"])
    def test_non_sensitive_keys(self, key):
        assert is_sensitive(key) is False

class TestValidate:
    def test_missing_key_is_error(self, tmp_path):
        env = write(tmp_path, ".env", "A=1\n")
        example = write(tmp_path, ".env.example", "A=\nB=\n")
        result = validate(env, example)
        assert any(i.key == "B" and i.severity == Severity.ERROR for i in result.issues)
    def test_extra_key_is_warning(self, tmp_path):
        env = write(tmp_path, ".env", "A=1\nEXTRA=x\n")
        example = write(tmp_path, ".env.example", "A=\n")
        result = validate(env, example)
        assert any(i.key == "EXTRA" and i.severity == Severity.WARNING for i in result.issues)
    def test_sensitive_empty_is_error(self, tmp_path):
        env = write(tmp_path, ".env", "API_KEY=\n")
        example = write(tmp_path, ".env.example", "API_KEY=\n")
        result = validate(env, example)
        assert any(i.key == "API_KEY" and i.severity == Severity.ERROR for i in result.issues)
    def test_all_present_no_errors(self, tmp_path):
        env = write(tmp_path, ".env", "A=1\nB=2\n")
        example = write(tmp_path, ".env.example", "A=\nB=\n")
        assert validate(env, example).passed

class TestCLI:
    def test_passes_with_valid_env(self, tmp_path):
        write(tmp_path, ".env", "A=1\nB=2\n")
        write(tmp_path, ".env.example", "A=\nB=\n")
        assert main(["--env", str(tmp_path/".env"), "--example", str(tmp_path/".env.example")]) == 0
    def test_fails_with_missing_key(self, tmp_path):
        write(tmp_path, ".env", "A=1\n")
        write(tmp_path, ".env.example", "A=\nB=\n")
        assert main(["--env", str(tmp_path/".env"), "--example", str(tmp_path/".env.example")]) == 1
    def test_missing_env_file_exits_2(self, tmp_path):
        write(tmp_path, ".env.example", "A=\n")
        assert main(["--env", str(tmp_path/".env"), "--example", str(tmp_path/".env.example")]) == 2

class TestInit:
    def test_strips_values(self, tmp_path):
        write(tmp_path, ".env", "A=hello\nB=world\n")
        code = main(["init", "--env", str(tmp_path/".env"), "--output", str(tmp_path/".env.example")])
        assert code == 0
        result = (tmp_path/".env.example").read_text()
        assert "A=" in result and "hello" not in result
    def test_preserves_comments(self, tmp_path):
        write(tmp_path, ".env", "# Database\nDB_URL=postgres://localhost\n")
        main(["init", "--env", str(tmp_path/".env"), "--output", str(tmp_path/".env.example")])
        assert "# Database" in (tmp_path/".env.example").read_text()
    def test_refuses_overwrite_without_force(self, tmp_path):
        write(tmp_path, ".env", "A=1\n")
        write(tmp_path, ".env.example", "EXISTING=\n")
        assert main(["init", "--env", str(tmp_path/".env"), "--output", str(tmp_path/".env.example")]) == 1
    def test_force_overwrites(self, tmp_path):
        write(tmp_path, ".env", "A=1\n")
        write(tmp_path, ".env.example", "EXISTING=\n")
        assert main(["init", "--env", str(tmp_path/".env"), "--output", str(tmp_path/".env.example"), "--force"]) == 0
