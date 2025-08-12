import os
import uuid
import shutil
import requests
import subprocess
from fastapi import FastAPI, Query, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse, JSONResponse

app = FastAPI()

@app.get("/health")
def health():
    return {"ok": True}

def _run_ffmpeg(input_path: str, output_path: str, bitrate_kbps: int, sharpen: bool):
    vf = []
    if sharpen:
        vf.append("unsharp=5:5:0.6:5:5:0.0")
    vf_arg = ",".join(vf) if vf else "null"

    cmd = [
        "ffmpeg", "-y",
        "-i", input_path,
        "-vf", vf_arg,
        "-c:v", "libx264",
        "-preset", "veryfast",
        "-profile:v", "high",
        "-level", "4.1",
        "-b:v", f"{bitrate_kbps}k",
        "-maxrate", f"{bitrate_kbps}k",
        "-bufsize", f"{bitrate_kbps*2}k",
        "-c:a", "copy",
        output_path
    ]
    proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if proc.returncode != 0:
        raise RuntimeError(proc.stderr[-2000:])

@app.get("/reencode")
def reencode(
    background_tasks: BackgroundTasks,
    video_url: str = Query(..., description="Direct URL to the source MP4/WEBM"),
    bitrate_kbps: int = Query(2600, ge=300, le=20000, description="Target video bitrate in kbps"),
    sharpen: bool = Query(True, description="Apply a light unsharp filter"),
):
    tmp_dir = "/tmp"
    in_path = os.path.join(tmp_dir, f"{uuid.uuid4()}.mp4")
    out_path = os.path.join(tmp_dir, f"{uuid.uuid4()}_out.mp4")

    try:
        # Download source
        with requests.get(video_url, stream=True, timeout=120) as r:
            r.raise_for_status()
            with open(in_path, "wb") as f:
                for chunk in r.iter_content(chunk_size=1024*256):
                    if chunk:
                        f.write(chunk)

        # Process with ffmpeg
        _run_ffmpeg(in_path, out_path, bitrate_kbps, sharpen)

        # Schedule cleanup after response is sent
        def cleanup():
            for p in (in_path, out_path):
                try:
                    if os.path.exists(p):
                        os.remove(p)
                except:
                    pass
        background_tasks.add_task(cleanup)

        return FileResponse(out_path, filename="veo3_sharp.mp4", media_type="video/mp4")
    except Exception as e:
        # Try to cleanup input if error
        try:
            if os.path.exists(in_path):
                os.remove(in_path)
        except:
            pass
        return JSONResponse({"ok": False, "error": str(e)}, status_code=400)