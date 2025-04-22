# scripts/harvester.py
import sys
from pipeline.gpt_processors.insight_generator import generate_insight

if __name__ == "__main__":
    source = sys.argv[1]
    query = sys.argv[2]
    print("Running harvest...")
    result = generate_insight(source, query)
    print("\n=== INSIGHT ===\n")
    print(result)