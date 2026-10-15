"""Prepare a locally acquired PDF for source-linked extraction."""
import json
import shutil
from pathlib import Path
from pypdf import PdfReader
from .screening import normalize_doi


def prepare_pdf(path, output_dir, doi, title):
    doi = normalize_doi(doi)
    if not doi:
        raise ValueError('Valid DOI required for PDF intake')
    source, out = Path(path), Path(output_dir)
    reader = PdfReader(source)
    blocks = []
    for index, page in enumerate(reader.pages, 1):
        text = page.extract_text(extraction_mode='layout') or ''
        if text.strip():
            blocks.append({'locator': f'page:{index}', 'text': text, 'xml': None})
    if not blocks:
        raise ValueError('PDF has no extractable text; OCR or PDF image input is needed')
    out.mkdir(parents=True, exist_ok=True)
    if source.resolve() != (out / 'article.pdf').resolve():
        shutil.copyfile(source, out / 'article.pdf')
    (out / 'blocks.json').write_text(json.dumps(blocks, ensure_ascii=False, indent=2), encoding='utf-8')
    (out / 'metadata.json').write_text(json.dumps({'doi': doi, 'title': title, 'source_format': 'pdf',
        'source_url': 'https://doi.org/' + doi, 'pages': len(reader.pages)}, ensure_ascii=False, indent=2), encoding='utf-8')
    return len(blocks)
