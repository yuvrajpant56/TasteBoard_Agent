import os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from math import pi

competitor_metrics = [
    {"product_name": "Opus Clip", "rating": 4.2, "review_count": 1500},
    {"product_name": "Descript", "rating": 4.7, "review_count": 3200},
    {"product_name": "Vidyo.ai", "rating": 3.9, "review_count": 800}
]

complaint_data = [
    {"theme": "Opus Clip: Slow rendering", "frequency": 42},
    {"theme": "Opus Clip: Bad support", "frequency": 15},
    {"theme": "Descript: Crashing", "frequency": 55},
    {"theme": "Descript: Learning curve", "frequency": 25},
    {"theme": "Vidyo.ai: Clunky UI", "frequency": 30}
]

opportunity_scores = [
    {"metric": "Market Demand", "score": 9},
    {"metric": "Competition Intensity", "score": 8},
    {"metric": "Differentiation", "score": 7},
    {"metric": "Customer Pain", "score": 9},
    {"metric": "Quality Gap", "score": 8},
    {"metric": "Monetization Potential", "score": 9},
    {"metric": "Trust Risk", "score": 4}
]

def run():
    charts_dir = os.path.join(os.path.dirname(__file__), "data", "charts")
    os.makedirs(charts_dir, exist_ok=True)
    
    print("1. Rating")
    names = [c.get("product_name", "Unknown") for c in competitor_metrics]
    ratings = [float(c.get("rating", 0.0)) if c.get("rating") else 0.0 for c in competitor_metrics]
    
    plt.figure(figsize=(8, 5))
    plt.bar(names, ratings, color='skyblue')
    plt.ylim(0, 5.5)
    plt.title('Competitor Ratings')
    plt.ylabel('Rating (out of 5)')
    plt.xticks(rotation=45, ha='right')
    print("Saving 1...")
    p = os.path.join(charts_dir, 'rating_chart.png')
    plt.savefig(p, bbox_inches='tight')
    plt.close()
    print("Saved 1.")
    
    print("2. Review Volume")
    counts = [int(c.get("review_count", 0)) if c.get("review_count") else 0 for c in competitor_metrics]
    
    plt.figure(figsize=(8, 5))
    plt.bar(names, counts, color='lightgreen')
    plt.title('Competitor Review Volume')
    plt.ylabel('Number of Reviews')
    plt.xticks(rotation=45, ha='right')
    print("Saving 2...")
    p = os.path.join(charts_dir, 'review_volume_chart.png')
    plt.savefig(p, bbox_inches='tight')
    plt.close()
    print("Saved 2.")
    
    print("3. Complaint")
    themes = [c.get("theme", "Unknown") for c in complaint_data]
    freqs = [c.get("frequency", 0) for c in complaint_data]
    
    plt.figure(figsize=(8, 5))
    plt.bar(themes, freqs, color='salmon')
    plt.title('Complaint Frequency')
    plt.ylabel('Frequency')
    plt.xticks(rotation=45, ha='right')
    print("Saving 3...")
    p = os.path.join(charts_dir, 'complaint_frequency_chart.png')
    plt.savefig(p, bbox_inches='tight')
    plt.close()
    print("Saved 3.")
    
    print("4. Radar")
    categories = [s.get("metric", "Unknown") for s in opportunity_scores]
    values = [s.get("score", 0) for s in opportunity_scores]
    
    N = len(categories)
    if N > 2:
        values += [values[0]]
        angles = [n / float(N) * 2 * pi for n in range(N)]
        angles += [angles[0]]
        
        plt.figure(figsize=(6, 6))
        ax = plt.subplot(111, polar=True)
        plt.xticks(angles[:-1], categories, color='grey', size=8)
        ax.plot(angles, values, linewidth=1, linestyle='solid')
        ax.fill(angles, values, 'b', alpha=0.1)
        plt.title('Opportunity Radar Chart', y=1.1)
        plt.ylim(0, 10)
        
        print("Saving 4...")
        p = os.path.join(charts_dir, 'opportunity_radar_chart.png')
        plt.savefig(p, bbox_inches='tight')
        plt.close()
        print("Saved 4.")
        
    print("Done")

if __name__ == "__main__":
    run()
