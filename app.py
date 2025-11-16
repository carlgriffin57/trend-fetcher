from flask import Flask, request, jsonify
from pytrends.request import TrendReq
from datetime import datetime

app = Flask(__name__)

@app.route('/')
def home():
    return jsonify({
        "message": "Trend Fetcher is running",
        "timestamp": datetime.utcnow().isoformat()
    })

@app.route('/trends', methods=['GET'])
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
    growth = values[-1] - values[0] if len(values) > 1 else 0
    direction = "rising" if growth > 0 else "falling" if growth < 0 else "stable"

    return jsonify({
        "keyword": keyword,
        "trend_direction": direction,
        "growth_rate": growth,
        "search_volume": int(values[-1]),
        "timestamp": datetime.utcnow().isoformat(),
        "related_topics": "via pytrends"
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)

    from gunicorn.app.wsgiapp import run
    run()

