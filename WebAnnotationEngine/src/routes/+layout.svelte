<script>
	import '../app.css';

  let isPopupVisible = false; // Controls the visibility of the popup

  function togglePopup() {
    isPopupVisible = !isPopupVisible;
  }

</script>

<div class="drawer lg:drawer-open">
  <input id="my-drawer-2" type="checkbox" class="drawer-toggle" />
  <div class="drawer-content flex flex-col items-center justify-center">
    <slot />
    <label for="my-drawer-2" class="btn btn-primary drawer-button lg:hidden">
      Open drawer
    </label>
  </div>
  <div class="drawer-side">
    <label for="my-drawer-2" aria-label="close sidebar" class="drawer-overlay"></label>
    <ul class="menu bg-base-200 text-base-content min-h-full w-20 p-4">
      <img class="size-20" src="/logo.svg" />
      <!-- Sidebar content here -->
      <li><a href="/">
        <img class="size-20" src="/review-batch.svg" alt="Go to Landing Page" />
      </a></li> 
      <li><a><img class="size-20" src="/sign.svg"></a></li>
      <li><a on:click={togglePopup}><img class="size-20" src="/comment.svg" /></a></li>
    </ul>
  </div>

  <!-- Popup -->
  {#if isPopupVisible}
  <div class="fixed inset-0 bg-black bg-opacity-50 flex justify-center items-center z-50" on:click={togglePopup}>
    <div class="bg-zinc-300 rounded-lg p-5 w-1/3 h-1/3 max-w-full max-h-full relative shadow-lg" on:click|stopPropagation>
      <!-- Close Button -->
      <button
        class="absolute top-2 right-5 text-3xl font-bold text-gray-800 hover:text-red-600"
        on:click={togglePopup}
        aria-label="Close">
        &times;
      </button>

      <!-- Checkbox and Label -->
      <div class="flex items-center mb-4">
        <input
          type="checkbox"
          id="outlier-detected"
          class="mr-2 w-5 h-5 border-gray-400 rounded focus:ring-blue-500"/>
        <label for="outlier-detected" class="text-black text-lg">Outlier Detected?</label>
      </div>

      <!-- Notes Label -->
      <label for="notes" class="block text-black text-lg mb-2">Notes:</label>

      <!-- Text Area -->
      <textarea
        id="notes"
        placeholder="Type what you outlier you noticed..."
        class="w-full h-2/3 p-2 border border-gray-400 rounded focus:outline-none focus:ring-2 focus:ring-blue-500 resize-none"></textarea>
    </div>
  </div>
  {/if}
</div>