import os
import json
import urllib.request
from dotenv import load_dotenv

# Load environment variables from .env file if it exists
load_dotenv()

def run_query_understanding(idea: str) -> dict:
    """
    Takes a free-text product idea and returns structured JSON 
    with category, target_users, keywords, and possible_competitors.
    """
    api_key = os.environ.get("GEMINI_API_KEY")
    
    if not api_key:
        print("[Query Understanding Agent] WARNING: GEMINI_API_KEY not found. Using mock response for demo.")
        return get_mock_response(idea)
            
    # Real implementation using Gemini REST API directly
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={api_key}"
    
    prompt = f"""
    You are an expert market researcher. 
    Analyze the following product idea and extract the category, target users, 
    search keywords for finding similar products, and a guess-list of likely competitors.
    
    Product Idea: "{idea}"
    
    Return EXACTLY a JSON object with this schema:
    {{
        "category": "The market category for this product idea",
        "target_users": ["Target user 1", "Target user 2"],
        "keywords": ["Keyword 1", "Keyword 2"],
        "possible_competitors": ["Competitor 1", "Competitor 2"]
    }}
    """
    
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {
            "responseMimeType": "application/json",
            "temperature": 0.2
        }
    }
    
    headers = {"Content-Type": "application/json"}
    req = urllib.request.Request(url, data=json.dumps(payload).encode('utf-8'), headers=headers)
    
    try:
        with urllib.request.urlopen(req) as response:
            result = json.loads(response.read().decode('utf-8'))
            text_response = result['candidates'][0]['content']['parts'][0]['text']
            return json.loads(text_response)
    except Exception as e:
        print(f"[Query Understanding Agent] Error calling Gemini API: {e}")
        print("Falling back to mock response.")
        return get_mock_response(idea)

def get_mock_response(idea: str) -> dict:
    if "YouTube videos into short clips" in idea:
        return {
            "category": "AI Video Repurposing Tools",
            "target_users": ["YouTubers", "Content Creators", "Social Media Managers", "Podcasters"],
            "keywords": ["AI video clipper", "YouTube to TikTok AI", "video repurposing", "auto captions AI", "short form video generator"],
            "possible_competitors": ["Opus Clip", "Munch", "Vizard", "Klap", "Descript"]
        }
    else:
        return {
            "category": "Unknown",
            "target_users": ["Unknown"],
            "keywords": ["Unknown"],
            "possible_competitors": ["Unknown"]
        }
