import os
import pathlib
from flask import Flask, jsonify, render_template, request
from werkzeug.utils import secure_filename
from PIL import Image

import ocr_service
import database_service
import gemini_service

app = Flask(__name__)
UPLOAD_FOLDER = "./static/uploads"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["MAX_CONTENT_LENGTH"] = 10 * 1024 * 1024
app.config["SUPPORTED_FORMATS"] = ["png", "jpeg", "jpg", "bmp", "pnm", "gif", "tiff", "webp", "pdf"]


@app.route("/", methods=["GET", "POST"])
def index():
    return render_template("index.html", languages=ocr_service.get_languages())


@app.route("/review", methods=["GET"])
def review():
    return render_template("review.html")


@app.route("/api/languages", methods=["GET"])
def list_supported_languages():
    return jsonify(languages=ocr_service.get_languages())


@app.route("/api/ocr", methods=["POST"])
def ocr():
    f = request.files["file"]
    language = request.form.get("language", default="en")
    filename = secure_filename(f.filename)
    file_extension = pathlib.Path(filename).suffix.lower().lstrip('.')

    if not file_extension or file_extension not in app.config["SUPPORTED_FORMATS"]:
        return jsonify(error="File format not supported or missing extension"), 400

    filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
    f.save(filepath)

    if file_extension == "pdf":
        text = ocr_service.pdf_to_text(filepath, language)
    else:
        text = ocr_service.ocr_core(Image.open(filepath), language)

    os.remove(filepath)

    return jsonify(text=text, filename=filename)


@app.route("/api/get_corrections", methods=["GET"])
def get_corrections_route():
    try:
        corrections = database_service.get_corrections()
        corrections_list = []
        for corr in corrections:
            corrections_list.append({
                "id": corr[0],
                "original_text": corr[1],
                "corrected_text": corr[2],
                "language": corr[3],
                "file_name": corr[4],
                "created_at": corr[5].isoformat()
            })
        return jsonify(corrections=corrections_list), 200
    except Exception as e:
        print(f"Error fetching corrections: {e}")
        return jsonify(success=False, error=str(e)), 500


@app.route("/api/save_correction", methods=["POST"])
def save_correction_route():
    data = request.get_json()
    original_text = data.get("original_text")
    corrected_text = data.get("corrected_text")
    language = data.get("language")
    file_name = data.get("file_name")

    try:
        database_service.save_correction(original_text, corrected_text, language, file_name)
        return jsonify(success=True), 200
    except Exception as e:
        print(f"Error saving correction: {e}")
        return jsonify(success=False, error=str(e)), 500


@app.route("/api/enhance_with_gemini", methods=["POST"])
def enhance_with_gemini():
    data = request.get_json()
    text = data.get("text")
    enhanced_text = gemini_service.enhance_text(text)
    return jsonify(enhanced_text=enhanced_text)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=True, host="0.0.0.0", port=port)
