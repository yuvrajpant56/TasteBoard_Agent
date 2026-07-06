import asyncio
import json
import os
from agents.query_understanding import run_query_understanding
from agents.market_search import MarketSearchAgent
from agents.evidence_collection import EvidenceCollectionAgent

async def main():
    print("=== Phase 1: Query Understanding ===")
    demo_idea = "I want to build an AI tool that helps creators repurpose long YouTube videos into short clips, captions, and social posts."
    query_result = run_query_understanding(demo_idea)
    print(json.dumps(query_result, indent=2))
    
    server_path = os.path.join(os.path.dirname(__file__), "mcp_server", "server.py")
    
    print("\n=== Phase 2: Market Search ===")
    search_agent = MarketSearchAgent(server_path)
    search_result = await search_agent.run(query_result)
    print(json.dumps(search_result, indent=2))
    
    print("\n=== Phase 3: Evidence Collection ===")
    evidence_agent = EvidenceCollectionAgent(server_path)
    evidence_result = await evidence_agent.run(search_result)
    print(json.dumps(evidence_result, indent=2))
    
    print("\n=== Logs Written to logs/tool_calls.jsonl ===")

if __name__ == "__main__":
    asyncio.run(main())
