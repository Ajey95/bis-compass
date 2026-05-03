from dataclasses import dataclass
from typing import List, Dict
import re


@dataclass
class Chunk:
    chunk_id: str
    standard_number: str
    title: str
    category: str
    content: str
    chunk_type: str  # "section_anchor" | "section_block" | "page_group" | "entry"
    parent_standard: str


def create_hierarchical_chunks(standards: List[Dict]) -> List[Chunk]:
    """
    Create section-aware chunks anchored to the BIS contents-page structure.

    Each standard becomes a compact, section-scoped chunk rather than a generic sliding window.
    This keeps the section title, standard number, and page-group context together.
    """
    chunks = []
    
    for std in standards:
        std_num = std["standard_number"]
        title = std["title"]
        category = std["category"]
        full_text = std["full_text"]
        pages = std.get("pages", [])
        start_page = std.get("start_page", -1)
        section_number = std.get("section_number", "")
        section_title = std.get("section_title", "")

        page_label = ""
        if pages:
            page_label = f"Pages: {pages[0] + 1} to {pages[-1] + 1}"
        elif start_page >= 0:
            page_label = f"Start page: {start_page + 1}"

        section_label = section_title if section_title else category

        # Compact section anchor for retrieval by section/topic words
        anchor_content = (
            f"SECTION {section_number or '?'} - {section_label}\n"
            f"Standard: {std_num}\n"
            f"Title: {title}\n"
            f"Category: {category}\n"
            f"{page_label}".strip()
        )
        chunks.append(Chunk(
            chunk_id=f"{std_num}_section_anchor",
            standard_number=std_num,
            title=title,
            category=category,
            content=anchor_content,
            chunk_type="section_anchor",
            parent_standard=std_num
        ))
        
        # Section block chunk keeps the actual ISO-name pages together for retrieval.
        block_lines = [
            f"SECTION {section_number or '?'} - {section_label}",
            f"Standard: {std_num}",
            f"Title: {title}",
            f"Category: {category}",
        ]
        if page_label:
            block_lines.append(page_label)
        block_lines.append("")
        block_lines.append(full_text[:4000])

        chunks.append(Chunk(
            chunk_id=f"{std_num}_section_block",
            standard_number=std_num,
            title=title,
            category=category,
            content="\n".join(block_lines),
            chunk_type="section_block",
            parent_standard=std_num
        ))

        # Lightweight entry chunk for title-specific matching.
        entry_content = f"{std_num} - {title}\n{section_label}\n{full_text[:1000]}"
        chunks.append(Chunk(
            chunk_id=f"{std_num}_entry",
            standard_number=std_num,
            title=title,
            category=category,
            content=entry_content,
            chunk_type="entry",
            parent_standard=std_num
        ))

        # Compact detail chunk restores some of the recall signal the older windowed
        # strategy had, without going back to many overlapping windows.
        detail_text = full_text[:1800]
        if detail_text:
            chunks.append(Chunk(
                chunk_id=f"{std_num}_detail",
                standard_number=std_num,
                title=title,
                category=category,
                content=f"{std_num}\n{section_label}\n{detail_text}",
                chunk_type="detail",
                parent_standard=std_num
            ))
    
    return chunks
