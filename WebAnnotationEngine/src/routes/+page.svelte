<script>
  let batches = ["B words", "Body parts", "Shapes"]; // Example data for batches
  let words = []; // Words in the selected batch
  let selectedBatch = null;

  const batchData = {
    "B words": ["bacon", "banana", "bank"],
    "Body parts": ["hand", "foot", "leg", "arm"],
    "Shapes": ["square", "star"]
  };

  function selectBatch(batch) {
    selectedBatch = batch;
    words = batchData[batch] || [];
  }
</script>

<style>
  .title {
    width: 100%;
    text-align: left;
    font-size: 4rem;
    margin-left: 4rem;
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

<div class="title">ASL Annotation</div>

<div class="container">
  <!-- Batch List -->
  <div class="batch-list">
    <h3>Batches</h3>
    {#each batches as batch}
      <div class="batch-item" on:click={() => selectBatch(batch)}>
        {batch}
      </div>
    {/each}
  </div>

  <!-- Word List -->
  <div class="word-list">
    <h3>{selectedBatch ? `${selectedBatch} - Words` : "Words"}</h3>
    {#if selectedBatch}
      {#each words as word}
        <div class="word-item">
          {word}
        </div>
      {/each}
    {/if}
  </div>
</div>
