"""Run without arguments for the desktop window, or list PDFs for the CLI."""

import argparse
import sys

if __package__:
    from .merger import merge_pdfs, open_pdf
else:
    from merger import merge_pdfs, open_pdf


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    if not argv:
        if __package__:
            from .gui import launch
        else:
            from gui import launch
        launch()
        return 0
    parser = argparse.ArgumentParser(description="Merge whole PDFs in the listed order; repeated files are kept.")
    parser.add_argument("pdfs", nargs="+", help="Input PDFs in the desired order")
    parser.add_argument("-o", "--output", required=True, help="Where to save the merged PDF")
    parser.add_argument("--force", action="store_true", help="Allow replacement of an existing output")
    parser.add_argument("--open", action="store_true", help="Open the completed PDF")
    args = parser.parse_args(argv)
    try:
        result = merge_pdfs(args.pdfs, args.output, overwrite=args.force,
                            progress=lambda index, total, path: print(f"[{index}/{total}] {path.name}"))
    except (ValueError, OSError, RuntimeError) as error:
        print(f"Error: {error}", file=sys.stderr)
        return 1
    print(f"Created: {result.path}\nPDFs: {result.file_count} | Pages: {result.page_count} | Size: {result.size_bytes:,} bytes")
    if args.open:
        try:
            open_pdf(result.path)
        except OSError as error:
            print(f"PDF saved, but the viewer could not open: {error}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
