import os
import json
from dotenv import load_dotenv 

def create_phrase_batches():
    load_dotenv() 
    meta_path = os.getenv("META_DATA")
    word_dict = {}
    for item in os.listdir(meta_path):
        item_path = os.path.join(meta_path, item)
        if os.path.isdir(item_path):
            for video in os.listdir(item_path):
                x = video.split("_")
                word = x[len(x) - 1].split(".")[0]
                clip = video
                if word and clip:
                    if word not in word_dict:
                        word_dict[word] = []
                    if clip not in word_dict[word]:
                        word_dict[word].append(clip)

    # sort by length of word * (5000 - length clip array) (descending, longest first)
    sorted_items = sorted(word_dict.items(), key=lambda x: len(x[0]) * (5000 - len(x[1])), reverse=True)

    batches = {}
    batch_index = 0
    batches[f"batch_{batch_index}"] = {}

    for i, (word, clips) in enumerate(sorted_items):
        batches[f"batch_{batch_index}"][word] = clips
        # start new batch every 2 words
        if (i + 1) % 2 == 0 and (i + 1) < len(sorted_items):
            batch_index += 1
            batches[f"batch_{batch_index}"] = {}

    file_path = "batches.json"
    with open(file_path, "w") as f:
        json.dump(batches, f, indent=4)
    print("batches created successfully")

create_phrase_batches()