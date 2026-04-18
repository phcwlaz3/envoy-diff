import argparse
import json
from envoy_diff.loader import load_config
from envoy_diff.labeler import label_config


def add_label_subparsers(subparsers) -> None:
    p = subparsers.add_parser("label", help="Attach semantic labels to config keys")
    p.add_argument("file", help="Env or JSON config file")
    p.add_argument(
        "--format", choices=["text", "json"], default="text", dest="fmt"
    )
    p.add_argument(
        "--rule",
        nargs=2,
        metavar=("LABEL", "PATTERN"),
        action="append",
        default=[],
        help="Extra labeling rule, e.g. --rule versioned VERSION",
    )
    p.add_argument(
        "--only-labeled",
        action="store_true",
        help="Only show keys that received labels",
    )


def run_label_command(args) -> int:
    try:
        config = load_config(args.file)
    except Exception as exc:
        print(f"error: {exc}")
        return 1

    extra_rules = {label: pattern for label, pattern in args.rule}
    result = label_config(config, extra_rules=extra_rules or None)

    if args.fmt == "json":
        out = {
            "summary": result.summary(),
            "label_count": result.label_count(),
            "labels": result.labels,
        }
        print(json.dumps(out, indent=2))
    else:
        print(result.summary())
        items = result.labels.items() if args.only_labeled else [
            (k, result.labels.get(k, [])) for k in result.config
        ]
        for key, lbls in items:
            tag_str = ", ".join(lbls) if lbls else "(none)"
            print(f"  {key}: {tag_str}")

    return 0
