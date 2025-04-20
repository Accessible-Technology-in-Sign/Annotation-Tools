import fs from 'fs';
import path from 'path';
import { Storage } from '@google-cloud/storage';
/* API used to load review videos in from the filepath specified in the config file */

const storage = new Storage();
const bucketName = 'annotation_engine_videos';
const reviewPrefix = 'ReviewSource/';

export async function GET({ params, request }) {
  try {
    const configPath = path.resolve('src/routes/config/videoConfig.json');
    const configData = JSON.parse(fs.readFileSync(configPath, 'utf-8'));

    const { batch, sign, filename } = params;
    const filePathInBucket = `${reviewPrefix}${batch}/${sign}/${filename}`;
    console.log(`Fetching review video: ${filePathInBucket}`);

    // const baseDir = path.resolve(configData.review_source, batch, sign);
    // const filePath = path.join(baseDir, filename);
    // console.log(`The full filepath is: ${filePath}`);

    const file = storage.bucket(bucketName).file(filePathInBucket);


    // if (!fs.existsSync(filePath)) {
    //   return new Response(JSON.stringify({ error: "Review file not found" }), { status: 404 });
    // }

    const [exists] = await file.exists();
    if (!exists) {
      return new Response(JSON.stringify({ error: 'Review file not found' }), { status: 404 });
    }

    const [metadata] = await file.getMetadata();
    const fileSize = parseInt(metadata.size, 10);
    const range = request.headers.get("range");

    // // Support video streaming with range requests
    // const stat = fs.statSync(filePath);
    // const fileSize = stat.size;
    // const range = request.headers.get("range");

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
    }

    // Default full file response
    const fillStream = file.createReadStream();
    return new Response(file, {
      headers: {
        'Content-Type': 'video/mp4',
        'Content-Length': fileSize
      }
    });

  } catch (error) {
    console.error("Error serving review video:", error);
    return new Response(JSON.stringify({ error: "Internal Server Error" }), { status: 500 });
  }
}
