from __future__ import annotations

from datetime import datetime, timezone
from html import escape
from pathlib import Path
import re
import shutil

import markdown

ROOT = Path(__file__).resolve().parent
OBSIDIAN_SOURCE = Path(
    r"C:\Users\mjt\OneDrive\Documents\Obsidian Vault\Caribbean Basin Revisions\Caribbean Revisions.md"
)
SOURCE = ROOT / "Caribbean Revisions.md"
TARGET = ROOT / "index.html"
NOTE_PATTERN = re.compile(r"\[\[note:\s*(.+?)\s*\]\]", re.IGNORECASE | re.DOTALL)
AUTHOR_ONLY_PATTERN = re.compile(
    r"\[\[author-only\]\].*?\[\[/author-only\]\]",
    re.IGNORECASE | re.DOTALL,
)
AUTHOR_ONLY_MARKER_PATTERN = re.compile(
    r"^\s*\[\[/?author-only\]\]\s*$",
    re.IGNORECASE | re.MULTILINE,
)


def strip_author_only_blocks(markdown_text: str) -> str:
    markdown_text = AUTHOR_ONLY_PATTERN.sub("", markdown_text)
    return AUTHOR_ONLY_MARKER_PATTERN.sub("", markdown_text)


def inject_margin_notes(markdown_text: str) -> str:
    def replacer(match: re.Match[str]) -> str:
        # Optional syntax: [[note: Label | Message text]]
        raw_text = " ".join(match.group(1).split())
        label = "Revision note"
        note_text = raw_text
        if "|" in raw_text:
            maybe_label, maybe_text = raw_text.split("|", 1)
            maybe_label = maybe_label.strip()
            maybe_text = maybe_text.strip()
            if maybe_label and maybe_text:
                label = maybe_label
                note_text = maybe_text

        return (
            f'<span class="margin-note" role="note" data-label="{escape(label)}">'
            f"{escape(note_text)}"
            "</span>"
        )

    return NOTE_PATTERN.sub(replacer, markdown_text)


def sync_source_from_obsidian() -> None:
    if not OBSIDIAN_SOURCE.exists():
        raise FileNotFoundError(
            f"Obsidian source file not found: {OBSIDIAN_SOURCE}"
        )

    shutil.copy2(OBSIDIAN_SOURCE, SOURCE)


def build_site() -> None:
    sync_source_from_obsidian()
    source_text = SOURCE.read_text(encoding="utf-8")
    source_text = strip_author_only_blocks(source_text)
    source_text = inject_margin_notes(source_text)

    # Parse markdown with support for tables, footnotes, and standard markdown extras.
    article_html = markdown.markdown(
        source_text,
        extensions=["extra", "sane_lists"],
        output_format="html5",
    )

    generated_utc = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    html = f"""<!DOCTYPE html>
<html lang=\"en\">
<head>
    <meta charset=\"UTF-8\">
    <meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\">
    <title>Caribbean Revisions</title>
    <link rel=\"stylesheet\" href=\"style.css\">
</head>
<body>
    <header class=\"site-header\">
        <h1>Caribbean Revisions</h1>
        <p class=\"subtitle\">Living Essay</p>
        <p class=\"generated\">Generated from Caribbean Revisions.md on {generated_utc}</p>
    </header>
    <main>
{article_html}
    </main>
</body>
</html>
"""

    TARGET.write_text(html, encoding="utf-8")


if __name__ == "__main__":
    build_site()
    print(f"Synced {SOURCE.name} from Obsidian and built {TARGET.name}")
