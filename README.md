# TasteBoard Agent

TasteBoard Agent is a data-backed market research assistant built for the "Agents for Business" Kaggle capstone track. It takes a simple product idea from a founder and conducts automated research to generate a comprehensive feasibility report.

## Setup & Run

1. **Clone the repository and set up a virtual environment**:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```
2. **Install requirements**:
   ```bash
   pip install -r requirements.txt
   ```
3. **Configure API Keys**:
   Create a `.env` file in the root directory and add your keys (e.g. `GEMINI_API_KEY`).
4. **Run the Streamlit App**:
   ```bash
   streamlit run ui/app.py
   ```
5. **Use the App**:
   Enter your product idea in the text area and click "Run Analysis".

## Multi-Agent Architecture

TasteBoard employs a highly modular, multi-agent architecture controlled by a **Coordinator Agent**.

1. **Coordinator Agent** (`coordinator.py`): The central orchestrator. It establishes a single connection to the MCP server and executes sub-agents sequentially. Crucially, it injects a scoped `call_tool` capability into each sub-agent, strictly enforcing which agent can access which tool.
2. **Query Understanding Agent**: Translates raw ideas into structured queries (category, target users, keywords).
3. **Market Search Agent**: Searches the web/Product Hunt for competitors based on keywords.
4. **Evidence Collection Agent**: Gathers public metadata (ratings, review counts, pricing) for each competitor.
5. **Review Mining Agent**: Clusters user feedback into distinct complaints and feature gaps.
6. **Market Benchmark Agent**: Constructs a comparative baseline for the industry.
7. **Feasibility Scoring Agent**: Analyzes the benchmark data to compute an objective Founder Opportunity Score.
8. **Visualization Agent**: Leverages Plotly to dynamically generate data charts (Rating Bars, Volume Bars, Radar Charts).
9. **Report Agent**: Synthesizes the pipeline data and charts into a 12-section Markdown report.

---

## Folder Layout

*   **`mcp_server/`**: Contains the 9 tools (skills) built as a standard MCP server.
*   **`agents/`**: Contains the 8 specialized AI sub-agents.
*   **`coordinator.py`**: The orchestration and security layer.
*   **`ui/`**: The Streamlit web app interface.
*   **`data/`**: Mock datasets and generated reports.
*   **`eval/`**: Golden test cases for evaluating system correctness.
*   **`logs/`**: Structured JSON logging for tracing tool calls.
*   **`.agents/AGENTS.md`**: The strict guardrails and architecture rules guiding the system.

---

## Runbook / Troubleshooting Guide

If you encounter issues while running the TasteBoard Agent, follow this plain-language checklist:

### 1. The Pipeline Fails or Crashes
- **Check your API Key**: Ensure `.env` contains a valid `GEMINI_API_KEY`.
- **Check the Logs**: Open `logs/tool_calls.jsonl` to see which agent failed. If the last entry says "Error parsing LLM output", the LLM might have returned prose instead of JSON. Running the pipeline again usually resolves transient LLM parsing errors.
- **Check your Internet Connection**: The Market Search and Evidence Collection agents rely on live web searches. If they timeout, the pipeline will fail.

### 2. The Report Cites a Source That Doesn't Check Out
TasteBoard is strictly instructed *not* to hallucinate, but if you find a broken link or suspect a hallucinated rating:
- **Look at the Raw Evidence**: Open `logs/tool_calls.jsonl` and find the `collect_product_metadata` entry for that competitor. This log contains the exact data the system retrieved from the live web.
- **Is it a hallucination or just outdated?**: If the log contains the data, the system successfully scraped it (though the website might have updated since). If the log *does not* contain the data, the Report Agent hallucinated it. Please report this as an issue so we can tighten the LLM prompt.

### 3. Scores Look Inconsistent or Incorrect
- **Check the Review Volume**: The Feasibility Scoring Agent weighs metrics heavily based on the volume of reviews. A product with a 5.0 rating but only 2 reviews will score lower on "Trust" than a product with a 4.6 rating and 10,000 reviews.
- **Check for "Insufficient Evidence"**: If a competitor couldn't be fully scraped, it receives default/penalty scores to prevent over-optimism. This will reflect in a lower final Founder Opportunity Score.

### 4. Running the Evals
You can test the system's resilience and guardrails by running the automated evaluation suite:
```bash
python eval/run_evals.py
```
*Note: Set `export RUN_ALL_EVALS=true` to run all 9 realistic and adversarial cases instead of the quick 3-case subset.*
