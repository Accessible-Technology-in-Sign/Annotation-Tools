import os
import json
from flask import Blueprint, jsonify, current_app
from flask_cors import cross_origin

batches_bp = Blueprint("batches", __name__)

def _load_config():
    repo_root = os.path.abspath(os.path.join(current_app.root_path, ".."))
    web_root = os.path.join(repo_root, "WebAnnotationEngine")
    cfg_path = os.path.join(web_root, "src", "routes", "config", "videoConfig.json")
    sign_list_path = os.path.join(web_root, "src", "routes", "config", "sign_list.txt")
    
    with open(cfg_path, "r", encoding="utf-8") as f:
        config = json.load(f)
    
    try:
        with open(sign_list_path, "r", encoding="utf-8") as f:
            sign_list_data = f.read()
    except FileNotFoundError:
        sign_list_data = ""
    
    return config, sign_list_data, web_root

@batches_bp.get("/")
def get_batches():
    try:
        config, sign_list_data, web_root = _load_config()

        review_source = config["review_source"]
        if not os.path.isabs(review_source):
            review_source = os.path.join(web_root, review_source)
        reference_source = config["reference_source"]
        if not os.path.isabs(reference_source):
            reference_source = os.path.join(web_root, reference_source)
        
        review_api = "/api/video/review/"
        reference_api = "/api/video/reference/"
        batches_to_load = config.get("batches", [])
        batches = {}
        
        sign_list_by_line = [line.strip() for line in sign_list_data.split("\n") if line.strip()]
        
        if batches_to_load:
            batch_dirs = [{"name": batch} for batch in batches_to_load]
        else:
            if os.path.exists(review_source):
                batch_dirs = [{"name": entry.name} for entry in os.scandir(review_source) if entry.is_dir()]
            else:
                batch_dirs = []
        
        for batch_dir in batch_dirs:
            batch_name = batch_dir["name"]
            batch_path = os.path.join(review_source, batch_name)
            if not os.path.exists(batch_path):
                continue
            
            batches[batch_name] = {}
            
            sign_dirs = [entry for entry in os.scandir(batch_path) if entry.is_dir()]
            for sign_dir in sign_dirs:
                sign_name = sign_dir.name
                if sign_list_data.strip() and sign_name not in sign_list_by_line:
                    continue
                if sign_name not in batches[batch_name]:
                    batches[batch_name][sign_name] = {"reference": None, "reviews": []}
                
                sign_path = sign_dir.path
                videos = [file for file in os.listdir(sign_path) if file.endswith('.mp4')]
                for video_file in videos:
                    file_path = os.path.join(review_api, batch_name, sign_name, video_file)
                    batches[batch_name][sign_name]["reviews"].append(file_path)
            if not batches[batch_name]:
                del batches[batch_name]
        
        if os.path.exists(reference_source):
            reference_files = [file for file in os.listdir(reference_source) if file.endswith('.mp4')]
            for file in reference_files:
                sign_name = os.path.splitext(file)[0]
                if sign_list_data.strip() and sign_name not in sign_list_by_line:
                    continue
                
                api_path = os.path.join(reference_api, file)
                for batch_name in batches:
                    if sign_name in batches[batch_name]:
                        batches[batch_name][sign_name]["reference"] = api_path

        return jsonify(batches), 200
        
    except Exception as error:
        print(f"Error loading video configuration: {error}")
        return jsonify({"error": "Failed to load video data"}), 500
