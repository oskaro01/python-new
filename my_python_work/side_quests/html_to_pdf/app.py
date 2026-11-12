"""Run without arguments for the desktop UI, or pass an HTML path for the CLI."""

import argparse
import sys

if __package__:
    from .converter import BROWSERS, LAYOUTS, PAPERS, SOURCE_FORMATS, PdfOptions, convert_document, open_pdf
else:
    from converter import BROWSERS, LAYOUTS, PAPERS, SOURCE_FORMATS, PdfOptions, convert_document, open_pdf


def main(argv=None, *, source_format="html"):
    argv = sys.argv[1:] if argv is None else argv
    label, extensions = SOURCE_FORMATS[source_format]
    if not argv:
        if __package__:
            from .gui import launch
        else:
            from gui import launch
        launch(source_format=source_format)
        return 0
    parser = argparse.ArgumentParser(description=f"Convert a local {label} file to PDF using Chrome, Edge, or Chromium.")
    parser.add_argument("source", help=f"Local {' or '.join(extensions)} source file")
    parser.add_argument("-o", "--output", help="PDF output path; defaults to the source filename with .pdf")
    parser.add_argument("--browser", choices=sorted(BROWSERS), default="auto")
    parser.add_argument("--paper", choices=list(PAPERS), default="css", help="Respect HTML print CSS by default (A4 fallback)")
    parser.add_argument("--layout", choices=list(LAYOUTS), default="auto", help="Auto reformats recognized MHTML chats for pagination")
    parser.add_argument("--landscape", action="store_true", help="Requires an explicit paper size")
    parser.add_argument("--margin-mm", type=float, help="Override all page margins; otherwise preserve HTML CSS")
    parser.add_argument("--no-background", action="store_true")
    parser.add_argument("--timeout", type=float, default=30, help="Browser launch/loading/readiness budget, in seconds")
    parser.add_argument("--delay-ms", type=int, default=250, help="Extra rendering wait before checking assets")
    parser.add_argument("--wait-for", default="", metavar="SELECTOR", help="Wait for a visible CSS selector, e.g. '#ready'")
    parser.add_argument("--allow-missing-assets", action="store_true", help="Export even if images, fonts, or stylesheets fail")
    parser.add_argument("--force", action="store_true", help="Allow replacement of an existing output after successful conversion")
    parser.add_argument("--open", action="store_true", help="Open the completed PDF in the default viewer")
    args = parser.parse_args(argv)
    options = PdfOptions(
        paper=args.paper, landscape=args.landscape, margin_mm=args.margin_mm,
        background=not args.no_background, browser=args.browser, timeout_seconds=args.timeout,
        delay_ms=args.delay_ms, wait_selector=args.wait_for, allow_missing_assets=args.allow_missing_assets,
        layout=args.layout,
    )
    try:
        result = convert_document(args.source, args.output, options, overwrite=args.force, source_format=source_format)
    except (ValueError, OSError, RuntimeError) as error:
        print(f"Error: {error}", file=sys.stderr)
        return 1
    print(f"Created: {result.path}\nSize: {result.size_bytes:,} bytes | Browser: {result.browser}")
    print(f"Layout: {LAYOUTS[result.layout]}" + (f" | Messages: {result.message_count}" if result.message_count else ""))
    for warning in result.warnings:
        print(f"Warning: {warning}", file=sys.stderr)
    if args.open:
        try:
            open_pdf(result.path)
        except OSError as error:
            print(f"PDF saved, but the viewer could not open: {error}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
