import json

class MarketSearchAgent:
    def __init__(self, call_tool_fn):
        """
        :param call_tool_fn: async function(tool_name, arguments) -> str
        """
        self.call_tool = call_tool_fn

    async def run(self, query_understanding_output: dict) -> list[dict]:
        """
        Calls `search_similar_products` with the competitor_guesses.
        """
        guesses = query_understanding_output.get("possible_competitors", [])
        print(f"[Market Search Agent] Calling MCP tool 'search_similar_products' with {len(guesses)} guesses...")
        
        text_output = await self.call_tool(
            "search_similar_products", 
            {"competitor_guesses": guesses}
        )
        
        return json.loads(text_output)
