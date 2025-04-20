import fs from 'fs';
import path from 'path';
import {Storage} from "@google-cloud/storage"
/* API used to load reference videos in from the filepath specified in the config file */

const storage = new Storage();
const bucketName = 'annotation_engine_videos';
const referencePrefix = 'dpan_source_videos/';

export async function GET({ params, request }) {
  const { filename } = params;
  const filePathInBucket = referencePrefix + filename;
  try {
    // const configPath = path.resolve('src/routes/config/videoConfig.json');
    // const configData = JSON.parse(fs.readFileSync(configPath, 'utf-8'));

    const file = storage.bucket(bucketName).file(filePathInBucket);
    console.log("Fetching reference video: " + filePathInBucket);
    const [metadata] = await file.getMetadata();
    const fileSize = parseInt(metadata.size, 10);

    const range = request.headers.get('range');

    // const baseDir = path.resolve(configData.reference_source);
    // const filePath = path.join(baseDir, filename);

    // if (!fs.existsSync(filePath)) {
    //   return new Response(JSON.stringify({ error: "Reference file not found" }), { status: 404 });
    // }

    // // Support video streaming with range requests
    // const stat = fs.statSync(filePath);
    // const fileSize = stat.size;

    if (range) {
      const parts = range.replace(/bytes=/, "").split("-");
      const start = parseInt(parts[0], 10);
      const end = parts[1] ? parseInt(parts[1], 10) : fileSize - 1;
      const chunkSize = end - start + 1;
    
      const fileStream = file.createReadStream({ start, end });
      return new Response(fileStream, {
        status: 206,
        headers: {
          'Content-Range': `bytes ${start}-${end}/${fileSize}`,
          'Accept-Ranges': 'bytes',
          'Content-Length': chunkSize,
          'Content-Type': 'video/mp4',
        }
      });
    }else {
      const stream = file.createReadStream();
      return new Response(stream, {
        headers:{
          'Content-Type': 'video/mp4',
          'Content-Length': fileSize
        }
      })
    }

    // // Default full file response
    // return new Response(fs.createReadStream(filePath), {
    //   headers: {
    //     'Content-Type': 'video/mp4',
    //     'Content-Length': fileSize
    //   }
    // });

  } catch (error) {
    console.error("Error serving reference video:", error);
    return new Response(JSON.stringify({ error: "Internal Server Error" }), { status: 500 });
  }
}
