import argparse
import json
from envoy_diff.loader import load_config
from envoy_diff.trimmer import trim_config


def add_trim_subparsers(subparsers) -> None:
    parser = subparsers.add_parser("trim", help="Strip whitespace from config values")
    parser.add_argument("file", help="Path to env or JSON config file")
    parser.add_argument(
        "--keys",
        nargs="+",
        metavar="KEY",
        help="Only trim these specific keys (default: all)",
    )
    parser.add_argument(
        "--chars",
        default=None,
        metavar="CHARS",
        help="Characters to strip (default: whitespace)",
    )
    parser.add_argument(
        "--format",
        choices=["text", "json"],
        default="text",
        help="Output format (default: text)",
    )
    parser.set_defaults(func=run_trim_command)


def run_trim_command(args: argparse.Namespace) -> int:
    try:
        config = load_config(args.file)
    except Exception as exc:
        print(f"Error loading file: {exc}")
        return 1

    result = trim_config(
        config,
        keys=args.keys if hasattr(args, "keys") else None,
        strip_chars=args.chars if hasattr(args, "chars") else None,
    )

    if args.format == "json":
        print(
            json.dumps(
                {
                    "config": result.config,
                    "trimmed_keys": result.trimmed_keys,
                    "trim_count": result.trim_count(),
                    "summary": result.summary(),
                },
                indent=2,
            )
        )
    else:
        print(result.summary())
        if result.has_trimmed():
            print()
            for k, v in result.config.items():
                marker = "*" if k in result.trimmed_keys else " "
                print(f"  [{marker}] {k}={v}")

    return 0
