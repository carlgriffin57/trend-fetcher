from flask import Flask, request, jsonify
from pytrends.request import TrendReq
from datetime import datetime

app = Flask(__name__)

@app.route('/trend', methods=['GET'])
def get_trend():
    keyword = request.args.get('keyword', '')
    if not keyword:
        return jsonify({"error": "Missing keyword"}), 400

    pytrends = TrendReq(hl='en-US', tz=360)
    try:
        pytrends.build_payload([keyword], cat=0, timeframe='today 3-m', geo='', gprop='')
        data = pytrends.interest_over_time()
    except Exception as e:
        return jsonify({"error": f"Failed to fetch data: {str(e)}"}), 500

    if data.empty:
        return jsonify({"error": "No data found for keyword"}), 404

    values = data[keyword].tolist()
    earliest, latest = values[0], values[-1]
    growth = round(((latest - earliest) / earliest) * 100, 2) if earliest > 0 else 0
    direction = "rising" if growth > 5 else "falling" if growth < -5 else "stable"

    result = {
        "keyword": keyword,
        "trend_direction": direction,
        "growth_rate": growth,
        "search_volume_index": latest,
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }

    return jsonify(result)

if __name__ == "__main__":
    from gunicorn.app.wsgiapp import run
    run()
