<script>
	import '../app.css';

	let isPopupVisible = false; // Controls the visibility of the popup

	function togglePopup() {
		isPopupVisible = !isPopupVisible;
	}
</script>

<div class="drawer lg:drawer-open">
	<input id="my-drawer-2" type="checkbox" class="drawer-toggle" />
	<div class="drawer-content">
		<slot />
		<label for="my-drawer-2" class="btn btn-primary drawer-button lg:hidden"> Open drawer </label>
	</div>
	<div class="drawer-side">
		<label for="my-drawer-2" aria-label="close sidebar" class="drawer-overlay"></label>
        <ul class="menu bg-base-200 text-base-content min-h-full w-20 p-0 flex flex-col items-center">
            <div class="p-4">
                <img class="size-20" src="/logo.svg" alt="Logo" />
            </div>
          
            <!-- Home Link -->
            <li class="w-full flex justify-center">
                <a href="/" class="tooltip tooltip-right flex items-center justify-center" data-tip="Home">
                  <svg xmlns="http://www.w3.org/2000/svg" class="h-8 w-8" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6" />
                  </svg>
                </a>
            </li>

            <!-- Tutorial Link -->
            <li class="w-full flex justify-center mt-2">
              <a href="/tutorial" class="tooltip tooltip-right flex items-center justify-center" data-tip="Tutorial">
                <svg xmlns="http://www.w3.org/2000/svg" class="h-8 w-8" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                  <path stroke-linecap="round" stroke-linejoin="round" d="M9.879 7.519c1.171-1.025 3.071-1.025 4.242 0 1.172 1.025 1.172 2.687 0 3.712-.203.179-.43.326-.67.442-.745.361-1.45.999-1.45 1.827v.75M21 12a9 9 0 1 1-18 0 9 9 0 0 1 18 0Zm-9 5.25h.008v.008H12v-.008Z" />
                </svg>
              </a>
            </li>
            
        </ul>
	</div>
</div>
