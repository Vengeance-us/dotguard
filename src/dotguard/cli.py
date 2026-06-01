from __future__ import annotations
import argparse, sys
from pathlib import Path
from dotguard.validator import Severity, validate
from dotguard.init_cmd import cmd_init

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
    parser.add_argument("--no-extras", dest="no_extras", action="store_true")
    parser.add_argument("--quiet", action="store_true")
    return parser

def main(argv=None):
    args = build_parser().parse_args(argv)
    if args.command == "init":
        return cmd_init(env=args.env, output=args.output, force=args.force)
    env_path, example_path = Path(args.env), Path(args.example)
    if not env_path.exists():
        print(f"dotguard: error: not found: {env_path}", file=sys.stderr); return 2
    if not example_path.exists():
        print(f"dotguard: error: not found: {example_path}", file=sys.stderr); return 2
    result = validate(env_path, example_path)
    if args.no_extras:
        for i in result.issues:
            if i.severity == Severity.WARNING and "not in .env.example" in i.message:
                i.severity = Severity.ERROR
    if not result.issues:
        if not args.quiet: print(f"dotguard: ok — {env_path} passed all checks")
        return 0
    if not args.quiet:
        print(f"dotguard: validating {env_path} against {example_path}\n")
        for i in result.issues: print(i)
        e, w = len(result.errors), len(result.warnings)
        parts = ([f"{e} error{'s' if e!=1 else ''}"] if e else []) + ([f"{w} warning{'s' if w!=1 else ''}"] if w else [])
        print(f"\n{', '.join(parts)} found.")
    if not result.passed: return 1
    if args.strict and result.warnings: return 1
    return 0

def entrypoint(): sys.exit(main())
if __name__ == "__main__": entrypoint()
