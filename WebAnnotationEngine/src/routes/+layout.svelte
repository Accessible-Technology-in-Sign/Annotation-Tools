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
    </ul>
  </div>
</div>