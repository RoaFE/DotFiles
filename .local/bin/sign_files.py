#!/usr/bin/env python3
"""
sign_files.py — Prepend a comment signature to source files.

Usage examples:
  python sign_files.py --ext cs --signature "Copyright 2026 Acme Ltd."
  python sign_files.py --ext gd,gdshader --signature "MIT License" --comment "#"
  python sign_files.py --ext cpp,h --signature "Author: Jane" --block --open "/*" --close "*/"
  python sign_files.py --ext py --signature "DO NOT EDIT" --dir ./src --recursive --dry-run
"""

import argparse
import datetime
import sys
from pathlib import Path


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def default_signature() -> str:
    signature = "Author:\t\tRowan Stockton\n"
    signature += "Created:\t\t" + datetime.date.today().strftime('%d-%m-%Y (dd-mm-YYYY)')
    return signature


def build_header(signature: str, comment: str, block: bool, open_tag: str, close_tag: str) -> str:
    """Return the full header string (with trailing newline) to prepend."""
    if block:
        return f"{open_tag}\n{signature}\n{close_tag}\n"
    else:
        lines = signature.splitlines()
        commented = "\n".join(f"{comment} {line}" if line.strip() else comment for line in lines)
        return commented + "\n"


def already_signed(content: str, signature: str) -> bool:
    """Return True if the signature text already appears in the file."""
    return signature in content


def process_file(path: Path, header: str, signature: str,
                 skip_existing: bool, dry_run: bool) -> str:
    """
    Prepend header to a single file.
    Returns a short status string for logging.
    """
    try:
        original = path.read_text(encoding="utf-8")
    except (UnicodeDecodeError, PermissionError) as e:
        return f"SKIP  (read error: {e})"

    if skip_existing and already_signed(original, signature):
        return "SKIP  (already signed)"

    new_content = header + "\n" + original

    if dry_run:
        return "DRY   (would prepend header)"

    try:
        path.write_text(new_content, encoding="utf-8")
    except PermissionError as e:
        return f"ERROR (write error: {e})"

    return "OK    (header added)"


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Prepend a comment signature to source files.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )

    parser.add_argument("--dir", default=".",
                        help="Target directory (default: current directory)")
    parser.add_argument("--ext", required=True,
                        help="Comma-separated extensions to match, e.g. cs,gd or *.cpp,*.h")
    parser.add_argument("--signature", default= default_signature(),
                        help="Signature text to insert (can be multi-line with \\n)")
    parser.add_argument("--comment", default="//",
                        help="Line comment prefix (default: //)")

    # Block comment options
    parser.add_argument("--block", action="store_true",
                        help="Use block comment style instead of line comments")
    parser.add_argument("--open", default="/*",
                        help="Block comment opening token (default: /*)")
    parser.add_argument("--close", default="*/",
                        help="Block comment closing token (default: */)")

    parser.add_argument("--recursive", action="store_true",
                        help="Recurse into subdirectories")
    parser.add_argument("--skip-existing", action="store_true",
                        help="Skip files that already contain the signature text")
    parser.add_argument("--dry-run", action="store_true",
                        help="Preview what would happen without writing files")

    args = parser.parse_args()

    # ---- Resolve directory ------------------------------------------------
    target_dir = Path(args.dir).resolve()
    if not target_dir.is_dir():
        print(f"Error: '{target_dir}' is not a directory.", file=sys.stderr)
        sys.exit(1)

    # ---- Normalise extensions ---------------------------------------------
    raw_exts = [e.strip().lstrip("*.").lower() for e in args.ext.split(",")]
    extensions = {f".{e}" for e in raw_exts if e}
    if not extensions:
        print("Error: no valid extensions parsed.", file=sys.stderr)
        sys.exit(1)

    # ---- Collect files ----------------------------------------------------
    glob = "**/*" if args.recursive else "*"
    files = [
        p for p in target_dir.glob(glob)
        if p.is_file() and p.suffix.lower() in extensions
    ]

    if not files:
        print(f"No files matching {extensions} found in '{target_dir}'.")
        sys.exit(0)

    # ---- Build header -----------------------------------------------------
    # Allow \n in the signature string passed via CLI
    signature = args.signature.replace("\\n", "\n")
    header = build_header(signature, args.comment, args.block, args.open, args.close)

    # ---- Print plan -------------------------------------------------------
    mode = "DRY RUN — " if args.dry_run else ""
    print(f"\n{mode}Signing {len(files)} file(s) in '{target_dir}'")
    print(f"Extensions : {', '.join(sorted(extensions))}")
    print(f"Comment    : {'block' if args.block else 'line'} ({args.comment!r})")
    print(f"Signature  : {signature!r}\n")
    print("-" * 60)

    # ---- Process ----------------------------------------------------------
    counts = {"OK": 0, "SKIP": 0, "ERROR": 0, "DRY": 0}
    for f in sorted(files):
        status = process_file(f, header, signature,
                              args.skip_existing, args.dry_run)
        key = status.split()[0].rstrip("(")
        counts[key] = counts.get(key, 0) + 1
        rel = f.relative_to(target_dir)
        print(f"  {status:<40} {rel}")

    print("-" * 60)
    print(f"\nDone.  OK: {counts.get('OK',0)}  "
          f"Skipped: {counts.get('SKIP',0)}  "
          f"Errors: {counts.get('ERROR',0)}"
          + (f"  Dry: {counts.get('DRY',0)}" if args.dry_run else ""))


if __name__ == "__main__":
    main()