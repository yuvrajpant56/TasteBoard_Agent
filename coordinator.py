import os
import sys
import json
import asyncio
from mcp.client.session import ClientSession
from mcp.client.stdio import stdio_client, StdioServerParameters

from agents.query_understanding import run_query_understanding
from agents.market_search import MarketSearchAgent
from agents.evidence_collection import EvidenceCollectionAgent
from agents.review_mining import ReviewMiningAgent
from agents.market_benchmark import MarketBenchmarkAgent
from agents.feasibility_scoring import FeasibilityScoringAgent
from agents.visualization import VisualizationAgent
from agents.report import ReportAgent

class Coordinator:
    def __init__(self, server_script_path: str):
        self.server_params = StdioServerParameters(
            command=sys.executable,
            args=[server_script_path],
        )
        self.session = None

        self.allowed_tools = {
            "Query Understanding Agent": [],
            "Market Search Agent": ["search_similar_products"],
            "Evidence Collection Agent": ["collect_product_metadata", "collect_product_reviews"],
            "Review Mining Agent": ["analyze_review_sentiment", "cluster_review_complaints"],
            "Market Benchmark Agent": ["extract_feature_gaps"],
            "Feasibility Scoring Agent": ["compute_market_scores"],
            "Visualization Agent": ["generate_charts"],
            "Report Agent": ["generate_market_report"]
        }

    def get_tool_caller(self, agent_name: str):
        """
        Returns a bound function that checks permissions before calling the tool.
        """
        async def call_tool(tool_name: str, arguments: dict) -> str:
            if tool_name not in self.allowed_tools.get(agent_name, []):
                raise PermissionError(f"[{agent_name}] is NOT authorized to call tool: {tool_name}")
            
            print(f"[{agent_name}] Calling tool: {tool_name}")
            result = await self.session.call_tool(tool_name, arguments=arguments)
            return result.content[0].text
        
        return call_tool

    async def run_pipeline(self, idea: str):
        print(f"=== Starting TasteBoard Pipeline ===")
        print(f"Product Idea: {idea}\n")
        
        async with stdio_client(self.server_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                self.session = session
                
                # Phase 1: Query Understanding
                print("--- Phase 1: Query Understanding ---")
                query_info = run_query_understanding(idea)
                
                # Phase 2: Market Search
                print("\n--- Phase 2: Market Search ---")
                market_search_agent = MarketSearchAgent(self.get_tool_caller("Market Search Agent"))
                competitors = await market_search_agent.run(query_info)
                
                # Phase 3: Evidence Collection
                print("\n--- Phase 3: Evidence Collection ---")
                evidence_collection_agent = EvidenceCollectionAgent(self.get_tool_caller("Evidence Collection Agent"))
                collected_evidence = await evidence_collection_agent.run(competitors)
                
                # Phase 4: Review Mining
                print("\n--- Phase 4: Review Mining ---")
                review_mining_agent = ReviewMiningAgent(self.get_tool_caller("Review Mining Agent"))
                clustered_evidence = await review_mining_agent.run(collected_evidence)
                
                # Phase 5: Market Benchmark
                print("\n--- Phase 5: Market Benchmark ---")
                market_benchmark_agent = MarketBenchmarkAgent(self.get_tool_caller("Market Benchmark Agent"))
                benchmark_data = await market_benchmark_agent.run(clustered_evidence)
                
                # Phase 6: Feasibility Scoring
                print("\n--- Phase 6: Feasibility Scoring ---")
                feasibility_scoring_agent = FeasibilityScoringAgent(self.get_tool_caller("Feasibility Scoring Agent"))
                scores = await feasibility_scoring_agent.run(benchmark_data, idea)
                
                # Phase 7: Visualization
                print("\n--- Phase 7: Visualization ---")
                visualization_agent = VisualizationAgent(self.get_tool_caller("Visualization Agent"))
                chart_paths = await visualization_agent.run(clustered_evidence, scores)
                
                # Convert list of paths into a dictionary mapping for the report prompt
                chart_paths_dict = {}
                for path in chart_paths:
                    filename = os.path.basename(path)
                    if "rating" in filename: chart_paths_dict["Rating Chart"] = path
                    elif "review" in filename: chart_paths_dict["Review Volume Chart"] = path
                    elif "complaint" in filename: chart_paths_dict["Complaint Frequency Chart"] = path
                    elif "radar" in filename: chart_paths_dict["Opportunity Radar Chart"] = path
                
                # Phase 8: Report Generation
                print("\n--- Phase 8: Report Generation ---")
                report_agent = ReportAgent(self.get_tool_caller("Report Agent"))
                
                # We need to extract just the complaints array for the report
                complaints = []
                for product in clustered_evidence:
                    if "reviews" in product and "complaints" in product["reviews"]:
                        complaints.extend(product["reviews"]["complaints"])
                
                feature_gaps = benchmark_data.get("feature_gaps", [])
                opportunity_scores = scores
                
                report = await report_agent.run(
                    query_info=query_info,
                    market_benchmark=benchmark_data.get("competitors", []),
                    complaints=complaints,
                    feature_gaps=feature_gaps,
                    opportunity_scores=opportunity_scores,
                    chart_paths=chart_paths_dict
                )
                
                if report:
                    output_path = os.path.join("data", "feasibility_report.md")
                    with open(output_path, "w") as f:
                        f.write(report)
                    print(f"\n✅ Pipeline Complete! Report saved to: {output_path}")
                    return report, chart_paths_dict
                else:
                    print("\n❌ Pipeline failed at report generation.")
                    return None, None

def main():
    demo_idea = "I want to build an AI tool that helps creators repurpose long YouTube videos into short clips, captions, and social posts."
    server_path = os.path.join(os.path.dirname(__file__), "mcp_server", "server.py")
    
    coordinator = Coordinator(server_path)
    asyncio.run(coordinator.run_pipeline(demo_idea))

if __name__ == "__main__":
    main()
