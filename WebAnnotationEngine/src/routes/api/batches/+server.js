/*
Put videoConfig.json in src/routes/config 
Put review videos like this: ReviewVideos/BatchName/WordName/all the videos
Put all reference videos in 1 folder

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

export async function GET() {
  const configPath = path.resolve('src/routes/config/videoConfig.json');

  try {
    const configData = JSON.parse(fs.readFileSync(configPath, 'utf-8'));

    const reviewSource = path.resolve(configData.review_source)
    const referenceSource = path.resolve(configData.reference_source);
    const batchesToLoad = configData.batches || [];
    const batches = {};
    const relativePath = (fullPath) => fullPath.replace(path.resolve('static'), '');

    const batchDirs = batchesToLoad.length > 0
      ? batchesToLoad.map(batch => ({ name: batch }))
      : fs.readdirSync(reviewSource, { withFileTypes: true }).filter(dir => dir.isDirectory());

    for (const batchDir of batchDirs) {
      const batchName = batchDir.name;
      const batchPath = path.join(reviewSource, batchName);
      batches[batchName] = {};

      const signDirs = fs.readdirSync(batchPath, { withFileTypes: true }).filter(dir => dir.isDirectory());

      for (const signDir of signDirs) {
        const signName = signDir.name;
        const signPath = path.join(batchPath, signName);
        const videos = fs.readdirSync(signPath).filter(file => file.endsWith('.mp4'));
        
        if (!batches[batchName][signName]) {
          batches[batchName][signName] = { reference: null, reviews: [] };
        }

        for (const file of videos) {
          const filePath = path.join(signPath, file);
          batches[batchName][signName].reviews.push(relativePath(filePath));
        }
      }
    }
    const referenceFiles = fs.readdirSync(referenceSource).filter(file => file.endsWith('.mp4'));
        

    for (const file of referenceFiles) {
      const signName = path.parse(file).name;
      const referencePath = path.join(referenceSource, file);

      for (const batchName in batches) {
        if (batches[batchName][signName]) {
          batches[batchName][signName].reference = relativePath(referencePath);
        }
      }
    }

    console.log("Final Batch Data:", JSON.stringify(batches, null, 2));

    return new Response(JSON.stringify(batches), { status: 200 });
  } catch (error) {
    console.error("Error loading video configuration:", error);
    return new Response(JSON.stringify({ error: "Failed to load video data" }), { status: 500 });
  }
}
