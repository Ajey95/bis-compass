#!/usr/bin/env python
"""
Quick validation script to verify BIS-Compass setup
Run this before submitting to judges
"""

import sys
import json
import os
from pathlib import Path


def check_python_version():
    """Verify Python 3.10+"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 10):
        print(f"❌ Python {version.major}.{version.minor} detected. Need 3.10+")
        return False
    print(f"✅ Python {version.major}.{version.minor}.{version.micro}")
    return True


def check_dependencies():
    """Verify all required packages installed"""
    required = [
        'fastapi', 'uvicorn', 'pydantic', 'groq',
        'sentence_transformers', 'chromadb', 'rank_bm25',
        'pdfplumber', 'numpy', 'torch', 'dotenv'
    ]
    
    missing = []
    for pkg in required:
        try:
            __import__(pkg.replace('-', '_'))
        except ImportError:
            missing.append(pkg)
    
    if missing:
        print(f"❌ Missing packages: {', '.join(missing)}")
        print(f"   Run: pip install -r requirements.txt")
        return False
    
    print(f"✅ All {len(required)} dependencies installed")
    return True


def check_env_config():
    """Check if GROQ_API_KEY is set"""
    if not os.getenv('GROQ_API_KEY'):
        print("⚠️  GROQ_API_KEY not set. Set it before running:")
        print("   cp .env.example .env")
        print("   # Edit .env with your key")
        # Don't fail on this, just warn
        return True
    
    print("✅ GROQ_API_KEY configured")
    return True


def check_file_structure():
    """Verify critical files exist"""
    required_files = [
        'inference.py',
        'src/__init__.py',
        'src/pipeline.py',
        'src/api.py',
        'src/ingestion/pdf_parser.py',
        'src/ingestion/chunker.py',
        'src/ingestion/embedder.py',
        'src/retrieval/retriever.py',
        'src/retrieval/reranker.py',
        'src/generation/llm.py',
        'requirements.txt',
        'README.md'
    ]
    
    missing = []
    for f in required_files:
        if not Path(f).exists():
            missing.append(f)
    
    if missing:
        print(f"❌ Missing files: {', '.join(missing)}")
        return False
    
    print(f"✅ All {len(required_files)} critical files present")
    return True


def check_inference_script():
    """Verify inference.py has correct structure"""
    try:
        from src.pipeline import run_pipeline
        print("✅ Inference pipeline imports successfully")
        return True
    except Exception as e:
        print(f"❌ Cannot import pipeline: {e}")
        return False


def check_output_format():
    """Verify output JSON schema is correct"""
    sample_output = {
        "id": "q1",
        "retrieved_standards": ["IS 269:1989", "IS 456:2000"],
        "latency_seconds": 2.34
    }
    
    # Check all required keys
    required_keys = {"id", "retrieved_standards", "latency_seconds"}
    actual_keys = set(sample_output.keys())
    
    if required_keys != actual_keys:
        print(f"❌ Output schema mismatch. Need: {required_keys}")
        return False
    
    # Verify types
    if not isinstance(sample_output["id"], str):
        print("❌ 'id' must be string")
        return False
    
    if not isinstance(sample_output["retrieved_standards"], list):
        print("❌ 'retrieved_standards' must be list of strings")
        return False
    
    if not isinstance(sample_output["latency_seconds"], (int, float)):
        print("❌ 'latency_seconds' must be number")
        return False
    
    print("✅ Output JSON schema is correct")
    return True


def main():
    print("\n" + "="*50)
    print("BIS-Compass Setup Verification")
    print("="*50 + "\n")
    
    checks = [
        ("Python Version", check_python_version),
        ("Dependencies", check_dependencies),
        ("Environment Config", check_env_config),
        ("File Structure", check_file_structure),
        ("Inference Pipeline", check_inference_script),
        ("Output Schema", check_output_format),
    ]
    
    results = []
    for name, check_func in checks:
        print(f"\nChecking: {name}...")
        try:
            result = check_func()
            results.append(result)
        except Exception as e:
            print(f"❌ Unexpected error: {e}")
            results.append(False)
    
    print("\n" + "="*50)
    passed = sum(results)
    total = len(results)
    
    if all(results):
        print(f"✅ ALL CHECKS PASSED ({passed}/{total})")
        print("\nReady to run inference.py!")
        print("Command: python inference.py --input public_test_set.json --output results.json")
        return 0
    else:
        print(f"❌ SOME CHECKS FAILED ({passed}/{total})")
        print("\nPlease fix the issues above before submission.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
