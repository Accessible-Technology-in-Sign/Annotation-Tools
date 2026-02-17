import {IS_PROD, PROD_API_URL, DEV_API_URL} from '$env/static/private';

// src/routes/api/batches/[username]/+server.js
export async function GET({ params, fetch }) {
  const { username } = params;
  let api_url;
  if(IS_PROD === "true")
      api_url = PROD_API_URL
    else
        api_url = DEV_API_URL

  console.log(api_url)
  if (!username?.trim()) {
    return new Response(
      JSON.stringify({ error: "Username required" }),
      { status: 400, headers: { "Content-Type": "application/json" } }
    );
  }

  try {
    const resp = await fetch(`${api_url}/batches/${username}`);

    if (!resp.ok) {
      return new Response(
        JSON.stringify({ error: `Backend failed with ${resp.status}` }),
        { status: resp.status, headers: { "Content-Type": "application/json" } }
      );
    }

    const batches = await resp.json();
    const batchList = batches.map((b) => b.batch);

    return new Response(
      JSON.stringify({ batches, batchList }),
      { headers: { "Content-Type": "application/json" } }
    );
  } catch (error) {
    console.error("API error:", error);
    return new Response(
      JSON.stringify({ error: "Failed to fetch from backend" }),
      { status: 500, headers: { "Content-Type": "application/json" } }
    );
  }
}
