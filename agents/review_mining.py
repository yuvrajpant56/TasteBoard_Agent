import json

class ReviewMiningAgent:
    def __init__(self, call_tool_fn):
        self.call_tool = call_tool_fn

    async def run(self, collected_evidence: list[dict]) -> list[dict]:
        """
        Calls `cluster_review_complaints` for each product.
        """
        results = []
        
        print(f"[Review Mining Agent] Clustering reviews for products...")
        
        for product in collected_evidence:
            if product.get("status") == "Verified Live" and "error" not in product.get("evidence", {}):
                print(f"  Clustering reviews for {product['name']}...")
                text_output = await self.call_tool(
                    "cluster_review_complaints",
                    {"product_name": product["name"]}
                )
                clusters = json.loads(text_output)
                
                product_data = {**product, "reviews": clusters}
                results.append(product_data)
            else:
                print(f"  Skipping {product['name']} (No valid evidence)")
                product_data = {**product, "reviews": {"error": "Skipped due to insufficient evidence."}}
                results.append(product_data)
                
        return results
