import os
import tempfile
import requests
import subprocess
from flask import Flask, request, jsonify, send_file

app = Flask(__name__)

def _run_ffmpeg(input_path, output_path, bitrate_kbps):
    # Force upscale to 1080p and apply sharpening
    ffmpeg_command = [
        "ffmpeg",
        "-y",  # overwrite output file
        "-i", input_path,
        "-c:v", "libx264",
        "-preset", "slow",
        "-b:v", f"{bitrate_kbps}k",
        "-vf", "scale=1920:1080,unsharp=5:5:0.6:5:5:0.0",
        "-movflags", "+faststart",
        output_path
    ]

    proc = subprocess.run(ffmpeg_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if proc.returncode != 0:
        raise RuntimeError(proc.stderr[-2000:])  # last part of ffmpeg log if error

@app.route("/reencode", methods=["GET"])
def reencode_video_get():
    video_url = request.args.get("video_url")
    target_bitrate = int(request.args.get("target_bitrate", "8000"))  # default 8 Mbps

    if not video_url:
        return jsonify({"error": "Missing video_url parameter"}), 400

    with tempfile.TemporaryDirectory() as tmpdir:
        input_path = os.path.join(tmpdir, "input.mp4")
        output_path = os.path.join(tmpdir, "output.mp4")

        # Download video
        r = requests.get(video_url, stream=True)
        if r.status_code != 200:
            return jsonify({"error": "Failed to download video"}), 400
        with open(input_path, "wb") as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)

        # Check file size
        if os.path.getsize(input_path) < 1000:
            return jsonify({"error": "Downloaded file too small"}), 400

        # Run ffmpeg
        try:
            _run_ffmpeg(input_path, output_path, target_bitrate)
        except Exception as e:
            return jsonify({"error": f"ffmpeg failed: {e}"}), 500

        return send_file(output_path, mimetype="video/mp4")

@app.route("/reencode", methods=["POST"])
def reencode_video_post():
    data = request.get_json(silent=True) or {}
    video_url = data.get("video_url")
    target_bitrate = int(data.get("target_bitrate", 8000))

    if not video_url:
        return jsonify({"error": "Missing video_url"}), 400

    with tempfile.TemporaryDirectory() as tmpdir:
        input_path = os.path.join(tmpdir, "input.mp4")
        output_path = os.path.join(tmpdir, "output.mp4")

        # Download video
        r = requests.get(video_url, stream=True)
        if r.status_code != 200:
            return jsonify({"error": "Failed to download video"}), 400
        with open(input_path, "wb") as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)

        if os.path.getsize(input_path) < 1000:
            return jsonify({"error": "Downloaded file too small"}), 400

        # Run ffmpeg
        try:
            _run_ffmpeg(input_path, output_path, target_bitrate)
        except Exception as e:
            return jsonify({"error": f"ffmpeg failed: {e}"}), 500

        return send_file(output_path, mimetype="video/mp4")

@app.route("/", methods=["GET"])
def home():
    return jsonify({"status": "ok"})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
