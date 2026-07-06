import asyncio
import json
import os
from agents.query_understanding import run_query_understanding
from agents.market_search import MarketSearchAgent
from agents.evidence_collection import EvidenceCollectionAgent
from agents.review_mining import ReviewMiningAgent
from agents.market_benchmark import MarketBenchmarkAgent
from agents.feasibility_scoring import FeasibilityScoringAgent

async def main():
    demo_idea = "I want to build an AI tool that helps creators repurpose long YouTube videos into short clips, captions, and social posts."
    server_path = os.path.join(os.path.dirname(__file__), "mcp_server", "server.py")
    
    print("=== Phase 1: Query Understanding ===")
    query_result = run_query_understanding(demo_idea)
    
    print("\n=== Phase 2: Market Search ===")
    search_agent = MarketSearchAgent(server_path)
    search_result = await search_agent.run(query_result)
    
    print("\n=== Phase 3: Evidence Collection ===")
    evidence_agent = EvidenceCollectionAgent(server_path)
    evidence_result = await evidence_agent.run(search_result)
    
    print("\n=== Phase 4.1: Review Mining ===")
    review_agent = ReviewMiningAgent(server_path)
    review_result = await review_agent.run(evidence_result)
    
    print("\n=== Phase 4.2: Market Benchmark ===")
    benchmark_agent = MarketBenchmarkAgent(server_path)
    benchmark_result = await benchmark_agent.run(review_result)
    print(json.dumps(benchmark_result, indent=2))
    
    print("\n=== Phase 4.3: Feasibility Scoring ===")
    scoring_agent = FeasibilityScoringAgent(server_path)
    scores_result = await scoring_agent.run(benchmark_result, demo_idea)
    print(json.dumps(scores_result, indent=2))
    
if __name__ == "__main__":
    asyncio.run(main())
