# TasteBoard Agent: How It Works

TasteBoard Agent uses a **Multi-Agent Architecture** to automatically evaluate the feasibility of startup product ideas. Given a raw idea, a team of specialized AI sub-agents orchestrates a complete market research pipeline, extracting real data, analyzing competitors, computing scores, and synthesizing a comprehensive founder report.

## The Architecture
The system consists of a **Coordinator Agent** managing 8 specialized **Sub-Agents**. To ensure strict separation of concerns and guard against hallucinations, the agents interact with external data strictly through an **MCP (Model Context Protocol) Server** exposing 9 specialized tools.

The Coordinator Agent enforces strict tool-calling permissions (e.g., the Report Agent cannot search the web, and the Market Search Agent cannot generate charts).

---

## The Step-by-Step Pipeline

When a user submits an idea, the Coordinator executes the following sequential pipeline:

### Phase 1: Query Understanding
* **Agent:** Query Understanding Agent (No external tools)
* **Action:** Takes the vague user idea and breaks it down into structured JSON containing:
  * **Category:** The broad industry (e.g., "AI Video Editing").
  * **Target Users:** Who the product is for.
  * **Keywords:** Search terms for finding competitors.
  * **Guess-list:** A list of likely competitors (e.g., "Opus Clip", "Descript").

### Phase 2: Market Search
* **Agent:** Market Search Agent
* **Tool:** `search_similar_products`
* **Action:** Takes the keywords and guess-list to search the web and Product Hunt for real, existing products in this space. It returns a confirmed list of competitors.

### Phase 3: Evidence Collection
* **Agent:** Evidence Collection Agent
* **Tools:** `collect_product_metadata`, `collect_product_reviews`
* **Action:** For every confirmed competitor, this agent fetches hard data:
  * **Metadata:** Pricing, main features, category.
  * **Reviews:** Ratings, review counts, and raw user feedback.
  * *Guardrail:* Every piece of collected data includes a source URL. Hallucinations are strictly prohibited.

### Phase 4: Review Mining
* **Agent:** Review Mining Agent
* **Tools:** `analyze_review_sentiment`, `cluster_review_complaints`
* **Action:** Processes the raw user reviews collected in Phase 3. It groups the reviews into overarching themes (e.g., "Inaccurate clipping", "High price") and counts their frequencies to determine the biggest unmet needs in the current market.

### Phase 5: Market Benchmark
* **Agent:** Market Benchmark Agent
* **Tool:** `extract_feature_gaps`
* **Action:** Compares the target idea against the analyzed competitors to build a feature matrix. It highlights areas where the current market is lacking (e.g., "No competitor offers reliable viral scoring").

### Phase 6: Feasibility Scoring
* **Agent:** Feasibility Scoring Agent
* **Tool:** `compute_market_scores`
* **Action:** Computes 8 specific scores (Market Demand, Competition Intensity, Differentiation, Customer Pain, Quality Gap, Monetization Potential, Trust Risk, and the final Founder Opportunity Score).
* **Score Transparency ("Show the math"):** For every score generated, the agent produces a `score_breakdown` containing the exact formula used, the specific competitor data points (inputs) that informed the score alongside their source URLs, and the weights applied. If any input lacks a traceable source, the score is returned as "insufficient evidence".

### Phase 7: Visualization
* **Agent:** Visualization Agent
* **Tool:** `generate_charts`
* **Action:** Takes the scored data and generates visual graphs (e.g., rating bar charts, complaint frequency charts, and opportunity radar charts) saving them to the local `data/charts/` directory.

### Phase 8: Report Generation
* **Agent:** Report Agent
* **Tool:** `generate_market_report`
* **Action:** Synthesizes all the evidence, scores, and charts into a final, structured Markdown report. It weaves the Score Transparency breakdowns into native HTML `<details>` and `<summary>` tags so that users can interactively "Show the math" for any computed score.

### Phase 9: UI Rendering
* **System:** Streamlit Frontend (`ui/app.py`)
* **Action:** Reads the final markdown report and renders it in the browser. It allows `unsafe_allow_html=True` to ensure the HTML `<details>` blocks for the score breakdowns are fully interactive.

---

## Guardrails
- **No Hallucinations:** Agents cannot invent competitor metrics. If real data is not found, the score is omitted or marked as "not found".
- **Source Tracing:** Every number in a score breakdown is traced back to a specific URL (or mock sample data) to prove its validity.
- **Single Responsibility:** Each tool performs exactly one job, keeping outputs structured and predictable.
