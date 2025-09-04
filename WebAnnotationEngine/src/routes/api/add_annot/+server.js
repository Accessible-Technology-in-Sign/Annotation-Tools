import {IS_PROD, PROD_API_URL, DEV_API_URL} from '$env/static/private';

export async function POST({ request, fetch }) {
  try {
    const body = await request.json();
    let api_url;
    if(IS_PROD === "true")
        api_url = PROD_API_URL
    else
        api_url = DEV_API_URL

    const resp = await fetch(`${api_url}/add_annot`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body)
    });

    const data = await resp.json();

    return new Response(JSON.stringify(data), {
      status: resp.status,
      headers: { "Content-Type": "application/json" }
    });
  } catch (error) {
    console.error("Proxy error:", error);
    return new Response(
      JSON.stringify({ error: "Failed to add annotation" }),
      { status: 500, headers: { "Content-Type": "application/json" } }
    );
  }
}
