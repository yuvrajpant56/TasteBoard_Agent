# TasteBoard Agent - Architecture & Guardrails

## Multi-Agent Architecture
This project uses a multi-agent architecture with a Coordinator Agent and 8 sub-agents. The workflow is executed in the following order:

1. **Query Understanding Agent**: Turns a vague idea into category, target users, keywords, and a guess-list of likely competitors (structured JSON output).
2. **Market Search Agent**: Searches for products matching those keywords.
3. **Evidence Collection Agent**: Collects rating, review_count, pricing, main_features, source (as structured JSON, never invented) for each product found.
4. **Review Mining Agent**: Clusters complaints and praises into themes with frequency counts.
5. **Market Benchmark Agent**: Builds a competitor comparison table.
6. **Feasibility Scoring Agent**: Computes Market Demand, Competition Intensity, Differentiation, Customer Pain, Quality Gap, Monetization Potential, Trust Risk, and a weighted Founder Opportunity Score — every number must trace back to collected evidence, never to LLM opinion alone.
7. **Visualization Agent**: Generates charts (rating bar chart, review volume bar chart, complaint frequency chart, opportunity radar chart) from the scored data.
8. **Report Agent**: Assembles everything into a structured founder report.

**Coordinator Agent**: Orchestrates all of the above.

## Hard Guardrails
- **No Hallucinations**: Never claim a product exists unless it was actually returned by a search. Never invent ratings, review counts, pricing, or user complaints.
- **Evidence-Backed**: Every piece of evidence used in the final report must cite its source (URL). If data is unavailable, output "not found" / "insufficient evidence" rather than guessing.
- **Structured Output**: Every tool returns structured JSON, not prose. Keep outputs concise — if a result would be large, summarize it and reference the full data rather than dumping it into the conversation.
- **Data Sources**: Prefer official APIs and public search results. No scraping paywalled, private, or ToS-restricted content.

## Tool Design Rules (MCP Server)
The MCP server exposes 9 tools: `search_similar_products`, `collect_product_metadata`, `collect_product_reviews`, `analyze_review_sentiment`, `cluster_review_complaints`, `extract_feature_gaps`, `compute_market_scores`, `generate_charts`, `generate_market_report`.
- **Clear Names**: Clear, specific names must be used.
- **Documentation**: Document every input and output parameter (type and purpose). Describe defaults where relevant. Keep parameter lists short.
- **Schemas**: Define an `inputSchema` and `outputSchema` for every tool and validate against them at runtime.
- **Single Responsibility**: One tool = one job. Don't bundle multiple steps into one "mega-tool."
- **Actionable Errors**: Error messages must be actionable — tell the caller what to do next (e.g., "No reviews found... Try with a broader product name").
- **Tool Scoping**: The Coordinator Agent enforces which tools each sub-agent may call.

## MVP Scope Constraints
- **Data Sources**: Product Hunt + general web search. Local mock/sample data is an acceptable stand-in for restricted sources (e.g., G2, Trustpilot) but must be labeled as "sample data" in reports.
- **Demo Case**: "I want to build an AI tool that helps creators repurpose long YouTube videos into short clips, captions, and social posts."
- **Tech Stack**: Python backend, Streamlit frontend.
- **Out of Scope**: Full CI/CD, canary rollout, cloud infra.
