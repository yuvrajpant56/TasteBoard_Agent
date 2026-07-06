import json

class EvidenceCollectionAgent:
    def __init__(self, call_tool_fn):
        self.call_tool = call_tool_fn

    async def run(self, verified_products: list[dict]) -> list[dict]:
        """
        Calls `collect_product_metadata` for each verified product.
        """
        results = []
        
        print(f"[Evidence Collection Agent] Collecting metadata for {len(verified_products)} products...")
        
        for product in verified_products:
            if product.get("status") == "Verified Live" and product.get("url"):
                text_output = await self.call_tool(
                    "collect_product_metadata",
                    {
                        "product_name": product["name"],
                        "product_url": product["url"]
                    }
                )
                metadata = json.loads(text_output)
                
                product_data = {**product, "evidence": metadata}
                results.append(product_data)
            else:
                print(f"  Skipping {product['name']} (Not verified live)")
                product_data = {**product, "evidence": {"error": "Insufficient evidence: Product not verified live."}}
                results.append(product_data)
                
        return results
