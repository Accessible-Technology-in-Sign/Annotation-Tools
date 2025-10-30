<script>
  import { onMount } from 'svelte';
  import { goto } from '$app/navigation';

  let username = null;
  let isLoggedIn = false;
  let loading = true;

  let batches = {}; 
  let batchList = [];
  let words = []; 
  let selectedBatch = null;

  const API_BASE = "http://127.0.0.1:5000";
  const basename = (p) => (p || "").split("/").pop();

  let wordProgress = {};
  let batchProgress = {};

  let userToken = 0;

  // ---------- PROGRESS HELPERS ----------

  async function loadProgressForWord(batch, word, uname, token) {
    if (!uname) return;

    const entry = batches?.[batch]?.[word];
    const reviews = entry?.reviews || [];
    const total = reviews.length;

    if (!total) {
      if (token !== userToken) return;
      wordProgress[word] = { done: 0, total: 0, percent: 0 };
      return;
    }

    const KEY = `wp:${uname}:${batch}:${word}`;
    const cached = localStorage.getItem(KEY);
    if (cached) {
      try {
        const parsed = JSON.parse(cached);
        if (token === userToken) wordProgress[word] = parsed;
      } catch {}
    }

    try {
      const res = await fetch(
        `${API_BASE}/annots?user=${encodeURIComponent(uname)}&sign=${encodeURIComponent(word)}`
      );
      if (!res.ok) return;

      const saved = await res.json();
      const baseSet = new Set(reviews.map(basename));

      let done = 0;
      for (const f of Object.keys(saved)) {
        if (baseSet.has(f) && saved[f]?.label && String(saved[f].label).trim() !== "") {
          done++;
        }
      }

      const percent = total ? Math.round((done / total) * 100) : 0;

      if (token !== userToken) return;

      wordProgress[word] = { done, total, percent };
      localStorage.setItem(KEY, JSON.stringify(wordProgress[word]));
    } catch (e) {
      if (token === userToken) console.warn("progress fetch failed:", word, e);
    }
  }

  function computeBatchProgress(batch) {
    const keys = Object.keys(batches[batch] || {});
    let done = 0, total = 0;

    for (const w of keys) {
      const wp = wordProgress[w];
      if (wp) {
        done  += wp.done  || 0;
        total += wp.total || 0;
      }
    }
    const percent = total ? Math.round((done / total) * 100) : 0;
    batchProgress[batch] = { done, total, percent };
  }

  async function loadAllWordProgress(batch, uname, token) {
    if (!batch || !uname) return;
    const ws = Object.keys(batches[batch] || {});
    await Promise.all(ws.map(w => loadProgressForWord(batch, w, uname, token)));
    if (token === userToken) computeBatchProgress(batch);
  }

  async function loadAllBatchesProgress(uname, token) {
    if (!uname) return;
    for (const b of batchList) {
      await loadAllWordProgress(b, uname, token);
    }
  }

  // ---------- LIFECYCLE ----------

  onMount(async () => {
    const storedUsername = (typeof window !== "undefined")
      ? (localStorage.getItem("username") || "").trim()
      : "";

    if (storedUsername) {
      username = storedUsername;
      isLoggedIn = true;
      userToken++;
      wordProgress = {};
      batchProgress = {};
    }

    loading = false;

    try {
      const response = await fetch(`${API_BASE}/api/batches`);
      if (!response.ok) throw new Error('Failed to load batches');
      batches = await response.json();
      batchList = Object.keys(batches);

      if (!selectedBatch && batchList.length) {
        selectedBatch = batchList[0];
        words = Object.keys(batches[selectedBatch]);
      }

      if (isLoggedIn && username) {
        const token = userToken;
        await loadAllWordProgress(selectedBatch, username, token);
        await loadAllBatchesProgress(username, token);
      }
    } catch (error) {
      console.error('Error loading batches:', error);
    }
  });

  // ---------- AUTH ----------

  async function saveUsername() {
    const next = (username || "").trim();
    if (next === "") return;

    const res = await fetch(`${API_BASE}/check_user`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ username: next }),
    });

    const data = await res.json();

    if (data.valid) {
      localStorage.setItem("username", next);
      isLoggedIn = true;

      userToken++;
      wordProgress = {};
      batchProgress = {};

      const token = userToken;
      await loadAllWordProgress(selectedBatch, next, token);
    } else {
      alert("Username not recognized. Please contact an admin.");
    }
  }

  function logout() {
    localStorage.removeItem("username");
    isLoggedIn = false;
    username = null;

    userToken++;
    wordProgress = {};
    batchProgress = {};
  }

  // ---------- UI ACTIONS ----------

  function selectBatch(batch) {
    selectedBatch = batch;
    words = Object.keys(batches[batch]);
    if (isLoggedIn && username) {
      const token = userToken;
      loadAllWordProgress(batch, username, token);
    }
  }

  function startAnnotating(word) {
    if (!isLoggedIn) {
      alert("Please enter your name to start annotating.");
      return;
    }
    goto(`/annotation/${encodeURIComponent(selectedBatch)}/${encodeURIComponent(word)}`);
  }
