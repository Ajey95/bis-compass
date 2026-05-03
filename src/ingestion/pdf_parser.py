import pdfplumber
import re
from typing import List, Dict


def infer_category(text: str) -> str:
    """Infer category from text content using keyword matching."""
    text_lower = text.lower()
    
    cement_keywords = ["cement", "concrete", "mortar", "pozzolana", "cementitious"]
    if any(kw in text_lower for kw in cement_keywords):
        return "Cement & Concrete"
    
    steel_keywords = ["steel", "iron", "bar", "rod", "wire", "reinforcement", "rebar", "tmt"]
    if any(kw in text_lower for kw in steel_keywords):
        return "Steel & Iron"
    
    aggregate_keywords = ["aggregate", "sand", "gravel", "stone", "coarse", "fine", "granule"]
    if any(kw in text_lower for kw in aggregate_keywords):
        return "Aggregates"
    
    masonry_keywords = ["brick", "tile", "ceramic", "clay", "masonry", "block"]
    if any(kw in text_lower for kw in masonry_keywords):
        return "Masonry"
    
    timber_keywords = ["timber", "wood", "plywood", "bamboo", "lumber"]
    if any(kw in text_lower for kw in timber_keywords):
        return "Timber & Wood"
    
    return "General Building Materials"


def _detect_section_context(text: str) -> Dict[str, str]:
    """Extract a section number/title from a block of PDF text when present."""
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    for idx, line in enumerate(lines[:8]):
        match = re.search(r"\bSECTION\s+(\d+)\b", line, re.IGNORECASE)
        if not match:
            continue

        section_number = match.group(1)
        section_title = ""

        remainder = line[match.end():].strip(" :-\t")
        if remainder:
            section_title = remainder
        else:
            for follow in lines[idx + 1: idx + 4]:
                if len(follow) > 2 and follow.upper() == follow:
                    section_title = follow
                    break

        return {
            "section_number": section_number,
            "section_title": section_title or f"Section {section_number}",
        }

    return {"section_number": "", "section_title": ""}


def _normalize_standard_number(value: str) -> str:
    """Normalize BIS standard numbers so repeated matches collapse to one canonical form."""
    normalized = re.sub(r"\s+", " ", str(value).strip())
    normalized = re.sub(r"\s*:\s*", ":", normalized)
    normalized = re.sub(r"\s*\(\s*Part\s*(\d+)\s*\)", r" (Part \1)", normalized, flags=re.IGNORECASE)
    normalized = re.sub(r"\s+", " ", normalized).strip()
    return normalized


