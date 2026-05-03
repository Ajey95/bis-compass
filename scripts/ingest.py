#!/usr/bin/env python
"""
BIS-Compass Data Ingestion Script
Usage: python scripts/ingest.py --pdf data/bis_sp21.pdf

This script:
1. Parses the BIS SP 21 PDF
2. Extracts standards and section metadata
3. Creates section-aware chunks
4. Builds vector embeddings
5. Stores in ChromaDB for retrieval
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import argparse
from src.ingestion.pdf_parser import extract_standards
from src.ingestion.chunker import create_hierarchical_chunks
from src.ingestion.embedder import build_vector_store


def main():
    parser = argparse.ArgumentParser(
        description="Ingest BIS SP 21 PDF into ChromaDB vector store"
    )
    parser.add_argument(
        "--pdf",
        default="data/bis_sp21.pdf",
        help="Path to BIS SP 21 PDF file"
    )
    args = parser.parse_args()
    
    print("BIS-Compass Data Ingestion")
    print("=" * 50)
    
    # Step 1: Parse PDF
    print("\nStep 1/3: Parsing PDF...")
    try:
        standards = extract_standards(args.pdf)
        print(f"  ✓ Extracted {len(standards)} standards")
    except Exception as e:
        print(f"  ✗ Error parsing PDF: {e}")
        sys.exit(1)
    
    # Step 2: Create chunks
    print("\nStep 2/3: Creating hierarchical chunks...")
    try:
        chunks = create_hierarchical_chunks(standards)
        print(f"  ✓ Created {len(chunks)} chunks")
        print(f"    - Section anchor chunks: {len([c for c in chunks if c.chunk_type == 'section_anchor'])}")
        print(f"    - Section block chunks: {len([c for c in chunks if c.chunk_type == 'section_block'])}")
        print(f"    - Entry chunks: {len([c for c in chunks if c.chunk_type == 'entry'])}")
        print(f"    - Detail chunks: {len([c for c in chunks if c.chunk_type == 'detail'])}")
    except Exception as e:
        print(f"  ✗ Error creating chunks: {e}")
        sys.exit(1)
    
    # Step 3: Build vector store
    print("\nStep 3/3: Embedding and storing in ChromaDB...")
    try:
        build_vector_store(chunks, persist_dir="./chroma_db")
        print(f"  ✓ Vector store ready at ./chroma_db")
    except Exception as e:
        print(f"  ✗ Error building vector store: {e}")
        sys.exit(1)
    
    print("\n" + "=" * 50)
    print("✓ Ingestion complete. Ready for inference!")
    print("=" * 50)


if __name__ == "__main__":
    main()
