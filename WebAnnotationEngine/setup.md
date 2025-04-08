# Annotation Engine Setup
## Video loading  

In order to load in videos from your local directory to the annotation engine, you must specify the locations of the review and reference videos in your local directory in a configuration file. This file also gives you the ability to choose which batches and words are loaded in. 

### Configuration files

Two files must be present in your code in <span style="color: green;">src/routes/config</span>:
- <span style="color: green;">videoConfig.json</span> – Specifies the sources for review and reference videos and optionally limits batches to be loaded
- <span style="color: green;">sign_list.txt</span> – A list of specific sign words to be loaded. This file must exist but may be empty if you want to include all words.

### videoConfig.json setup

#### Example videoConfig.json:
```json
{
    "sign_list": "src/routes/config/sign_list.txt", 
    "review_source": "static/ReviewVideos",
    "reference_source": "static/ReferenceVideos",
    "batches": ["Batch 1", "Batch 2"]
}
```

#### Explanation:
- sign_list: The path to sign_list.txt relative to WebAnnotationEngine which contains sign words to be loaded separated by new lines.
- review_source: The path to the directory where review videos are stored relative to WebAnnotationEngine. Does not have to be in static.
- reference_source: The path to the directory where reference videos are stored relative to WebAnnotationEngine. Does not have to be in static.
- batches: Specifies which batches to load. Put <span style="color: green;">[]</span> for all available batches to be loaded.

### Directory structure

The review and reference directories should be formatted like this:
```
review_videos/
  ├── batch1/
  │   ├── sign1/
  │   │   ├── video1.mp4
  │   │   ├── video2.mp4
  │   ├── sign2/
  ├── batch2/
  │   ├── sign3/
  │       ├── video3.mp4

reference_videos/
  ├── sign1.mp4
  ├── sign2.mp4
  ├── sign3.mp4
  ```
### Database setup

In a seperate terminal, `cd` into the `flask_app` folder and create a virtual python environment. After activating this environement, run `pip install requirements.txt`. This will install all dependencies necessary.
Then, run `python3 app.py`.

Currently, we use a MySQL database, make sure you have MySQL installed on your computer. 
In the `flask_app/config.py` file, change `USER` and `PSWD` to match your local setup. 

#### Add users
cd into flask_app and run python3 add_user.py <user_name_to_add>

