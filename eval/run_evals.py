import os
import sys
import json
import asyncio
import re

# Add parent directory to path so we can import the coordinator
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from coordinator import Coordinator

LOGS_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "logs", "tool_calls.jsonl")

def get_logged_competitors_and_scores():
    """Parses tool_calls.jsonl to extract real competitor names and valid score metrics seen in logs."""
    competitors = set()
    scores = {}
    
    if not os.path.exists(LOGS_FILE):
        return competitors, scores
        
    with open(LOGS_FILE, 'r') as f:
        for line in f:
            try:
                log_entry = json.loads(line)
                tool_name = log_entry.get("tool_name", "")
                
                # Check for metadata collection to find real competitor names
                if tool_name == "collect_product_metadata" and log_entry.get("success"):
                    if "product_name" in log_entry.get("input", {}):
                        competitors.add(log_entry["input"]["product_name"].lower())
                
                # Check for computed scores
                if tool_name == "compute_market_scores" and log_entry.get("success"):
                    output_summary = log_entry.get("output_summary", "")
                    if output_summary.startswith("Scores computed:"):
                        try:
                            scores_json = output_summary.replace("Scores computed: ", "").strip()
                            scores = json.loads(scores_json)
                        except:
                            pass
            except json.JSONDecodeError:
                continue
                
    return competitors, scores

async def run_evaluation(test_case, coordinator):
    print(f"\n[{test_case['id']}] Starting Evaluation...")
    print(f"Idea: {test_case['idea']}")
    
    result = {
        "id": test_case["id"],
        "type": test_case["type"],
        "crashed": False,
        "hallucinated": False,
        "adversarial_passed": None,
        "overall": "FAIL"
    }
    
    # Clear logs before run
    if os.path.exists(LOGS_FILE):
        os.remove(LOGS_FILE)
        
    try:
        report, _ = await coordinator.run_pipeline(test_case["idea"])
        if not report:
            result["crashed"] = True
            return result
            
        # Parse logs to see what was ACTUALLY found
        logged_competitors, logged_scores = get_logged_competitors_and_scores()
        
        # Check for hallucination
        # We look for markdown tables in the report indicating competitors
        report_competitors = []
        for line in report.split('\n'):
            if '|' in line and not line.startswith('|---'):
                parts = [p.strip() for p in line.split('|') if p.strip()]
                if len(parts) > 1 and parts[0].lower() != 'competitor':
                    # First column is usually competitor name
                    report_competitors.append(parts[0].lower())
        
        # Ensure every competitor listed in the report's tables actually exists in the logs
        # Note: We skip generic terms that might appear in tables
        for comp in report_competitors:
            # Clean up potential markdown links like [Name](url)
            comp_clean = re.sub(r'\[(.*?)\]\(.*?\)', r'\1', comp).strip().lower()
            if comp_clean and comp_clean not in ['competitor', 'metric', 'theme', 'score']:
                # If a competitor in the report isn't in the logged valid evidence:
                # We check if it's a substring match to be safe
                found = any(comp_clean in c for c in logged_competitors) or any(c in comp_clean for c in logged_competitors)
                if not found and comp_clean not in ["not found", "insufficient evidence", "n/a", "none"]:
                    result["hallucinated"] = True
                    print(f"  ❌ Hallucination detected: {comp_clean} was in report but not in logs!")
                    
        # Check score transparency breakdowns for hallucinations
        if isinstance(logged_scores, dict):
            breakdowns = []
            if "scores" in logged_scores:
                for s in logged_scores["scores"]:
                    if "score_breakdown" in s:
                        breakdowns.append(s["score_breakdown"])
            if "founder_opportunity_score_breakdown" in logged_scores:
                breakdowns.append(logged_scores["founder_opportunity_score_breakdown"])
                
            for b in breakdowns:
                for inp in b.get("inputs", []):
                    source = str(inp.get("source", "")).strip().lower()
                    if not source:
                        result["hallucinated"] = True
                        print(f"  ❌ Hallucination detected: Empty source in score breakdown!")
                        continue
                    
                    if "sample data" in source or "computed internally" in source or source in ["not found", "insufficient evidence", "n/a", "none"]:
                        continue
                        
                    # Check if the source contains one of the logged competitors
                    found = any(c in source for c in logged_competitors)
                    if not found:
                        result["hallucinated"] = True
                        print(f"  ❌ Hallucination detected: Score breakdown source '{source}' does not match any logged competitor!")

        # Check adversarial specifically
        if test_case["type"] == "adversarial":
            # It should say insufficient evidence, not found, or not have hallucinated competitors
            if result["hallucinated"]:
                result["adversarial_passed"] = False
            else:
                lower_report = report.lower()
                if "insufficient evidence" in lower_report or "not found" in lower_report or len(logged_competitors) == 0:
                    result["adversarial_passed"] = True
                else:
                    # If it didn't hallucinate but still didn't explicitly say insufficient evidence when it found 0 things
                    result["adversarial_passed"] = False
                    
        # Overall assessment
        if result["crashed"]:
            result["overall"] = "FAIL (Crashed)"
        elif result["hallucinated"]:
            result["overall"] = "FAIL (Hallucinated)"
        elif test_case["type"] == "adversarial" and not result["adversarial_passed"]:
            result["overall"] = "FAIL (Adversarial Guardrail Missed)"
        else:
            result["overall"] = "PASS"
            
    except Exception as e:
        print(f"  ❌ Exception during pipeline: {e}")
        result["crashed"] = True
        result["overall"] = "FAIL (Crashed)"
        
    return result

async def main():
    test_cases_path = os.path.join(os.path.dirname(__file__), "test_cases.json")
    with open(test_cases_path, "r") as f:
        test_cases = json.load(f)
        
    server_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "mcp_server", "server.py")
    coordinator = Coordinator(server_path)
    
    results = []
    
    # For speed and API limit safety, we might just run 3 for demonstration if not overridden
    # But by default, run all.
    run_all = os.environ.get("RUN_ALL_EVALS", "false").lower() == "true"
    if not run_all:
        print("Note: Running a fast subset of 3 cases (2 realistic, 1 adversarial). Set RUN_ALL_EVALS=true to run all 9.")
        test_cases = [test_cases[0], test_cases[1], test_cases[6]]

    for tc in test_cases:
        res = await run_evaluation(tc, coordinator)
        results.append(res)
        
    print("\n" + "="*80)
    print("📋 EVALUATION SUMMARY")
    print("="*80)
    print(f"{'Test Case ID':<35} | {'Type':<12} | {'Crashed':<8} | {'Hallucinated':<12} | {'Overall':<10}")
    print("-" * 80)
    
    passed = 0
    for r in results:
        crashed_str = "Yes" if r["crashed"] else "No"
        hallucinated_str = "Yes" if r["hallucinated"] else "No"
        
        print(f"{r['id']:<35} | {r['type']:<12} | {crashed_str:<8} | {hallucinated_str:<12} | {r['overall']}")
        if r['overall'] == "PASS":
            passed += 1
            
    print("-" * 80)
    print(f"Total Passed: {passed}/{len(results)}")
    print("="*80)

if __name__ == "__main__":
    asyncio.run(main())
