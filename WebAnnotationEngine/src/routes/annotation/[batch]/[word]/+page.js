export async function load({ params, fetch }) {
  const { batch, word } = params;
  console.log('Loading data for batch:', batch, 'and word:', word);

  const response = await fetch('/videoData.json');
  console.log('Fetch response status:', response.status);

  if (!response.ok) {
    console.error('Failed to fetch video data');
    throw new Error('Failed to load video data');
  }

  const videoData = await response.json();
  console.log('Fetched video data:', videoData);

  const selectedBatch = videoData.batches[batch];
  if (!selectedBatch) {
    throw new Error(`Batch "${batch}" not found`);
  }

  const selectedVideoData = selectedBatch[word];
  if (!selectedVideoData) {
    throw new Error(`Word "${word}" not found in batch "${batch}"`);
  }

  console.log('Selected video data:', selectedVideoData);

  return {
    batch,
    word,
    selectedVideoData
  };
}
