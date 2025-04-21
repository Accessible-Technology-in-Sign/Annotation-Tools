/*
Put videoConfig.json in src/routes/config 
Put review videos like this: ReviewVideos/batchNum/WordName/all the videos
Put all reference videos in 1 folder
Put sign_list.txt in src/routes/config and list words to annotate or leave enpty if want all
(It does not strictly have to be under static)

example videoConfig.json:
{
    "sign_list": "src/config/sign_list.txt", --> doesn't do anything rn
    "review_source": "static/ReviewVideos",
    "reference_source": "static/ReferenceVideos",
    "language": "en",
    "batches": ["Batch 2"] or [] for all batches
}
*/

import fs from 'fs';
import path from 'path';

import { Storage } from '@google-cloud/storage';

const GCP_BUCKET = {
  REVIEW_VIDEO_FOLDER : "ReviewSource/",
  REFERENCE_VIDEO_FOLDER: "dpan_source_videos/",
  BUCKET_NAME: "annotation_engine_videos"
}

export async function GET() {
  const configPath = path.resolve('src/routes/config/videoConfig.json');
  const signListPath = path.resolve('src/routes/config/sign_list.txt');

  try {
    const configData = JSON.parse(fs.readFileSync(configPath, 'utf-8'));
    const signListData = fs.readFileSync(signListPath, 'utf-8');
    const storage = new Storage();
    const bucket = storage.bucket(GCP_BUCKET.BUCKET_NAME);

    const reviewAPI = '/api/video/review/';
    const referenceAPI = '/api/video/reference/';
    const batchesToLoad = configData.batches || [];
    const batches = {};

    const [reviewFiles] = await bucket.getFiles({
      prefix: GCP_BUCKET.REVIEW_VIDEO_FOLDER,
      autoPaginate: false
    });

    const signListByLine = signListData.split("\n")

    for (const file of reviewFiles) {
      if (!file.name.endsWith('.mp4')) continue;

      const fileParts = file.name.split("/");
      if (fileParts.length != 4) continue;

      const [, batchNum, signName, filename] = fileParts;

      //If batches specified, only include those
      if (batchesToLoad.length > 0 && !batchesToLoad.includes(batchNum)) continue;

      if (signListData.trim() !== '' && !signListByLine.includes(signName)) continue;

      //create entry in batch object for the batch 
      if (!batches[batchNum]) batches[batchNum] = {};

      //add sign words in batch
      if (!batches[batchNum][signName]) {
        batches[batchNum][signName] = { reference: null, reviews: [] };
      }

      // Have the pages refer to the API when loading the videos (such that it can load outside of static)
      const filePath = path.join(reviewAPI, batchNum, signName, filename);
      batches[batchNum][signName].reviews.push(filePath);
    }

    //reference videos
    const [referenceFiles] = await bucket.getFiles({
      prefix: GCP_BUCKET.REFERENCE_VIDEO_FOLDER,
      autoPaginate: false
    });

    for (const file of referenceFiles) {
      if (!file.name.endsWith('.mp4')) continue;
    
      const fileName = path.basename(file.name);
      const signName = path.parse(fileName).name;

      //if sign list contains words, skip those not specified
      if (signListData.trim() !== '' && !signListByLine.includes(signName)) {
        continue;
      }

      const apiPath = path.join(referenceAPI, fileName);

      for (const batchNum in batches) {
        if (batches[batchNum][signName]) {
          batches[batchNum][signName].reference = apiPath;
        }
      }
    }

    return new Response(JSON.stringify(batches), { status: 200 });
    } catch (error) {
      console.error("Error loading video configuration:", error);
      return new Response(JSON.stringify({ error: "Failed to load video data" }), { status: 500 });
    }
  }

