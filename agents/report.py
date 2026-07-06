import json

class ReportAgent:
    def __init__(self, call_tool_fn):
        self.call_tool = call_tool_fn

    async def run(self, query_info, market_benchmark, complaints, feature_gaps, opportunity_scores, chart_paths) -> str:
        """
        Calls `generate_market_report` to create the final markdown report.
        """
        print("[Report Agent] Synthesizing final founder report...")
        
        text_output = await self.call_tool(
            "generate_market_report",
            {
                "query_info": query_info,
                "market_benchmark": market_benchmark,
                "complaints": complaints,
                "feature_gaps": feature_gaps,
                "opportunity_scores": opportunity_scores,
                "chart_paths": chart_paths
            }
        )
        
        parsed = json.loads(text_output)
        
        if "error" in parsed:
            print(f"Error: {parsed['error']}")
            return None
            
        report_markdown = parsed.get("report_markdown", "")
        return report_markdown
