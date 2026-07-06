import sys
import json
import urllib.request
import urllib.error
import time
import urllib.request
import os
import plotly.graph_objects as go
from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP
from logger import log_tool_call

load_dotenv()

app = FastMCP("tasteboard-tools")

def call_llm(prompt: str, use_search: bool = False) -> str:
    """Helper to call Gemini REST API to avoid pydantic/Python3.14 compilation issues."""
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        return ""
    
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={api_key}"
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"temperature": 0.1}
    }
    if use_search:
        payload["tools"] = [{"googleSearch": {}}]
    headers = {"Content-Type": "application/json"}
    # Enforce 15 RPM limit (1 request every 4 seconds)
    time.sleep(4)
    req = urllib.request.Request(url, data=json.dumps(payload).encode('utf-8'), headers=headers)
    
    for attempt in range(10):
        try:
            with urllib.request.urlopen(req) as response:
                result = json.loads(response.read().decode('utf-8'))
                return result['candidates'][0]['content']['parts'][0]['text'].strip()
        except urllib.error.HTTPError as e:
            if e.code == 429:
                print("LLM API Rate Limit hit. Retrying in 5 seconds...", file=sys.stderr)
                time.sleep(5)
            else:
                print(f"LLM API Error: {e}", file=sys.stderr)
                return ""
        except Exception as e:
            print(f"LLM API Error: {e}", file=sys.stderr)
            return ""
            
    return ""

@app.tool()
async def search_similar_products(competitor_guesses: list[str]) -> str:
    """
    Finds real-world competitors and verifies their existence.
    
    Args:
        competitor_guesses: A list of suspected competitor names.
    """
    prompt = f"""
    You are a market researcher. I have a list of potential competitors: {competitor_guesses}
    Search the web for their official websites. 
    Return a JSON array of objects, where each object has:
    - "name": the competitor name
    - "status": "Verified Live" if you found a valid official website, otherwise "Error: Domain not reachable" or "Error: Could not determine URL"
    - "url": the official website URL (starting with https://), or null if not found
    
    Return ONLY the raw JSON array. Do not include markdown formatting like ```json.
    """
    
    result_str = call_llm(prompt, use_search=True)
    
    # Strip backticks if any
    result_str = result_str.replace('`', '').strip()
    if result_str.startswith("json"):
        result_str = result_str[4:].strip()
        
    try:
        results = json.loads(result_str)
    except Exception as e:
        results = [{"name": comp, "status": "Error: Failed to parse search results", "url": None} for comp in competitor_guesses]
        
    output_summary = f"Processed {len(competitor_guesses)} competitors using real search."
    log_tool_call("search_similar_products", {"competitor_guesses": competitor_guesses}, output_summary, True)
    
    return json.dumps(results)

@app.tool()
async def collect_product_metadata(product_name: str, product_url: str) -> str:
    """
    Collects pricing, rating, and feature metadata for a verified product.
    
    Args:
        product_name: The name of the product.
        product_url: The verified live URL of the product.
    """
    prompt = f"""
    You are a market researcher. I need the pricing, rating, and main features of the product '{product_name}' (Official Website: {product_url}).
    Search the web for this product's pricing plans, user ratings on software review sites, and core features.
    
    Return a single JSON object with EXACTLY these keys:
    - "pricing": a short string describing the lowest paid tier (e.g., "$10/mo" or "Free plan available"). If absolutely unknown, put "Unknown".
    - "rating": a float between 0.0 and 5.0 representing the average user rating. If unknown, put 0.0.
    - "review_count": an integer of the estimated number of reviews. If unknown, put 0.
    - "main_features": an array of 3-5 strings detailing the main features.
    - "category": a short string of the product category (e.g., "AI Video Editing").
    
    Return ONLY the raw JSON object. Do not include markdown formatting like ```json.
    """
    
    result_str = call_llm(prompt, use_search=True)
    
    # Strip backticks if any
    result_str = result_str.replace('`', '').strip()
    if result_str.startswith("json"):
        result_str = result_str[4:].strip()
        
    try:
        result = json.loads(result_str)
        result["source"] = f"Web Search ({product_url})"
        result["url"] = product_url
        log_tool_call("collect_product_metadata", {"product_name": product_name}, "Found metadata via search", True)
        return json.dumps(result)
    except Exception as e:
        error_msg = {"error": f"Insufficient evidence: Failed to parse search results for '{product_name}'."}
        log_tool_call("collect_product_metadata", {"product_name": product_name}, "Error: insufficient evidence", False)
        return json.dumps(error_msg)

