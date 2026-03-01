import json
import os
from datetime import datetime
import logging
from jinja2 import Template

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("DashboardGen")

def generate_dashboard(data_path, template_path, output_path):
    if not os.path.exists(data_path):
        logger.error(f"Data file not found: {data_path}")
        return

    with open(data_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    if not os.path.exists(template_path):
        logger.error(f"Template file not found: {template_path}")
        return

    with open(template_path, 'r', encoding='utf-8') as f:
        template_str = f.read()

    template = Template(template_str)
    
    # Format timestamp for display
    ts = datetime.fromisoformat(data['timestamp']).strftime('%Y-%m-%d %H:%M:%S')
    
    context = {
        "TIMESTAMP": ts,
        "indices": data.get("indices", []),
        "trending_stocks": data.get("trending_stocks", []),
        "reddit_categorized": data.get("reddit_categorized", {})
    }

    try:
        html = template.render(context)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html)
        logger.info(f"Dashboard successfully generated at {output_path}")
    except Exception as e:
        logger.error(f"Render failed: {e}")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", default="us-market-trends/data/market_data.json")
    parser.add_argument("--template", default="us-market-trends/assets/dashboard_template.html")
    parser.add_argument("--output", default="us-market-trends/index.html")
    args = parser.parse_args()
    
    generate_dashboard(args.data, args.template, args.output)
