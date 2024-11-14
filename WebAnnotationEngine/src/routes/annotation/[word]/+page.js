export async function load({ params, fetch }) {
    const { word } = params;
    console.log('Loading data for word:', word);
  
    const response = await fetch('/videoData.json');
    console.log('Fetch response status:', response.status);
  
    if (!response.ok) {
      console.error('Failed to fetch video data');
      throw new Error('Failed to load video data');
    }
  
    const videoData = await response.json();
    console.log('Fetched video data:', videoData);
  
    let selectedVideoData = null;
    for (const batch in videoData.batches) {
      if (videoData.batches[batch][word]) {
        selectedVideoData = videoData.batches[batch][word];
        break;
      }
    }
  
    if (!selectedVideoData) {
      console.warn(`No data found for word: ${word}`);
      throw new Error(`No data available for word: ${word}`);
    }
  
    console.log('Selected video data:', selectedVideoData);
  
    return {
      word,
      selectedVideoData
    };
  }
  