</script>


<style>
  .title {
    width: 100%;
    text-align: left;
    font-size: 4rem;
    margin-left: 4rem;
  }

  .user-info {
    position: absolute;
    top: 10px;
    right: 20px;
    display: flex;
    align-items: center;
    gap: 10px;
    background: rgba(0, 0, 0, 0.1);
    padding: 8px 16px;
    border-radius: 8px;
    font-size: 1rem;
    font-weight: bold;
  }

  .logout-button {
    background: red;
    color: white;
    border: none;
    padding: 6px 12px;
    border-radius: 6px;
    cursor: pointer;
  }

  .logout-button:hover {
    background: darkred;
  }

  .container {
    display: flex;
    width: 100%;
    height: 100vh;
  }

  .batch-list, .word-list {
    flex: 1; 
    background-color: #f3f4f6;
    padding: 1rem;
    border-radius: 0.5rem;
    margin: 0.5rem;
    overflow-y: auto; 
  }

  .batch-item, .word-item {
    padding: 0.5rem;
    margin: 0.25rem 0;
    background-color: #e5e7eb;
    border-radius: 0.25rem;
    cursor: pointer;
    text-align: center;
  }

  .batch-item:hover, .word-item:hover {
    background-color: #d1d5db;
  }

  .meta { font-size: 12px; color: #4b5563; }
  .bar-bg { height: 6px; background: #e5e7eb; border-radius: 6px; }
  .bar-fill { height: 6px; background: #3b82f6; border-radius: 6px; transition: width 160ms linear; }

  h3 {
    margin-top: 0;
  }
</style>

<!-- Login Section -->
{#if loading}
  <div class="fixed inset-0 flex items-center justify-center bg-white">
    <h2 class="text-2xl font-bold">Loading...</h2>
  </div>
{:else}
  {#if !isLoggedIn}
    <div class="fixed inset-0 flex items-center justify-center bg-black bg-opacity-50">
      <div class="bg-white p-6 rounded shadow-lg">
        <h2 class="text-lg">Enter your name to start annotating:</h2>
        <input
          type="text"
          bind:value={username}
          class="border p-2 rounded w-full"
          placeholder="Enter your name..."
          on:keypress={(event) => event.key === 'Enter' && saveUsername()}
        />
        <button on:click={saveUsername} class="mt-4 bg-blue-500 text-white p-2 rounded w-full">
          Start
        </button>
      </div>
    </div>
  {/if}

  {#if isLoggedIn}
  <div class="title">ASL Annotation</div>
  <div class="user-info">
    <span>Hello, {username}</span>
    <button on:click={logout} class="logout-button">Log Out</button>
  </div>
    <div class="container">
      <!-- Batch List -->
      <div class="batch-list">
        <h3>Batches</h3>
        {#each batchList as b}
          <div class="batch-item" on:click={() => selectBatch(b)}>
            <div class="flex items-center justify-between">
              <div>{b}</div>
              <div class="meta">
                {#if batchProgress[b]}
                  {batchProgress[b].done}/{batchProgress[b].total} • {batchProgress[b].percent}%
                {:else}
                  loading…
                {/if}
              </div>
            </div>
            <div class="bar-bg mt-2">
              <div
                class="bar-fill"
                style="width: {batchProgress[b]?.percent ?? 0}%">
              </div>
            </div>
          </div>
        {/each}
      </div>


      <!-- Word List -->
      <div class="word-list">
        <h3>{selectedBatch ? `${selectedBatch} - Words` : "Words"}</h3>
        {#if selectedBatch}
          {#each words as word}
            <div class="word-item" on:click={() => startAnnotating(word)}>
              <div class="flex items-center justify-between">
                <div>{word}</div>
                <div class="meta">
                  {#if wordProgress[word]}
                    {wordProgress[word].done}/{wordProgress[word].total} • {wordProgress[word].percent}%
                  {:else}
                    loading…
                  {/if}
                </div>
              </div>
              <div class="bar-bg mt-2">
                <div class="bar-fill" style="width: {wordProgress[word]?.percent ?? 0}%"></div>
              </div>
            </div>
          {/each}
        {/if}
      </div>
  </div>
  {/if}
{/if}
