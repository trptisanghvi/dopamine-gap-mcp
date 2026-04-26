import os
from flask import Flask, jsonify, send_from_directory
from flask_cors import CORS
from dotenv import load_dotenv
from server import get_discourse_timeline, get_clinical_timeline

load_dotenv()
app = Flask(__name__, static_folder="docs")
CORS(app)


def parse_timeline(raw: str) -> dict:
    """Parse text output from get_discourse_timeline / get_clinical_timeline.
    Lines look like: '2015: ████ (65)'
    """
    counts = {}
    for line in raw.splitlines():
        line = line.strip()
        if line and line[0].isdigit():
            try:
                year_part, rest = line.split(":", 1)
                count = int(rest.strip().rsplit("(", 1)[-1].rstrip(")").strip())
                counts[int(year_part.strip())] = count
            except (ValueError, IndexError):
                continue
    return counts


@app.route("/data")
def data():
    """Return live Guardian + PubMed counts as JSON."""
    start_year, end_year = 2004, 2024

    pub_raw  = get_discourse_timeline(
        "dopamine hit", start_year, end_year
    )
    clin_raw = get_clinical_timeline(
        "dopamine reward prediction error striatum", start_year, end_year
    )

    pub_counts  = parse_timeline(pub_raw)
    clin_counts = parse_timeline(clin_raw)

    years     = list(range(start_year, end_year + 1))
    pub_data  = [pub_counts.get(y, 0)  for y in years]
    clin_data = [clin_counts.get(y, 0) for y in years]

    return jsonify({
        "years":      [f"'{str(y)[2:]}" for y in years],
        "pub_data":   pub_data,
        "clin_data":  clin_data,
        "start_year": start_year,
        "end_year":   end_year,
    })


@app.route("/")
def index():
    """Serve the chart page from docs/index.html."""
    return send_from_directory("docs", "index.html")


if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port)