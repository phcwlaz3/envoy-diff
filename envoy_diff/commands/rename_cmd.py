"""CLI subcommand: rename keys in an env config file."""
import argparse
import json
import sys
from envoy_diff.loader import load_config
from envoy_diff.renamer import rename_config


def add_rename_subparsers(subparsers) -> None:
    parser = subparsers.add_parser("rename", help="Rename keys in an env config")
    parser.add_argument("file", help="Path to env or JSON config file")
    parser.add_argument(
        "--map",
        nargs=2,
        metavar=("OLD", "NEW"),
        action="append",
        dest="mappings",
        default=[],
        help="Explicit key rename (repeatable)",
    )
    parser.add_argument("--pattern", help="Regex pattern to match key names")
    parser.add_argument("--replacement", default="", help="Replacement string for pattern")
    parser.add_argument(
        "--format", choices=["text", "json"], default="text", dest="fmt"
    )
    parser.set_defaults(func=run_rename_command)


def run_rename_command(args: argparse.Namespace) -> int:
    try:
        config = load_config(args.file)
    except Exception as exc:
        print(f"Error loading file: {exc}", file=sys.stderr)
        return 1

    mapping = {old: new for old, new in args.mappings} if args.mappings else None
    pattern = args.pattern or None
    replacement = args.replacement if pattern else None

    result = rename_config(config, mapping=mapping, pattern=pattern, replacement=replacement)

    if args.fmt == "json":
        output = {
            "config": result.config,
            "renamed": [{"from": o, "to": n} for o, n in result.renamed],
            "skipped": result.skipped,
            "rename_count": result.rename_count(),
        }
        print(json.dumps(output, indent=2))
    else:
        print(result.summary())
        if result.skipped:
            print(f"Skipped (conflict): {', '.join(result.skipped)}")
        print()
        for key, value in result.config.items():
            print(f"{key}={value}")

    return 0
