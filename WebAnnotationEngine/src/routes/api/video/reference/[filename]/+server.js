import {Storage} from "@google-cloud/storage"
/* API used to load reference videos in from the filepath specified in the config file */

const storage = new Storage();
const GCP_BUCKET = {
  REVIEW_VIDEO_FOLDER : "ReviewSource/",
  REFERENCE_VIDEO_FOLDER: "dpan_source_videos/",
  BUCKET_NAME: "annotation_engine_videos"
}

export async function GET({ params, request }) {
  try {
    const { filename } = params;
    const filePathInBucket = GCP_BUCKET.REFERENCE_VIDEO_FOLDER + filename;
    const file = storage.bucket(GCP_BUCKET.BUCKET_NAME).file(filePathInBucket);
    console.log("Fetching reference video: " + filePathInBucket);

    // Support video streaming with range requests
    const [metadata] = await file.getMetadata();
    const fileSize = parseInt(metadata.size, 10);
    const range = request.headers.get('range');

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
      // Default full file response
      const stream = file.createReadStream();
      return new Response(stream, {
        headers:{
          'Content-Type': 'video/mp4',
          'Content-Length': fileSize
        }
      })
    }

  } catch (error) {
    console.error("Error serving reference video:", error);
    return new Response(JSON.stringify({ error: "Internal Server Error" }), { status: 500 });
  }
}
