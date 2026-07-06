import json

class FeasibilityScoringAgent:
    def __init__(self, call_tool_fn):
        self.call_tool = call_tool_fn

    async def run(self, benchmark_data: dict, idea: str) -> dict:
        """
        Calls `compute_market_scores`.
        """
        print(f"[Feasibility Scoring Agent] Computing scores based on benchmark...")
        
        text_output = await self.call_tool(
            "compute_market_scores",
            {
                "benchmark_data": benchmark_data,
                "idea": idea
            }
        )
        scores_data = json.loads(text_output)
        
        return scores_data
