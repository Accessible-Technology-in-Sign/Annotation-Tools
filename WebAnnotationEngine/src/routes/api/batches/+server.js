/*
Put videoConfig.json in src/routes/config 
Put review videos like this: ReviewVideos/BatchName/WordName/all the videos
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

export async function GET() {
  const configPath = path.resolve('src/routes/config/videoConfig.json');
  const signListPath = path.resolve('src/routes/config/sign_list.txt');


  try {
    const configData = JSON.parse(fs.readFileSync(configPath, 'utf-8'));
    const signListData = fs.readFileSync(signListPath, 'utf-8');
    const storage = new Storage();
    const bucket = storage.bucket('annotation_engine_videos');
    // const reviewSource = path.resolve(configData.review_source)
    // const referenceSource = path.resolve(configData.reference_source);
    const reviewAPI = '/api/video/review/';
    const referenceAPI = '/api/video/reference/';
    const batchesToLoad = configData.batches || [];
    const batches = {};

    // const relativePath = (fullPath) => fullPath.replace(path.resolve('static'), '');

    const [reviewFiles] = await bucket.getFiles({
      prefix: "ReviewSource/", autoPaginate: false
    });

    const signListByLine = signListData.split("\n")

    for (const file of reviewFiles) {
      if (!file.name.endsWith('.mp4')) continue;

      const parts = file.name.split("/");
      if (parts.length != 4) continue;

      const [, batchName, signName, filename] = parts;

      if (batchesToLoad.length > 0 && !batchesToLoad.includes(batchName)) continue;

      if (signListData.trim() !== '' && !signListByLine.includes(signName)) continue;

      if (!batches[batchName]) batches[batchName] = {};
      if (!batches[batchName][signName]) {
        batches[batchName][signName] = { reference: null, reviews: [] };
      }

      const apiPath = path.join(reviewAPI, batchName, signName, filename);
      batches[batchName][signName].reviews.push(apiPath);
    }

    const [referenceFiles] = await bucket.getFiles({ prefix: 'dpan_source_videos/', autoPaginate: false });
    for (const file of referenceFiles) {
      if (!file.name.endsWith('.mp4')) continue;
    
      const fileName = path.basename(file.name);
      const signName = path.parse(fileName).name;

      if (signListData.trim() !== '' && !signListByLine.includes(signName)) continue;
      const apiPath = path.join(referenceAPI, fileName);

      for (const batchName in batches) {
        if (batches[batchName][signName]) {
          batches[batchName][signName].reference = apiPath;
        }
      }
    }

    return new Response(JSON.stringify(batches), { status: 200 });
    } catch (error) {
      console.error("Error loading video configuration:", error);
      return new Response(JSON.stringify({ error: "Failed to load video data" }), { status: 500 });
    }
  }
    


    // //If batches specified, only include those
    // const batchDirs = batchesToLoad.length > 0
    //   ? batchesToLoad.map(batch => ({ name: batch }))
    //   : fs.readdirSync(reviewSource, { withFileTypes: true }).filter(dir => dir.isDirectory());

    // //create entry in batch object for the batch 
    // for (const batchDir of batchDirs) {
    //   const batchName = batchDir.name;
    //   const batchPath = path.join(reviewSource, batchName);
    //   batches[batchName] = {};
      
    //   const signDirs = fs.readdirSync(batchPath, { withFileTypes: true }).filter(dir => dir.isDirectory());

    //   //add all signs words in batch 
    //   for (const signDir of signDirs) {
    //     //if sign list contains words, skip those not specified
    //     if (signListData.trim() != "" && !signListByLine.includes(signDir.name)) {
    //       continue;
    //     }
    //     const signName = signDir.name;
    //     const signPath = path.join(batchPath, signName);
    //     const videos = fs.readdirSync(signPath).filter(file => file.endsWith('.mp4'));
        
    //     if (!batches[batchName][signName]) {
    //       batches[batchName][signName] = { reference: null, reviews: [] };
    //     }

    //     //add all videos to each sign
    //     for (const file of videos) {
    //       //const filePath = path.join(signPath, file);
    //       //batches[batchName][signName].reviews.push(relativePath(filePath));

    //       // Have the pages refer to the API when loading the videos (such that it can load outside of static)
    //       const filePath = path.join(reviewAPI, batchName, signName, file);
    //       batches[batchName][signName].reviews.push(filePath);
    //     }
    //   }
    //   if (Object.keys(batches[batchName]).length == 0) {
    //     delete batches[batchName];
    //   }
    // }
    // const referenceFiles = fs.readdirSync(referenceSource).filter(file => file.endsWith('.mp4'));
        
    // //reference videos
    // for (const file of referenceFiles) {
    //   //if sign list contains words, skip those not specified
    //   if (signListData.trim() != "" && !signListByLine.includes(path.parse(file).name)) {
    //     continue;
    //   }
    //   const signName = path.parse(file).name;
    //   const referencePath = path.join(referenceSource, file);
    //   const apiPath = path.join(referenceAPI, file)


    //   for (const batchName in batches) {
    //     if (batches[batchName][signName]) {
    //       //batches[batchName][signName].reference = relativePath(referencePath);
    //       batches[batchName][signName].reference = apiPath;
    //     }
    //   }
    // }

//     return new Response(JSON.stringify(batches), { status: 200 });
//   } catch (error) {
//     console.error("Error loading video configuration:", error);
//     return new Response(JSON.stringify({ error: "Failed to load video data" }), { status: 500 });
//   }
// }
