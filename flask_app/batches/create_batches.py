import os
import json
from dotenv import load_dotenv 

def create_phrase_batches():
    load_dotenv() 
    meta_path = os.getenv("META_DATA")
    meta_file = "dmk_v1-train.json"
    full_path = os.path.join(meta_path, meta_file)
    data = {}

    with open(full_path, 'r') as file:
        data = json.load(file)

    phrases = group_clips_by_word(data)

    batches = {}
    batch_index = 0
    batches[f"batch_{batch_index}"] = {}
    #print(phrases)
    
    for phrase_group in phrases:
        print(phrase_group["word"])
        batches[f"batch_{batch_index}"][phrase_group["word"]] = phrase_group["clips"]
        if(len(batches[f"batch_{batch_index}"]) == 2):
            batch_index += 1
            batches[f"batch_{batch_index}"] = {}

    file_path = "batches.json"
    with open(file_path, "w") as f:
        json.dump(batches, f, indent=4)
    print("batches created successfully")

def group_clips_by_word(data):
    """
    Groups clips by word into a list of dicts formatted like:
    [{"word": "sap", "clips": ["clip1.mp4", "clip2.mp4"]}, ...]
    """
    result = {}

    for entry in data:
        word = entry.get("phrase")
        clip = entry.get("clipFilename")

        if word and clip:
            if word not in result:
                result[word] = []
            # Avoid duplicates
            if clip not in result[word]:
                result[word].append(clip)

    return [{"word": word, "clips": clips} for word, clips in result.items()]


create_phrase_batches()