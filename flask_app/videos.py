import os
import re
import json
from flask import Blueprint, request, Response, jsonify, current_app, send_file

videos_bp = Blueprint("videos", __name__)

def _load_config():
    repo_root = os.path.abspath(os.path.join(current_app.root_path, ".."))
    web_root = os.path.join(repo_root, "WebAnnotationEngine")
    cfg_path = os.path.join(web_root, "src", "routes", "config", "videoConfig.json")
    with open(cfg_path, "r", encoding="utf-8") as f:
        return json.load(f), web_root

def _send_with_range(file_path, mimetype="video/mp4"):
    if not os.path.isfile(file_path):
        return jsonify({"error": "File not found"}), 404

    range_header = request.headers.get("Range")
    if not range_header:
        resp = send_file(file_path, mimetype=mimetype, conditional=True)
        resp.headers["Accept-Ranges"] = "bytes"
        resp.headers["Cache-Control"] = "public, max-age=86400, immutable"
        return resp

    m = re.match(r"bytes=(\d+)-(\d+)?$", range_header)
    size = os.path.getsize(file_path)
    if not m:
        return Response(status=416)
    start = int(m.group(1))
    end = int(m.group(2)) if m.group(2) else size - 1
    end = min(end, size - 1)
    if start > end or start >= size:
        return Response(status=416)

    with open(file_path, "rb") as f:
        f.seek(start)
        data = f.read(end - start + 1)

    resp = Response(data, 206, mimetype=mimetype, direct_passthrough=True)
    resp.headers["Content-Range"] = f"bytes {start}-{end}/{size}"
    resp.headers["Accept-Ranges"] = "bytes"
    resp.headers["Content-Length"] = str(end - start + 1)
    resp.headers["Cache-Control"] = "public, max-age=86400, immutable"
    return resp

@videos_bp.get("/reference/<path:filename>")
def get_reference_video(filename):
    cfg, web_root = _load_config()
    base_dir = cfg["reference_source"]
    if not os.path.isabs(base_dir):
        base_dir = os.path.join(web_root, base_dir)
    file_path = os.path.join(base_dir, filename)
    return _send_with_range(file_path)

@videos_bp.get("/review/<batch>/<sign>/<path:filename>")
def get_review_video(batch, sign, filename):
    cfg, web_root = _load_config()
    review_root = cfg["review_source"]
    if not os.path.isabs(review_root):
        review_root = os.path.join(web_root, review_root)
    file_path = os.path.join(review_root, batch, sign, filename)
    return _send_with_range(file_path)
