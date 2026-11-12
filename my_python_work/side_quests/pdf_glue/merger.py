"""Combine entire PDF documents in their supplied order, including duplicates."""

from contextlib import ExitStack
from dataclasses import dataclass
from pathlib import Path
import os
import sys
import tempfile
import webbrowser


@dataclass(frozen=True)
class MergeResult:
    path: Path
    file_count: int
    page_count: int
    size_bytes: int


def validate_paths(pdf_paths, output_path, *, overwrite=False):
    sources = tuple(Path(path).expanduser().resolve() for path in pdf_paths)
    if len(sources) < 2:
        raise ValueError("Add at least two PDFs. The same PDF can be included more than once.")
    for source in sources:
        if not source.is_file() or source.suffix.lower() != ".pdf":
            raise ValueError(f"Choose an existing PDF file: {source}")
        if not source.stat().st_size:
            raise ValueError(f"This PDF is empty: {source.name}")
    if not str(output_path).strip():
        raise ValueError("Choose where to save the merged PDF.")
    target = Path(output_path).expanduser().resolve()
    if target.suffix.lower() != ".pdf":
        raise ValueError("The output filename must end with .pdf.")
    if target in sources or (target.exists() and any(os.path.samefile(target, source) for source in sources)):
        raise ValueError("The output must be a different file from every input PDF.")
    if target.exists() and (not target.is_file() or not overwrite):
        raise FileExistsError("The output already exists. Choose another filename or allow replacement.")
    return sources, target


def merge_pdfs(pdf_paths, output_path, *, overwrite=False, progress=None):
    sources, target = validate_paths(pdf_paths, output_path, overwrite=overwrite)
    try:
        from pypdf import PdfReader, PdfWriter
        from pypdf.errors import PyPdfError
    except ImportError as error:
        raise RuntimeError("Install PDF Glue's requirements.txt with the Python interpreter you are using.") from error

    temporary = None
    try:
        with ExitStack() as resources, PdfWriter() as writer:
            page_count = 0
            for index, source in enumerate(sources, start=1):
                if progress:
                    progress(index, len(sources), source)
                try:
                    # Each occurrence gets its own reader and form namespace, even for the same path.
                    handle = resources.enter_context(source.open("rb"))
                    reader = PdfReader(handle)
                    if reader.is_encrypted:
                        raise ValueError("This version needs an unlocked PDF; save an unlocked copy first.")
                    count = len(reader.pages)
                    if not count:
                        raise ValueError("This PDF contains no pages.")
                    if reader.get_fields():
                        reader.add_form_topname(f"document_{index}")
                    writer.append(reader, outline_item=f"{index}. {source.stem}", import_outline=True)
                    page_count += count
                except (PyPdfError, ValueError, KeyError, IndexError, RecursionError, NotImplementedError) as error:
                    raise ValueError(f"Could not read or append {source.name}: {error}") from error
            writer.add_metadata({"/Title": target.stem, "/Producer": "PDF Glue (pypdf)"})
            target.parent.mkdir(parents=True, exist_ok=True)
            with tempfile.NamedTemporaryFile(prefix=".pdf-glue-", suffix=".pdf", dir=target.parent, delete=False) as handle:
                temporary = Path(handle.name)
                writer.write(handle)
            with temporary.open("rb") as handle:
                if len(PdfReader(handle).pages) != page_count:
                    raise RuntimeError("The merged PDF did not contain the expected number of pages.")
            # A failed merge never replaces an existing output. Exclusive publication also
            # protects a new output if another program creates that filename while we work.
            if overwrite:
                temporary.replace(target)
            elif os.name == "nt":
                temporary.rename(target)
            else:
                os.link(temporary, target)
                temporary.unlink()
            temporary = None
            return MergeResult(target, len(sources), page_count, target.stat().st_size)
    except PyPdfError as error:
        raise RuntimeError(f"Could not create the merged PDF: {error}") from error
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)


def open_pdf(path):
    path = Path(path).resolve()
    if sys.platform == "win32":
        os.startfile(str(path))
    else:
        webbrowser.open(path.as_uri())
