import fs from 'fs';
import path from 'path';

export async function GET() {
  const basePath = path.resolve('static/ReviewVideos');
  const batches = {};

  const batchDirs = fs.readdirSync(basePath, { withFileTypes: true }).filter(dir => dir.isDirectory());

  for (const batchDir of batchDirs) {
    const batchName = batchDir.name;
    const batchPath = path.join(basePath, batchName);
    batches[batchName] = {};

    const files = fs.readdirSync(batchPath).filter(file => file.endsWith('.mp4'));

    for (const file of files) {
      const referenceMatch = file.match(/^(\w+)\.mp4$/);
      if (referenceMatch) {
        const word = referenceMatch[1];
        if (!batches[batchName][word]) {
          batches[batchName][word] = { reference: null, reviews: [] };
        }
        batches[batchName][word].reference = file;
        continue;
      }

      const reviewMatch = file.match(/-(\w+)-/);
      if (reviewMatch) {
        const word = reviewMatch[1];
        if (!batches[batchName][word]) {
          batches[batchName][word] = { reference: null, reviews: [] };
        }
        batches[batchName][word].reviews.push(file);
      }
    }
  }

  return new Response(JSON.stringify(batches), { status: 200 });
}
