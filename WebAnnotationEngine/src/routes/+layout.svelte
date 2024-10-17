<script>
	import '../app.css';
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
      <img class="size-20" src="logo.svg" />
      <!-- Sidebar content here -->
      <li id="review-batch">
          <a><img class="size-20" src="review-batch.svg"></a>
      </li>
      <li><a><img class="size-20" src="sign.svg"></a></li>
      <li><a><img class="size-20" src="comment.svg"></a></li>
    </ul>
  </div>
</div>