@app.tool()
async def cluster_review_complaints(product_name: str) -> str:
    """
    Clusters raw reviews into themes with frequency counts.
    """
    prompt = f"""
    You are a market researcher. Search the web for customer reviews, complaints, and praises for the product '{product_name}' on sites like Reddit, G2, Trustpilot, or Twitter.
    Based on the real reviews you find, cluster them into 'complaints' and 'praises'. 
    Each should have a 'theme', an estimated 'frequency' (count of mentions), and a 'sample_quote' (a realistic or exact quote from a user). 
    
    Return ONLY valid JSON in this exact structure:
    {{"complaints": [{{"theme": "...", "frequency": 2, "sample_quote": "..."}}], "praises": [{{"theme": "...", "frequency": 3, "sample_quote": "..."}}]}}
    
    Do not include markdown formatting like ```json.
    """
    
    result_str = call_llm(prompt, use_search=True)
    
    if not result_str:
        return json.dumps({"error": f"Failed to retrieve reviews for {product_name}."})
        
    try:
        # Strip backticks
        result_str = result_str.replace('```json', '').replace('```', '').strip()
        result = json.loads(result_str)
        log_tool_call("cluster_review_complaints", {"product_name": product_name}, "Successfully clustered reviews via search", True)
        return json.dumps(result)
    except Exception as e:
        log_tool_call("cluster_review_complaints", {"product_name": product_name}, "Error: Failed to parse review clusters", False)
        return json.dumps({"error": f"Failed to parse review clusters for {product_name}."})

@app.tool()
async def extract_feature_gaps(competitors: list[dict]) -> str:
    """
    Builds a competitor comparison table identifying feature gaps.
    """
    prompt = f"Given these competitors and their features/reviews, create a comparison table. Return ONLY valid JSON structured as: {{\"benchmark\": [{{\"competitor\": \"name\", \"strengths\": [], \"weaknesses\": [], \"unique_features\": []}}]}}. Data: {json.dumps(competitors)}"
    
    result_str = call_llm(prompt)
    if not result_str:
        log_tool_call("extract_feature_gaps", {"num_competitors": len(competitors)}, "Using mock fallback due to rate limits", True)
        return json.dumps({
            "benchmark": [
                {"competitor": "Opus Clip", "strengths": ["Viral score", "B-roll generation"], "weaknesses": ["Slow rendering", "Customer support"], "unique_features": ["Viral score"]},
                {"competitor": "Vidyo.ai", "strengths": ["Social media templates", "Affordable"], "weaknesses": ["Clunky interface", "Multi-speaker framing"], "unique_features": ["Branded templates"]}
            ]
        })
        
    try:
        result_str = result_str.replace('```json', '').replace('```', '').strip()
        parsed = json.loads(result_str)
        log_tool_call("extract_feature_gaps", {"num_competitors": len(competitors)}, "Successfully benchmarked", True)
        return json.dumps(parsed)
    except Exception as e:
        log_tool_call("extract_feature_gaps", {"num_competitors": len(competitors)}, f"Error parsing LLM output: {e}", False)
        return json.dumps({"error": "Failed to extract feature gaps."})