def extract_standards(pdf_path: str, page_group_size: int = 3) -> List[Dict]:
    """
    Parse BIS PDF and extract standards by detecting section headers on pages.

    Strategy:
    - Read PDF page-by-page and search for lines that look like BIS standard headers (e.g., "IS 269:1989", "IS 2185 (Part 2): 1983").
    - For each detected header, record the start page and collect the following `page_group_size` pages as the canonical chunk.

    Returns list of dicts with keys:
    - standard_number, title, full_text, category, start_page, pages (list of page indices)
    """
    standards = []

    header_pattern = re.compile(r"\b(IS\s+\d+(?:[-/]\d+)?(?:\s*\(Part\s*\d+\))?(?:\s*:\s*\d{4})?)\b", re.IGNORECASE)

    try:
        with pdfplumber.open(pdf_path) as pdf:
            num_pages = len(pdf.pages)
            page_texts = []
            for pnum, page in enumerate(pdf.pages, start=1):
                text = page.extract_text() or ""
                page_texts.append(text)

            # Scan pages for headers
            for i, text in enumerate(page_texts):
                # Look for a header anywhere on the page
                for line in text.splitlines():
                    m = header_pattern.search(line)
                    if m:
                        header = m.group(1).strip()
                        # Extract title: prefer remainder of the line after header, or next non-empty line
                        remainder = line[m.end():].strip()
                        title = remainder
                        if not title:
                            # search next lines on the same page
                            lines_after = text.splitlines()[text.splitlines().index(line) + 1:]
                            for la in lines_after:
                                la_strip = la.strip()
                                if la_strip:
                                    title = la_strip
                                    break

                        if not title:
                            title = f"Standard {header}"

                        start_page = i
                        end_page = min(num_pages, start_page + page_group_size)
                        pages = list(range(start_page, end_page))

                        # Concatenate page texts for the group
                        group_text = "\n".join(page_texts[p] for p in pages if p < len(page_texts))
                        section_context = _detect_section_context(group_text)

                        category = infer_category(group_text)

                        standards.append({
                            "standard_number": header,
                            "title": title[:200],
                            "full_text": group_text[:4000],
                            "category": category,
                            "section_number": section_context.get("section_number", ""),
                            "section_title": section_context.get("section_title", ""),
                            "start_page": start_page,
                            "pages": pages
                        })
                        # skip ahead to avoid duplicate detection on overlapping pages
                        break
    except FileNotFoundError:
        print(f"Warning: PDF not found at {pdf_path}. Using fallback standards.")
        fallback_standards = [
            {"standard_number": "IS 269:1989", "title": "Specification for 33 Grade Ordinary Portland Cement", "full_text": "Ordinary Portland cement (OPC) for concrete and mortar. High durability and strength.", "category": "Cement & Concrete", "section_number": "1", "section_title": "CEMENT AND CONCRETE", "start_page": -1, "pages": []},
            {"standard_number": "IS 1489-1:1991", "title": "Specification for Portland Pozzolana Cement", "full_text": "Pozzolana cement containing fly ash for improved durability and reduced heat generation.", "category": "Cement & Concrete", "section_number": "1", "section_title": "CEMENT AND CONCRETE", "start_page": -1, "pages": []},
            {"standard_number": "IS 456:2000", "title": "Code of Practice for Plain and Reinforced Concrete", "full_text": "Design and construction requirements for concrete structures including mix design and curing.", "category": "Cement & Concrete", "section_number": "1", "section_title": "CEMENT AND CONCRETE", "start_page": -1, "pages": []},
        ]
        return fallback_standards

    # If no standards detected via headers, fallback to heuristic split of full_text
    if not standards:
        # Combine all page texts and fallback to earlier behavior
        try:
            with pdfplumber.open(pdf_path) as pdf:
                full_text = "\n".join((page.extract_text() or "") for page in pdf.pages)
        except Exception:
            full_text = ""

        text_blocks = re.split(r'(?=IS\s+[\d\-]+)', full_text)
        for block in text_blocks[1:]:
            match = re.match(r'IS\s+([\d\-]+)\s*(?::\s*(\d{4}))?', block)
            if not match:
                continue
            std_num = match.group(1)
            year = match.group(2) if match.group(2) else ""
            standard_number = f"IS {std_num}:{year}" if year else f"IS {std_num}"
            lines = block.split('\n')
            title = ""
            for line in lines[1:]:
                line_clean = line.strip()
                if line_clean and not line_clean.startswith('IS '):
                    title = line_clean[:100]
                    break
            if not title:
                title = f"Building Material Standard {standard_number}"
            full_text_excerpt = block[:2000]
            category = infer_category(block)
            standards.append({
                "standard_number": standard_number,
                "title": title,
                "full_text": full_text_excerpt,
                "category": category,
                "section_number": "",
                "section_title": "",
                "start_page": -1,
                "pages": []
            })

    deduped = []
    seen = set()

    for standard in standards:
        standard_number = _normalize_standard_number(standard.get("standard_number", ""))
        if not standard_number:
            continue

        if standard_number in seen:
            continue

        seen.add(standard_number)
        standard["standard_number"] = standard_number
        deduped.append(standard)

    # Keep stable ordering by the first page where the standard was detected.
    deduped.sort(key=lambda item: item.get("start_page", -1))
    return deduped
