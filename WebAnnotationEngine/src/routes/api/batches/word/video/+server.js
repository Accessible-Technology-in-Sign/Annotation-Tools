// src/routes/api/batches/word/video/+server.js
import {IS_PROD, PROD_API_URL, DEV_API_URL} from '$env/static/private';

export async function POST({ request, fetch }) {
  try {
    const body = await request.json();
    let api_url;
    if(IS_PROD === "true")
        api_url = PROD_API_URL
    else
        api_url = DEV_API_URL

    const resp = await fetch(`${api_url}/batches/word/video`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body)
    });

    if (!resp.ok) {
      const err = await resp.json().catch(() => ({}));
      return new Response(JSON.stringify(err), {
        status: resp.status,
        headers: { "Content-Type": "application/json" }
      });
    }

    // proxy the raw video stream (blob)
    const arrayBuffer = await resp.arrayBuffer();
    return new Response(arrayBuffer, {
      status: 200,
      headers: {
        "Content-Type": "video/mp4"
      }
    });
  } catch (error) {
    console.error("Proxy error:", error);
    return new Response(
      JSON.stringify({ error: "Failed to fetch video from backend" }),
      { status: 500, headers: { "Content-Type": "application/json" } }
    );
  }
}
