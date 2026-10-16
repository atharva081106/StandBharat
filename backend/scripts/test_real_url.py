import asyncio
import sys
import os
sys.path.insert(0, os.path.abspath("."))
from app.services.website_analysis import WebsiteAnalysisService

async def main():
    target = sys.argv[1] if len(sys.argv) > 1 else "https://python.org"
    print(f"Analyzing real live URL: {target}...")
    result = await WebsiteAnalysisService.analyze_url(target)
    
    print("\n--- 1. REAL EXTRACTED TECHNICAL SEO METADATA ---")
    for k, v in result["metadata"].items():
        print(f"  {k:<22}: {v}")
        
    print("\n--- 2. REAL EXTRACTED BUSINESS & BRAND INTELLIGENCE ---")
    for k, v in result["analysis_results"].items():
        v_str = str(v).encode("ascii", "replace").decode("ascii")
        print(f"  {k:<22}: {v_str}")

if __name__ == "__main__":
    asyncio.run(main())
