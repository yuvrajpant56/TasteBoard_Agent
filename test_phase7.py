import asyncio
import os
import json
from agents.visualization import VisualizationAgent

async def main():
    server_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "mcp_server", "server.py"))
    
    agent = VisualizationAgent(server_script_path=server_path)
    
    # Mock data from Phase 3 & 4
    collected_evidence = [
        {
            "name": "Opus Clip",
            "status": "Verified Live",
            "evidence": {
                "rating": 4.2,
                "review_count": 1500
            },
            "reviews": {
                "complaints": [
                    {"theme": "Slow rendering", "frequency": 42},
                    {"theme": "Bad support", "frequency": 15}
                ]
            }
        },
        {
            "name": "Descript",
            "status": "Verified Live",
            "evidence": {
                "rating": 4.7,
                "review_count": 3200
            },
            "reviews": {
                "complaints": [
                    {"theme": "Crashing", "frequency": 55},
                    {"theme": "Learning curve", "frequency": 25}
                ]
            }
        },
        {
            "name": "Vidyo.ai",
            "status": "Verified Live",
            "evidence": {
                "rating": 3.9,
                "review_count": 800
            },
            "reviews": {
                "complaints": [
                    {"theme": "Clunky UI", "frequency": 30}
                ]
            }
        }
    ]
    
    feasibility_scores = {
        "scores": [
            {"metric": "Market Demand", "score": 9},
            {"metric": "Competition Intensity", "score": 8},
            {"metric": "Differentiation", "score": 7},
            {"metric": "Customer Pain", "score": 9},
            {"metric": "Quality Gap", "score": 8},
            {"metric": "Monetization Potential", "score": 9},
            {"metric": "Trust Risk", "score": 4}
        ],
        "founder_opportunity_score": 77
    }
    
    print("=== Phase 7: Visualization ===")
    paths = await agent.run(collected_evidence, feasibility_scores)
    
    for p in paths:
        print(f"Generated chart: {p}")

if __name__ == "__main__":
    asyncio.run(main())
