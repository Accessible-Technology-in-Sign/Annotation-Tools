export async function load({ params, fetch }) {
  const { batch, word } = params;

  console.log(batch);
  console.log(word);

  let videoList;

  try {
    const res = await fetch("/api/batches/word/videos", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ batch_number: batch, word })
    });

    const data = await res.json();
    videoList = data.videos;
    console.log(videoList);
  } catch (error) {
    console.error("Load error:", error);
  }

  if (!batch) {
    throw new Error(`Batch "${batch}" not found`);
  }

  if (!videoList) {
    throw new Error(`Word "${word}" not found in batch "${batch}"`);
  }

  return {
    batch,
    word,
    videoList
  };
}
