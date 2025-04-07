#!/usr/bin/env python3
import os
import time
import subprocess
from flask import Flask, request, redirect, url_for, render_template_string, render_template

app = Flask(__name__)
UPLOAD_DIR = "/home/pi/upload"
os.makedirs(UPLOAD_DIR, exist_ok=True)

viewer_process = None

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        f = request.files.get("file")
        if f:
            save_path = os.path.join(UPLOAD_DIR, f.filename)
            f.save(save_path)
        return redirect(url_for("index"))
    
    files = os.listdir(UPLOAD_DIR)
    # Sort by mod time descending
    files.sort(key=lambda x: os.path.getmtime(os.path.join(UPLOAD_DIR, x)), reverse=True)
    
    return render_template("index.html", files=files)

@app.route("/display/<filename>", methods=["POST"])
def display_file(filename):
    global viewer_process
    if viewer_process:
        viewer_process.kill()
        viewer_process = None
    file_path = os.path.join(UPLOAD_DIR, filename)
    # Adjust led-image-viewer command as needed
    cmd = [
          "sudo",
          "/home/pi/bin/led-image-viewer",
          file_path,
          "--led-no-hardware-pulse",
          "--led-cols=64",
          "--led-rows=32",
          "--led-brightness=50"
    ]
    viewer_process = subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, stdin=subprocess.DEVNULL)
    return redirect(url_for("index"))

@app.route("/stop", methods=["POST"])
def stop_display():
    global viewer_process
    if viewer_process:
        viewer_process.kill()
        viewer_process = None
    return redirect(url_for("index"))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)

