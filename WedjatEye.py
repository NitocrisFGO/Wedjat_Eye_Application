from flask import Flask, request, render_template, jsonify, send_file, url_for
import matplotlib.pyplot as plt
from PIL import Image
import torch
from torchvision import transforms
import cv2
import numpy as np
import torch.nn as nn
from colorizers import *
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


# load the colorize model
def load_colorization_models():
    colorizer_eccv16 = eccv16(pretrained=True).eval()
    colorizer_siggraph17 = siggraph17(pretrained=True).eval()
    return colorizer_eccv16, colorizer_siggraph17


# simple super-resolution method
def super_resolution(input_image):
    # TODO: implement super-resolution method
    output_image = Image.open(TEST_IMAGE_PATH)
    return output_image


# homepage routing
@app.route("/")
def homepage():
    central_images = [
        {"url": "/static/images/einstein.gif",
         "text": "Give old photos a fresh look with more vivid colors!",
         "link": url_for("colorize_process")},
        {"url": "/static/images/city-scape.gif",
         "text": "Super resolution makes your images clearer!",
         "link": url_for("super_resolution_process")},
    ]
    return render_template("homepage.html", central_images=central_images)


# API for upload and process image
def colorize(input_image_path, model):
    img = load_img(input_image_path)
    (tens_l_orig, tens_l_rs) = preprocess_img(img, HW=(256, 256))

    with torch.no_grad():
        out_img = postprocess_tens(tens_l_orig, model(tens_l_rs).cpu())

    return out_img


@app.route("/colorize", methods=["GET", "POST"])
def colorize_process():
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
        output_image = colorize(file_path, colorizer_eccv16)

        # save processed image
        processed_path = os.path.join(app.config["PROCESSED_FOLDER"], "processed_" + file.filename)

        plt.imsave(processed_path, output_image)

        # return result page
        return render_template("colorize_result.html", input_image=file.filename, output_image="processed_" + file.filename)

    return render_template("colorize_homepage.html")


# API for upload and process image
@app.route("/super-resolution", methods=["GET", "POST"])
def super_resolution_process():
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
        return render_template("super_resolution_result.html", input_image=file.filename, output_image="processed_" + file.filename)

    return render_template("super_resolution_homepage.html")


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


# # After the client accesses the processed file, clean up all files in processed and uploads.
# @app.after_request
# def cleanup_files(response):
#     for folder in [app.config["UPLOAD_FOLDER"], app.config["PROCESSED_FOLDER"]]:
#         for file in os.listdir(folder):
#             file_path = os.path.join(folder, file)
#             try:
#                 os.remove(file_path)
#             except Exception as e:
#                 print(f"Error removing file {file_path}: {e}")
#     return response


# start the server
if __name__ == "__main__":
    colorizer_eccv16, colorizer_siggraph17 = load_colorization_models()
    app.run(host="0.0.0.0", port=5000, debug=True)