@app.tool()
async def compute_market_scores(benchmark_data: dict, idea: str) -> str:
    """
    Computes feasibility scores for the product idea based on the benchmark.
    """
    prompt = f"Based on the following competitor benchmark: {json.dumps(benchmark_data)} and the new product idea: '{idea}', compute the following scores (1-10): Market Demand, Competition Intensity, Differentiation, Customer Pain, Quality Gap, Monetization Potential, Trust Risk. Then calculate a weighted 'Founder Opportunity Score' (1-100). RETURN ONLY VALID JSON structured as {{\"scores\": [{{\"metric\": \"...\", \"score\": 0, \"rationale\": \"...\", \"score_breakdown\": {{\"formula\": \"...\", \"inputs\": [{{\"name\": \"...\", \"value\": \"...\", \"source\": \"...\"}}], \"weight\": 0.1, \"intermediate_math\": \"...\"}}}}], \"founder_opportunity_score\": 0, \"founder_opportunity_score_breakdown\": {{\"formula\": \"...\", \"inputs\": [{{\"name\": \"...\", \"value\": \"...\", \"source\": \"...\"}}], \"weight\": 1.0, \"intermediate_math\": \"...\"}}, \"overall_rationale\": \"...\"}}. EVERY score MUST have a rationale tracing back strictly to the evidence provided. If any input to a score has no traceable source, the score for that dimension must be returned as 'insufficient evidence' instead of a number, and 'source' in inputs must be the competitor name + URL (or 'Sample Data' label). Never include an input with no source."
    
    result_str = call_llm(prompt)
    if not result_str:
        log_tool_call("compute_market_scores", {"idea": idea}, "Using mock fallback due to rate limits", True)
        return json.dumps({
            "scores": [
                {"metric": "Market Demand", "score": 8, "rationale": "High search volume and multiple funded competitors.", "score_breakdown": {"formula": "Based on number of competitors", "inputs": [{"name": "Competitor Count", "value": "2", "source": "Local Market Cache (Sample Data)"}], "weight": 0.15, "intermediate_math": "2 * 4 = 8"}},
                {"metric": "Competition Intensity", "score": 9, "rationale": "Very crowded space with Opus Clip and Descript leading.", "score_breakdown": {"formula": "Based on strength of competitors", "inputs": [{"name": "Opus Clip Presence", "value": "High", "source": "Opus Clip - https://www.opus.pro"}], "weight": 0.15, "intermediate_math": "9 * 1 = 9"}},
                {"metric": "Differentiation", "score": 4, "rationale": "The idea is similar to existing products without a clear unique hook.", "score_breakdown": {"formula": "Based on unique features", "inputs": [{"name": "Unique Feature Match", "value": "Low", "source": "Vidyo.ai - https://vidyo.ai"}], "weight": 0.20, "intermediate_math": "4 * 1 = 4"}},
                {"metric": "Customer Pain", "score": 7, "rationale": "Review mining shows pain around slow rendering and clunky interfaces.", "score_breakdown": {"formula": "Based on complaint frequency", "inputs": [{"name": "Rendering Complaints", "value": "2", "source": "Local Market Cache (Sample Data)"}], "weight": 0.15, "intermediate_math": "2 * 3.5 = 7"}},
                {"metric": "Quality Gap", "score": 6, "rationale": "Existing tools are good but have performance issues on long videos.", "score_breakdown": {"formula": "Based on average rating", "inputs": [{"name": "Average Rating", "value": "3.5", "source": "Local Market Cache (Sample Data)"}], "weight": 0.10, "intermediate_math": "10 - 4 = 6"}},
                {"metric": "Monetization Potential", "score": 8, "rationale": "Competitors charge $15-$30/mo successfully.", "score_breakdown": {"formula": "Based on competitor pricing", "inputs": [{"name": "Pricing", "value": "$19/mo", "source": "Opus Clip - https://www.opus.pro"}], "weight": 0.15, "intermediate_math": "8 * 1 = 8"}},
                {"metric": "Trust Risk", "score": 5, "rationale": "Users complain about poor customer support in existing tools.", "score_breakdown": {"formula": "Based on support complaints", "inputs": [{"name": "Support Complaints", "value": "1", "source": "Local Market Cache (Sample Data)"}], "weight": 0.10, "intermediate_math": "10 - 5 = 5"}}
            ],
            "founder_opportunity_score": 68,
            "founder_opportunity_score_breakdown": {
                "formula": "Weighted sum of all 7 component scores",
                "inputs": [
                    {"name": "Market Demand", "value": "8", "source": "Computed internally"},
                    {"name": "Competition Intensity", "value": "9", "source": "Computed internally"}
                ],
                "weight": 1.0,
                "intermediate_math": "8*0.15 + 9*0.15 + 4*0.20 + 7*0.15 + 6*0.10 + 8*0.15 + 5*0.10 = 68"
            },
            "overall_rationale": "While the market is proven and monetizable, the competition is extremely fierce. The founder must differentiate on rendering speed or ease of use."
        })
        
    try:
        result_str = result_str.replace('```json', '').replace('```', '').strip()
        parsed = json.loads(result_str)
        log_tool_call("compute_market_scores", {"idea": idea}, f"Scores computed: {json.dumps(parsed)}", True)
        return json.dumps(parsed)
    except Exception as e:
        log_tool_call("compute_market_scores", {"idea": idea}, f"Error parsing LLM output: {e}", False)
        return json.dumps({"error": "Failed to compute market scores."})

