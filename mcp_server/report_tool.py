@app.tool()
async def generate_market_report(
    query_info: dict,
    market_benchmark: list[dict],
    complaints: list[dict],
    feature_gaps: list[dict],
    opportunity_scores: list[dict]
) -> str:
    """
    Synthesizes all collected market data into a structured founder feasibility report.
    Returns markdown text.
    """
    prompt = f"""
    You are an expert market analyst and startup advisor.
    Synthesize the following research data into a clear, concise, and structured Founder Feasibility Report.
    The output must be formatted in Markdown.
    
    # Query Info (The Idea)
    {json.dumps(query_info, indent=2)}
    
    # Market Benchmark (Competitors & Evidence)
    {json.dumps(market_benchmark, indent=2)}
    
    # Customer Complaints (Themes)
    {json.dumps(complaints, indent=2)}
    
    # Feature Gaps (Unmet Needs)
    {json.dumps(feature_gaps, indent=2)}
    
    # Opportunity Scores
    {json.dumps(opportunity_scores, indent=2)}
    
    Requirements for the Report:
    1. Executive Summary: Brief verdict on the opportunity.
    2. Market Landscape: Summary of competitors and where they fall short.
    3. The Opportunity: What feature gaps and complaints create an opening.
    4. Scoring Breakdown: Explain the Founder Opportunity Score.
    5. Recommendations: 3 concrete next steps for the founder.
    
    Keep it professional, evidence-backed (cite numbers from the data where possible), and actionable.
    Do NOT hallucinate any numbers or competitors not in the data provided.
    """
    
    report = call_llm(prompt)
    if not report:
        log_tool_call("generate_market_report", {"query_info": query_info}, "Error: LLM returned empty report", False)
        return json.dumps({"error": "Failed to generate report via LLM."})
        
    log_tool_call("generate_market_report", {"query_info": query_info}, "Successfully generated report", True)
    return json.dumps({"report_markdown": report})
