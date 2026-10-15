"""Prepare a locally acquired PDF for source-linked extraction."""
import json
import shutil
import re
from html.parser import HTMLParser
from pathlib import Path
from pypdf import PdfReader
from pypdf.errors import PdfReadError
from .screening import normalize_doi


class ArticleHTMLBlocks(HTMLParser):
    """Preserve public HTML paragraph/table text, without executing page scripts."""
    def __init__(self):
        super().__init__()
        self.active = None
        self.depth = 0
        self.content = []
        self.blocks = []
        self.skip = 0

    def handle_starttag(self, tag, attrs):
        if tag in ('script', 'style'):
            self.skip += 1
        if self.skip:
            return
        if self.active is None and tag in ('table', 'p', 'h1', 'h2', 'h3'):
            self.active, self.depth, self.content = tag, 1, []
        elif self.active == tag:
            self.depth += 1
        if self.active and tag in ('td', 'th', 'tr', 'br'):
            self.content.append(' ')

    def handle_endtag(self, tag):
        if tag in ('script', 'style'):
            self.skip = max(0, self.skip - 1)
            return
        if self.skip:
            return
        if self.active == tag:
            self.depth -= 1
            if self.depth == 0:
                text = re.sub(r'\s+', ' ', ' '.join(self.content)).strip()
                if text:
                    self.blocks.append({'locator': f'html-{tag}:{len(self.blocks)}', 'text': text, 'xml': None})
                self.active = None

    def handle_data(self, text):
        if self.active and not self.skip:
            self.content.append(text)


def prepare_html(path, output_dir, doi, title):
    doi = normalize_doi(doi)
    if not doi:
        raise ValueError('Valid DOI required for HTML intake')
    source, out = Path(path), Path(output_dir)
    parser = ArticleHTMLBlocks()
    parser.feed(source.read_text(encoding='utf-8'))
    if not parser.blocks:
        raise ValueError('No static HTML evidence blocks found')
    out.mkdir(parents=True, exist_ok=True)
    if source.resolve() != (out/'article.html').resolve():
        shutil.copyfile(source, out/'article.html')
    (out/'blocks.json').write_text(json.dumps(parser.blocks, ensure_ascii=False, indent=2), encoding='utf-8')
    (out/'metadata.json').write_text(json.dumps({'doi': doi, 'title': title, 'source_format': 'html',
        'source_url': 'https://doi.org/' + doi}, ensure_ascii=False, indent=2), encoding='utf-8')
    return len(parser.blocks)


def prepare_pdf(path, output_dir, doi, title):
    doi = normalize_doi(doi)
    if not doi:
        raise ValueError('Valid DOI required for PDF intake')
    source, out = Path(path), Path(output_dir)
    blocks = []
    integrity = 'standard_reader'
    try:
        reader = PdfReader(source)
        pages = len(reader.pages)
        texts = [page.extract_text(extraction_mode='layout') or '' for page in reader.pages]
    except PdfReadError:
        import pymupdf
        # Preserve the original bytes. Recovery is flagged, never silently certified.
        recovered = pymupdf.open(source)
        pages = len(recovered)
        texts = [page.get_text(sort=True) for page in recovered]
        integrity = 'recovered_reader_requires_visual_review'
    for index, text in enumerate(texts, 1):
        if text.strip():
            blocks.append({'locator': f'page:{index}', 'text': text, 'xml': None})
    if not blocks:
        raise ValueError('PDF has no extractable text; OCR or PDF image input is needed')
    out.mkdir(parents=True, exist_ok=True)
    if source.resolve() != (out / 'article.pdf').resolve():
        shutil.copyfile(source, out / 'article.pdf')
    (out / 'blocks.json').write_text(json.dumps(blocks, ensure_ascii=False, indent=2), encoding='utf-8')
    (out / 'metadata.json').write_text(json.dumps({'doi': doi, 'title': title, 'source_format': 'pdf',
        'source_url': 'https://doi.org/' + doi, 'pages': pages, 'source_integrity': integrity}, ensure_ascii=False, indent=2), encoding='utf-8')
    return len(blocks)