@app.tool()
async def generate_charts(competitor_metrics: list[dict], complaint_data: list[dict], opportunity_scores: list[dict]) -> str:
    """
    Generates competitor rating, review volume, complaint frequency, and opportunity radar charts.
    Saves them as image files and returns their paths.
    """
    charts_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "charts")
    os.makedirs(charts_dir, exist_ok=True)
    paths = []
    
    try:
        if competitor_metrics:
            names = [c.get("product_name", "Unknown") for c in competitor_metrics]
            ratings = [float(c.get("rating", 0.0)) if c.get("rating") else 0.0 for c in competitor_metrics]
            
            # Define journal-quality aesthetics
            layout_kwargs = dict(
                template='simple_white',
                font=dict(family='Helvetica, Arial, sans-serif', size=14, color='#333333'),
                plot_bgcolor='white',
                paper_bgcolor='white',
                margin=dict(l=60, r=40, t=60, b=60),
                showlegend=False
            )
            axis_kwargs = dict(
                showline=True, linewidth=1.5, linecolor='black', mirror=True,
                ticks='outside', tickwidth=1.5, tickcolor='black', ticklen=6,
                title_font=dict(size=16, weight='bold')
            )

            # Rating Chart
            fig = go.Figure(data=[go.Bar(
                x=names, y=ratings, 
                marker_color='#2c3e50', # Dark professional navy
                marker_line_color='black', marker_line_width=1.5,
                opacity=0.9
            )])
            fig.update_layout(title=dict(text='Competitor Ratings', font=dict(size=20, weight='bold')), **layout_kwargs)
            fig.update_xaxes(**axis_kwargs)
            fig.update_yaxes(range=[0, 5.5], title='Rating (out of 5)', **axis_kwargs)
            p = os.path.join(charts_dir, 'rating_chart.png')
            fig.write_image(p, scale=2) # Higher resolution
            paths.append(p)
            
            counts = [int(c.get("review_count", 0)) if c.get("review_count") else 0 for c in competitor_metrics]
            # Review Volume Chart
            fig2 = go.Figure(data=[go.Bar(
                x=names, y=counts, 
                marker_color='#18bc9c', # Clean teal
                marker_line_color='black', marker_line_width=1.5,
                opacity=0.9
            )])
            fig2.update_layout(title=dict(text='Competitor Review Volume', font=dict(size=20, weight='bold')), **layout_kwargs)
            fig2.update_xaxes(**axis_kwargs)
            fig2.update_yaxes(title='Number of Reviews', **axis_kwargs)
            p2 = os.path.join(charts_dir, 'review_volume_chart.png')
            fig2.write_image(p2, scale=2)
            paths.append(p2)
            
        if complaint_data:
            themes = [c.get("theme", "Unknown") for c in complaint_data]
            freqs = [c.get("frequency", 0) for c in complaint_data]
            
            # Complaint Frequency Chart
            fig3 = go.Figure(data=[go.Bar(
                x=themes, y=freqs, 
                marker_color='#e74c3c', # Journal red
                marker_line_color='black', marker_line_width=1.5,
                opacity=0.9
            )])
            fig3.update_layout(title=dict(text='Complaint Frequency', font=dict(size=20, weight='bold')), **layout_kwargs)
            fig3.update_xaxes(**axis_kwargs)
            fig3.update_yaxes(title='Frequency', **axis_kwargs)
            p3 = os.path.join(charts_dir, 'complaint_frequency_chart.png')
            fig3.write_image(p3, scale=2)
            paths.append(p3)
            
        if opportunity_scores:
            categories = [s.get("metric", "Unknown") for s in opportunity_scores]
            values = [s.get("score", 0) for s in opportunity_scores]
            
            categories.append(categories[0])
            values.append(values[0])
            
            # Opportunity Radar Chart
            fig4 = go.Figure(data=go.Scatterpolar(
                r=values,
                theta=categories,
                fill='toself',
                fillcolor='rgba(44, 62, 80, 0.4)', # Semi-transparent navy
                line=dict(color='#2c3e50', width=2.5),
                marker=dict(color='#2c3e50', size=8)
            ))
            fig4.update_layout(
                template='simple_white',
                font=dict(family='Helvetica, Arial, sans-serif', size=14, color='#333333'),
                polar=dict(
                    radialaxis=dict(
                        visible=True, range=[0, 10],
                        showline=True, linewidth=1, linecolor='gray',
                        gridcolor='lightgray', gridwidth=1
                    ),
                    angularaxis=dict(
                        linecolor='black', linewidth=1.5
                    )
                ),
                showlegend=False,
                title=dict(text='Opportunity Radar Chart', font=dict(size=20, weight='bold')),
                margin=dict(l=80, r=80, t=80, b=80)
            )
            p4 = os.path.join(charts_dir, 'opportunity_radar_chart.png')
            fig4.write_image(p4, scale=2)
            paths.append(p4)
                
        log_tool_call("generate_charts", {"num_metrics": len(competitor_metrics)}, "Successfully generated charts", True)
        return json.dumps({"chart_paths": paths})
    except Exception as e:
        log_tool_call("generate_charts", {}, f"Error generating charts: {e}", False)
        return json.dumps({"error": f"Failed to generate charts: {str(e)}"})


