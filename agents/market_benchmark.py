import json

class MarketBenchmarkAgent:
    def __init__(self, call_tool_fn):
        self.call_tool = call_tool_fn

    async def run(self, clustered_evidence: list[dict]) -> dict:
        """
        Calls `extract_feature_gaps`.
        """
        # Filter out skipped products
        valid_competitors = [c for c in clustered_evidence if "error" not in c.get("reviews", {})]
        
        print(f"[Market Benchmark Agent] Benchmarking {len(valid_competitors)} competitors...")
        
        text_output = await self.call_tool(
            "extract_feature_gaps",
            {"competitors": valid_competitors}
        )
        benchmark_data = json.loads(text_output)
        
        return benchmark_data
