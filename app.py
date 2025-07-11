from flask import Flask, render_template, jsonify
from secugen_device import capture_fingerprint  # import the function

app = Flask(__name__, static_folder="static", template_folder="views")

@app.route("/api/capture", methods=["GET"])
def api_capture():
    try:
        tpl = capture_fingerprint()
        return jsonify(Code=0, Template=tpl)
    except Exception as e:
        return jsonify(Code=1, Message=str(e))

@app.route("/", methods=["GET"])
def home():
    """
    Calls the local API to capture a fingerprint,
    then renders index.html with the first 100 hex chars of the template.
    """
    try:
        # Call the API route internally
        resp = app.test_client().get("/api/capture")
        data = resp.get_json()

        if data.get("Code") == 0:
            fingerprint_hex = data["Template"][:100]
        else:
            fingerprint_hex = "Error: " + data.get("Message", "Unknown error")
    except Exception as e:
        fingerprint_hex = f"Communication error: {e}"

    return render_template("index.html", fingerprint_data=fingerprint_hex)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)
