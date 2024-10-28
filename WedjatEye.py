from flask import Flask, request, render_template, jsonify, send_file
from PIL import Image
import io

import os


app = Flask(__name__)

# set upload and processed file
UPLOAD_FOLDER = "uploads"
PROCESSED_FOLDER = "processed"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(PROCESSED_FOLDER, exist_ok=True)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["PROCESSED_FOLDER"] = PROCESSED_FOLDER

TEST_IMAGE_PATH = "test/test.png"


# simple super-resolution method
def super_resolution(input_image):
    # TODO: implement super-resolution method
    output_image = Image.open(TEST_IMAGE_PATH)
    return output_image

# homepage routing
@app.route("/")
def homepage():
    return render_template("homepage.html")

# API for upload and process image
@app.route("/super-resolution", methods=["GET", "POST"])
def upload_and_process():
    if request.method == "POST":
        if "file" not in request.files:
            return jsonify({"error": "No file part"})

        file = request.files["file"]
        if file.filename == "":
            return jsonify({"error": "No selected file"})

        # save upload image
        file_path = os.path.join(app.config["UPLOAD_FOLDER"], file.filename)
        file.save(file_path)

        # save and process image
        input_image = Image.open(file_path)
        output_image = super_resolution(input_image)

        # save processed image
        processed_path = os.path.join(app.config["PROCESSED_FOLDER"], "processed_" + file.filename)

        # convert to RGB if image is RGBA
        if output_image.mode == "RGBA":
            output_image = output_image.convert("RGB")

        output_image.save(processed_path, format="JPEG")

        # return result page
        return render_template("result.html", input_image=file.filename, output_image="processed_" + file.filename)

    return render_template("index.html")


# Tag Feedback Interface
@app.route("/flag", methods=["POST"])
def flag_output():
    data = request.json
    flagged_image = data.get("image_name")

    # Simulation saves feedback as log file
    with open("feedback_log.txt", "a") as f:
        f.write(f"{flagged_image} flagged as problematic.\n")

    return jsonify({"status": "Image flagged successfully"})


# Image file routing
@app.route("/uploads/<filename>")
def uploaded_file(filename):
    return send_file(os.path.join(app.config["UPLOAD_FOLDER"], filename))


@app.route("/processed/<filename>")
def processed_file(filename):
    return send_file(os.path.join(app.config["PROCESSED_FOLDER"], filename))


# 启动应用
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)

