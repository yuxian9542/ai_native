import os
import sys
from datetime import datetime
from pathlib import Path

from flask import Flask, render_template, request

# Ensure local imports work when running directly
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
if CURRENT_DIR not in sys.path:
    sys.path.append(CURRENT_DIR)

from amzn_crawl_backend import amzn_review_main, set_run_log_file  # noqa: E402


app = Flask(
    __name__,
    template_folder=os.path.join(CURRENT_DIR, "templates"),
    static_folder=os.path.join(CURRENT_DIR, "static"),
)


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        keyword = request.form.get("keyword", "").strip()
        try:
            num_products = int(request.form.get("num_products", "3"))
        except Exception:
            num_products = 3
        try:
            num_pages = int(request.form.get("num_pages", "1"))
        except Exception:
            num_pages = 1

        star_raw = request.form.get("star", "").strip()
        star = int(star_raw) if star_raw.isdigit() else None

        # Prepare per-run output and log file names
        output_dir = Path(CURRENT_DIR) / "output"
        output_dir.mkdir(parents=True, exist_ok=True)
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_path = output_dir / f"results_{ts}.log"
        set_run_log_file(str(log_path))

        results = amzn_review_main(
            search_term=keyword,
            num_result=num_products,
            star=star,
            total_pages=num_pages,
        )

        rendered = render_template(
            "results.html",
            keyword=keyword,
            num_products=num_products,
            num_pages=num_pages,
            star=star,
            results=results,
        )

        outfile = output_dir / f"results_{ts}.html"
        outfile.write_text(rendered, encoding="utf-8")

        return rendered

    # GET
    return render_template("index.html")


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)


