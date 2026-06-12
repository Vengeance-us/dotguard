from __future__ import annotations
import argparse, sys
from pathlib import Path
from dotguard.validator import Severity, validate
from dotguard.init_cmd import cmd_init
from dotguard.git_check import check_env_in_git

def build_parser():
    parser = argparse.ArgumentParser(prog="dotguard", description="Validate your .env before you deploy.")
    subparsers = parser.add_subparsers(dest="command")
    init_p = subparsers.add_parser("init", help="Generate .env.example from .env")
    init_p.add_argument("--env", default=".env", metavar="FILE")
    init_p.add_argument("--output", default=".env.example", metavar="FILE")
    init_p.add_argument("--force", action="store_true")
    parser.add_argument("--env", default=".env", metavar="FILE")
    parser.add_argument("--example", default=".env.example", metavar="FILE")
    parser.add_argument("--strict", action="store_true")
    parser.add_argument("--fail-on", dest="fail_on", default="errors", choices=["errors", "warnings", "all"], metavar="LEVEL")
    parser.add_argument("--no-extras", dest="no_extras", action="store_true")
    parser.add_argument("--quiet", action="store_true")
    parser.add_argument("--no-git-check", dest="no_git_check", action="store_true")
    return parser

def print_line(msg, quiet):
    if not quiet: print(msg)

def run_check(args):
    env_path, example_path = Path(args.env), Path(args.example)
    if not env_path.exists():
        print(f"dotguard: error: not found: {env_path}", file=sys.stderr); return 2
    if not example_path.exists():
        print(f"dotguard: error: not found: {example_path}", file=sys.stderr); return 2
    git_error = None
    if not getattr(args, "no_git_check", False):
        git_error = check_env_in_git(env_path)
    result = validate(env_path, example_path)
    if args.no_extras:
        for i in result.issues:
            if i.severity == Severity.WARNING and "not in .env.example" in i.message:
                i.severity = Severity.ERROR
    if not result.issues and not git_error:
        print_line(f"dotguard: ok — {env_path} passed all checks", args.quiet)
        return 0
    if git_error:
        print_line(f"[ERROR] GIT: {git_error}", args.quiet)
    for i in result.issues: print_line(str(i), args.quiet)
    errors = len(result.errors) + (1 if git_error else 0)
    warnings = len(result.warnings)
    parts = ([f"{errors} error{'s' if errors!=1 else ''}"] if errors else []) + ([f"{warnings} warning{'s' if warnings!=1 else ''}"] if warnings else [])
    print_line(f"{', '.join(parts)} found.", args.quiet)
    fail_on = args.fail_on
    if args.strict and fail_on == "errors":
        fail_on = "warnings"
    if fail_on == "errors":
        return 1 if errors else 0
    return 1 if (errors or warnings) else 0

def main(argv=None):
    args = build_parser().parse_args(argv)
    if args.command == "init":
        return cmd_init(env=args.env, output=args.output, force=args.force)
    return run_check(args)

def entrypoint(): sys.exit(main())
if __name__ == "__main__": entrypoint()
