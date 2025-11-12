<script>
  import { onMount } from 'svelte';
  import { page } from '$app/stores';
  import { goto } from '$app/navigation';

  const API_BASE = 'http://localhost:5000';
  const username = (localStorage.getItem('username') || '').trim();
  const basename = (p) => (p || '').split('/').pop();

  let items = [];
  let loading = true;
  let error = null;

  $: params = $page.params;

  onMount(async () => {
    try {
      const annUrl = new URL(`${API_BASE}/annots`);
      annUrl.searchParams.set('user', username);
      annUrl.searchParams.set('sign', params.word);
      const annRes = await fetch(annUrl);
      if (!annRes.ok) throw new Error(`HTTP ${annRes.status} (annots)`);
      const saved = await annRes.json();

      const batchesRes = await fetch(`${API_BASE}/api/batches`);
      if (!batchesRes.ok) throw new Error(`HTTP ${batchesRes.status}`);
      const batches = await batchesRes.json();

      const entry = batches?.[params.batch]?.[params.word];
      const reviews = entry?.reviews || [];

      items = reviews.map((full) => {
        const base = basename(full);
        const a = saved[base];
        return {
          full,
          video: base,
          label: a && a.label && String(a.label).trim() ? a.label : 'Unlabeled',
          time: a?.time ?? null
        };
      });
    } catch (e) {
      error = String(e);
    } finally {
      loading = false;
    }
  });

  function review(item) {
    const q = new URLSearchParams({ video: item.full });
    goto(`/annotation/${params.batch}/${params.word}?${q.toString()}`);
  }

  function labelMeta(l) {
    const base =
      'inline-flex items-center gap-2 px-2.5 py-1 rounded-md text-sm font-medium shrink-0';
    if (l === 'Good') return { cls: `${base} bg-green-200`, icon: '/thumbs-up.svg' };
    if (l === 'Variant') return { cls: `${base} bg-yellow-200`, icon: '/variant.svg' };
    if (l === 'Bad') return { cls: `${base} bg-red-200`, icon: '/thumbs-down.svg' };
    if (l === 'Further Review') return { cls: `${base} bg-blue-200`, icon: '/archive.svg' };
    if (l === 'Unlabeled') return { cls: `${base} bg-gray-200`, icon: '' }; // NEW
    return { cls: `${base} bg-gray-200`, icon: '' };
  }
</script>

{#if loading}
  <div class="p-6 text-gray-500">Loading…</div>
{:else if error}
  <div class="p-6 text-red-600">Error: {error}</div>
{:else}
  <div class="p-6 max-w-3xl mx-auto">
    <h1 class="text-xl font-semibold">Summary — {params.word} <span class="text-gray-500">({params.batch})</span></h1>
    {#if items.length === 0}
      <div class="mt-4 text-gray-500">No annotations yet for this word.</div>
    {:else}
      <div class="mt-4 border rounded overflow-hidden">
        {#each items as it (it.full)}
          {@const meta = labelMeta(it.label)}

          <div class="flex items-center gap-3 px-3 py-2 border-b last:border-b-0">
            <span class="font-mono truncate flex-1" title={it.full}>{it.video}</span>
            <span class="inline-flex items-center gap-2 px-2.5 py-1 rounded-md text-sm font-medium {meta.cls}">
              {#if meta.icon}<img src={meta.icon} class="w-4 h-4" alt="" />{/if}
              {it.label}
            </span>
            <button class="px-3 py-1 rounded bg-blue-600 text-white hover:bg-blue-700"
                    on:click={() => review(it)}>
              Review
            </button>
          </div>
        {/each}
      </div>
    {/if}
  </div>
{/if}
