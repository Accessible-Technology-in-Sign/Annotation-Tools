// src/routes/api/batches/word/videos/+server.js
import {IS_PROD, PROD_API_URL, DEV_API_URL} from '$env/static/private';

export async function POST({ request, fetch }) {
  try {
    let api_url;
    if(IS_PROD === "true")
        api_url = PROD_API_URL
    else
        api_url = DEV_API_URL
    const body = await request.json();

    const resp = await fetch(`${api_url}/batches/word/videos`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body)
    });

    if (!resp.ok) {
      return new Response(
        JSON.stringify({ error: `Backend failed with ${resp.status}` }),
        { status: resp.status, headers: { "Content-Type": "application/json" } }
      );
    }

    const data = await resp.json();
    return new Response(JSON.stringify(data), {
      headers: { "Content-Type": "application/json" }
    });
  } catch (error) {
    console.error("Proxy error:", error);
    return new Response(
      JSON.stringify({ error: "Failed to fetch from backend" }),
      { status: 500, headers: { "Content-Type": "application/json" } }
    );
  }
}
