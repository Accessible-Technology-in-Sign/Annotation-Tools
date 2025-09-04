import {IS_PROD, PROD_API_URL, DEV_API_URL} from '$env/static/private';
// src/routes/api/check_user/+server.js
export async function POST({ request, fetch }) {
  let api_url;
  if(IS_PROD === "true")
      api_url = PROD_API_URL
    else
        api_url = DEV_API_URL
  try {
    const body = await request.json();

    const resp = await fetch(`${api_url}/check_user`, {
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
    console.error("API error:", error);
    return new Response(
      JSON.stringify({ error: "Failed to reach backend" }),
      { status: 500, headers: { "Content-Type": "application/json" } }
    );
  }
}
