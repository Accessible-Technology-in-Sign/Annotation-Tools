<script>
  import { onMount } from 'svelte';
  import { goto } from '$app/navigation';



  let username = null;
  let isLoggedIn = false;
  let loading = true;

  let batches = []; 
  let batchList = [];
  let words = []; 
  let selectedBatch = null;


  onMount(async () => {
    if (typeof window !== "undefined") {
      const storedUsername = localStorage.getItem("username");
      if (storedUsername) {
        username = storedUsername;
      }
    }

    isLoggedIn = !!username;  
    loading = false;

    const res = await fetch(`/api/batches/${username}`);
    const data = await res.json();
    batches = data["batches"]
    batchList = data ["batchList"]
  });

  async function saveUsername() {
    if (username.trim() === "") return;

    try {
      const res = await fetch("/api/check_user", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ username }),
      });

      const data = await res.json();

      if (data.valid) {
        localStorage.setItem("username", username);
        isLoggedIn = true;
      } else {
        alert("Username not recognized. Please contact an admin.");
      }
    } catch (error) {
      console.error("Frontend error:", error);
      alert("Something went wrong, please try again.");
    }
  }

  function selectBatch(batchNumber) {
      selectedBatch = batchNumber;
      const batchObj = batches.find(b => b.batch === batchNumber);
      if (batchObj) {
          words = batchObj.words;
          console.log(words);
      } else {
          words = [];
          console.log("Batch not found!");
      }
  }

  function startAnnotating(word) {
    if (!isLoggedIn) {
      alert("Please enter your name to start annotating.");
      return;
    }
    goto(`/annotation/${encodeURIComponent(selectedBatch)}/${encodeURIComponent(word)}`);
  }
  function logout() {
    // Remove username from local storage
    localStorage.removeItem("username"); 

      // Reset state
      username = null;
      isLoggedIn = false;
      selectedBatch = null;
      words = [];
      batchList = [];
      batches = [];
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
        {#each batchList as batch}
          <div class="batch-item" on:click={() => selectBatch(batch)}>
            {batch}
          </div>
        {/each}
      </div>

      <!-- Word List -->
      <div class="word-list">
        <h3>{selectedBatch !== null ? `${selectedBatch} - Words` : "Words"}</h3>
        {#if selectedBatch !== null}
          {#each words as word}
            <div class="word-item" on:click={() => startAnnotating(word)}>
              {word}
            </div>
          {/each}
        {/if}
      </div>
  </div>
  {/if}
{/if}
