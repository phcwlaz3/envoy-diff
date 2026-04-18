"""CLI sub-command: annotate config keys with metadata labels."""
import argparse
import json
import sys
from typing import List, Optional

from envoy_diff.loader import load_config
from envoy_diff.annotator import annotate_config


def add_annotate_subparsers(subparsers) -> None:
    parser = subparsers.add_parser(
        "annotate",
        help="Attach metadata annotations to config keys.",
    )
    parser.add_argument("file", help="Path to .env or .json config file.")
    parser.add_argument(
        "--label",
        metavar="KEY=ANNOTATION",
        action="append",
        default=[],
        dest="labels",
        help="Annotation to apply, e.g. DB_HOST='primary host'. Repeatable.",
    )
    parser.add_argument(
        "--format",
        choices=["text", "json"],
        default="text",
        dest="fmt",
    )


def run_annotate_command(args) -> int:
    try:
        config = load_config(args.file)
    except Exception as exc:  # noqa: BLE001
        print(f"Error loading file: {exc}", file=sys.stderr)
        return 1

    annotations = {}
    for label in args.labels:
        if "=" not in label:
            print(f"Invalid --label format (expected KEY=TEXT): {label}", file=sys.stderr)
            return 1
        key, _, text = label.partition("=")
        annotations[key.strip()] = text.strip()

    result = annotate_config(config, annotations)

    if args.fmt == "json":
        output = {
            "annotated": result.annotated,
            "skipped": result.skipped,
            "summary": result.summary(),
        }
        print(json.dumps(output, indent=2))
    else:
        print(result.summary())
        if result.annotated:
            print("\nAnnotated keys:")
            for key, meta in result.annotated.items():
                print(f"  {key} = {meta['value']!r}  [{meta['annotation']}]")
        if result.skipped:
            print("\nSkipped (not in config):")
            for key in result.skipped:
                print(f"  {key}")

    return 0
