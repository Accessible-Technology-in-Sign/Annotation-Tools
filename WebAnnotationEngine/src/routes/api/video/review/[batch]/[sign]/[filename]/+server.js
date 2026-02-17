import fs from 'fs';
import path from 'path';
/* API used to load review videos in from the filepath specified in the config file */

export async function GET({ params, request }) {
  try {
    const configPath = path.resolve('src/routes/config/videoConfig.json');
    const configData = JSON.parse(fs.readFileSync(configPath, 'utf-8'));

    const { batch, sign, filename } = params;
    console.log(`Fetching review video: ${batch}/${sign}/${filename}`);

    const baseDir = path.resolve(configData.review_source, batch, sign);
    const filePath = path.join(baseDir, filename);
    console.log(`The full filepath is: ${filePath}`);

    if (!fs.existsSync(filePath)) {
      return new Response(JSON.stringify({ error: "Review file not found" }), { status: 404 });
    }

    // Support video streaming with range requests
    const stat = fs.statSync(filePath);
    const fileSize = stat.size;
    const range = request.headers.get("range");

    if (range) {
      const parts = range.replace(/bytes=/, "").split("-");
      const start = parseInt(parts[0], 10);
      const end = parts[1] ? parseInt(parts[1], 10) : fileSize - 1;
      const chunkSize = end - start + 1;

      const nodeStream = fs.createReadStream(filePath, { start, end });
      let controllerClosed = false;
      
      const webStream = new ReadableStream({
        start(controller) {
          nodeStream.on('data', chunk => {
            if (!controllerClosed) {
              try {
                controller.enqueue(chunk);
              } catch (err) {
                console.warn("Failed to enqueue chunk:", err.message);
                controllerClosed = true;
                nodeStream.destroy(); 
              }
            }
          });
      
          nodeStream.on('end', () => {
            if (!controllerClosed) {
              controller.close();
              controllerClosed = true;
            }
          });
      
          nodeStream.on('error', err => {
            if (!controllerClosed) {
              controller.error(err);
              controllerClosed = true;
            }
          });
        },
      
        cancel() {
          controllerClosed = true;
          nodeStream.destroy();
        }
      });
      

      return new Response(webStream, {
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
    const nodeStream = fs.createReadStream(filePath, { start, end });
    let controllerClosed = false;
    
    const webStream = new ReadableStream({
      start(controller) {
        nodeStream.on('data', chunk => {
          if (!controllerClosed) {
            try {
              controller.enqueue(chunk);
            } catch (err) {
              console.warn("Failed to enqueue chunk:", err.message);
              controllerClosed = true;
              nodeStream.destroy(); 
            }
          }
        });
    
        nodeStream.on('end', () => {
          if (!controllerClosed) {
            controller.close();
            controllerClosed = true;
          }
        });
    
        nodeStream.on('error', err => {
          if (!controllerClosed) {
            controller.error(err);
            controllerClosed = true;
          }
        });
      },
    
      cancel() {
        controllerClosed = true;
        nodeStream.destroy();
      }
    });
    

    return new Response(webStream, {
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

