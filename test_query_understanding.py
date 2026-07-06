import json
from agents.query_understanding import run_query_understanding

def main():
    demo_idea = "I want to build an AI tool that helps creators repurpose long YouTube videos into short clips, captions, and social posts."
    print("Testing Query Understanding Agent...")
    print(f"Input Idea: {demo_idea}\n")
    
    result = run_query_understanding(demo_idea)
    
    print("Agent Output (Structured JSON):")
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    main()
