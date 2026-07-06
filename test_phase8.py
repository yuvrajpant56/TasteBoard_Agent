import asyncio
import os
from agents.report import run_report_agent

async def main():
    print("=== Phase 8: Report ===")
    
    # Mock data from previous phases
    query_info = {
        "category": "AI Video Editing",
        "target_users": ["Content Creators", "YouTubers"],
        "keywords": ["AI video repurposing", "shorts from long video"],
        "possible_competitors": ["Opus Clip", "Munch"]
    }
    
    market_benchmark = [
        {"product_name": "Opus Clip", "rating": 4.2, "review_count": 1500, "main_features": ["AI clipping", "Auto captions"], "source": "https://www.opus.pro"},
        {"product_name": "Descript", "rating": 4.7, "review_count": 3200, "main_features": ["Text-based editing", "Overdub"], "source": "https://www.descript.com"}
    ]
    
    complaints = [
        {"theme": "Opus Clip: Slow rendering", "frequency": 42},
        {"theme": "Descript: Crashing", "frequency": 55}
    ]
    
    feature_gaps = [
        {"feature": "Mobile-first editor", "gap_score": 8}
    ]
    
    opportunity_scores = [
        {"metric": "Market Demand", "score": 9},
        {"metric": "Quality Gap", "score": 8},
        {"metric": "Founder Opportunity Score", "score": 8.5}
    ]
    
    report = await run_report_agent(query_info, market_benchmark, complaints, feature_gaps, opportunity_scores)
    
    if report:
        out_dir = os.path.join(os.path.dirname(__file__), "data")
        os.makedirs(out_dir, exist_ok=True)
        report_path = os.path.join(out_dir, "feasibility_report.md")
        
        with open(report_path, "w") as f:
            f.write(report)
            
        print(f"Report successfully saved to {report_path}")
    else:
        print("Failed to generate report.")

if __name__ == "__main__":
    asyncio.run(main())
