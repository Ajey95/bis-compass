import os
import json
import re
from typing import List, Dict
from dotenv import load_dotenv

load_dotenv(override=True)

try:
    from groq import Groq
except Exception:
    Groq = None


client = None
if Groq is not None and os.getenv("GROQ_API_KEY"):
    client = Groq(api_key=os.getenv("GROQ_API_KEY"))

GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.1-8b-instant")


def generate_rationale(query: str, standards: List[Dict]) -> List[Dict]:
    """
    Generate rationales for retrieved standards using Groq LLM.
    
    Uses anti-hallucination prompting to ensure only relevant standards are marked as high relevance.
    """
    
    # Build standards context for the prompt
    standards_context = "Retrieved Standards:\n"
    for i, std in enumerate(standards):
        std_num = std.get("metadata", {}).get("standard_number", "UNKNOWN")
        title = std.get("metadata", {}).get("title", "")
        content_excerpt = std.get("content", "")[:300]
        standards_context += f"\n{i+1}. {std_num}: {title}\n   Excerpt: {content_excerpt}...\n"
    
    prompt = f"""You are a BIS compliance expert helping Indian MSEs find relevant building material standards.

Product Description: {query}

{standards_context}

Your task: Evaluate each retrieved standard's relevance to the product description. For each standard, provide:
1. A 1-2 sentence rationale explaining why it might or might not apply
2. A relevance score: "high" (directly applicable), "medium" (potentially applicable), or "low" (not relevant)

CRITICAL ANTI-HALLUCINATION RULES:
- Only mark standards as "high" relevance if they clearly relate to the product
- If a standard seems unrelated, mark it "low" - do NOT invent connections
- Never invent standard numbers or requirements that weren't in the retrieved list
- Be conservative: when in doubt, mark as "medium" or "low"

Return ONLY valid JSON in this exact format (no markdown, no code blocks):
{{"rationales": [{{"standard_number": "IS 269:1989", "rationale": "Directly relevant for cement-based products.", "relevance": "high"}}, {{"standard_number": "IS 456:2000", "rationale": "Provides design codes but not directly relevant to raw cement.", "relevance": "medium"}}]}}"""
    
    if client is None:
        for std in standards:
            metadata = std.get("metadata", {})
            standard_number = metadata.get("standard_number", "UNKNOWN")
            title = metadata.get("title", standard_number)
            category = metadata.get("category", "General Building Materials")
            std["rationale"] = f"Retrieved from the BIS {category.lower()} corpus for query matching."
            std["relevance"] = "high" if standard_number.lower() in query.lower() or title.lower() in query.lower() else "medium"
        return standards

    try:
        # Call Groq API with a supported model
        message = client.chat.completions.create(
            model=GROQ_MODEL,
            temperature=0.3,
            max_tokens=1000,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        
        response_text = message.choices[0].message.content
        
        # Extract JSON from response using regex
        json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
        if json_match:
            try:
                json_data = json.loads(json_match.group())
                rationales_list = json_data.get("rationales", [])
                
                # Merge rationales back into standards
                for std in standards:
                    std_num = std.get("metadata", {}).get("standard_number", "")
                    
                    # Find matching rationale
                    matching_rationale = None
                    for rat in rationales_list:
                        if rat.get("standard_number", "") == std_num:
                            matching_rationale = rat
                            break
                    
                    if matching_rationale:
                        std["rationale"] = matching_rationale.get("rationale", "No rationale available")
                        std["relevance"] = matching_rationale.get("relevance", "medium")
                    else:
                        std["rationale"] = f"Standard {std_num} retrieved for query relevance evaluation"
                        std["relevance"] = "medium"
                
                return standards
            
            except json.JSONDecodeError:
                # If JSON parsing fails, add default rationales
                for std in standards:
                    title = std.get("metadata", {}).get("title", "")
                    std["rationale"] = f"Retrieved standard: {title}"
                    std["relevance"] = "medium"
                return standards
        else:
            # No JSON found in response
            for std in standards:
                std["rationale"] = "Standard retrieved from BIS database"
                std["relevance"] = "medium"
            return standards
    
    except Exception as e:
        # On any error, add safe defaults
        print(f"Warning: LLM call failed - {str(e)}")
        for std in standards:
            std["rationale"] = "Standard from BIS building materials collection"
            std["relevance"] = "medium"
        return standards