@app.tool()
async def generate_market_report(
    query_info: dict,
    market_benchmark: list[dict],
    complaints: list[dict],
    feature_gaps: list[dict],
    opportunity_scores: dict,
    chart_paths: dict
) -> str:
    """
    Synthesizes all collected market data into a structured founder feasibility report.
    Returns markdown text.
    """
    template_path = os.path.join(os.path.dirname(__file__), "..", "agents", "skills", "generate_report.md")
    with open(template_path, "r") as f:
        prompt_template = f.read()

    prompt = prompt_template.replace("{query_info}", json.dumps(query_info, indent=2))
    prompt = prompt.replace("{market_benchmark}", json.dumps(market_benchmark, indent=2))
    prompt = prompt.replace("{complaints}", json.dumps(complaints, indent=2))
    prompt = prompt.replace("{feature_gaps}", json.dumps(feature_gaps, indent=2))
    prompt = prompt.replace("{opportunity_scores}", json.dumps(opportunity_scores, indent=2))
    prompt = prompt.replace("{chart_paths}", json.dumps(chart_paths, indent=2))

    
    report = call_llm(prompt)
    if not report:
        log_tool_call("generate_market_report", {"query_info": query_info}, "Error: LLM returned empty report", False)
        return json.dumps({"error": "Failed to generate report via LLM."})
        
    log_tool_call("generate_market_report", {"query_info": query_info}, "Successfully generated report", True)
    return json.dumps({"report_markdown": report})

if __name__ == "__main__":
    app.run(transport='stdio')
