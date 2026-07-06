import json

class VisualizationAgent:
    def __init__(self, call_tool_fn):
        self.call_tool = call_tool_fn

    async def run(self, collected_evidence: list[dict], feasibility_scores: dict) -> list[str]:
        """
        Calls `generate_charts` with market data.
        Returns a list of image paths.
        """
        print(f"[Visualization Agent] Generating market research charts...")
        
        # Extract competitor metrics
        competitor_metrics = []
        complaint_data = []
        
        for product in collected_evidence:
            if product.get("status") == "Verified Live" and "error" not in product.get("evidence", {}):
                evidence = product["evidence"]
                competitor_metrics.append({
                    "product_name": product["name"],
                    "rating": evidence.get("rating", 0.0),
                    "review_count": evidence.get("review_count", 0)
                })
                
                # Add reviews to complaint data if available
                if "reviews" in product and "complaints" in product["reviews"]:
                    for complaint in product["reviews"]["complaints"]:
                        complaint_data.append({
                            "theme": f"{product['name']}: {complaint['theme']}",
                            "frequency": complaint["frequency"]
                        })
        
        opportunity_scores = feasibility_scores.get("scores", [])
        
        text_output = await self.call_tool(
            "generate_charts",
            {
                "competitor_metrics": competitor_metrics,
                "complaint_data": complaint_data,
                "opportunity_scores": opportunity_scores
            }
        )
        parsed = json.loads(text_output)
        
        if "error" in parsed:
            print(f"Error generating charts: {parsed['error']}")
            return []
        else:
            paths = parsed.get("chart_paths", [])
            print(f"Successfully generated {len(paths)} charts.")
            return paths
