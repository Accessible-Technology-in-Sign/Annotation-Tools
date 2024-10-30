<script>
  import { Pane, Splitpanes } from 'svelte-splitpanes';
  let videoElement;
  let reviewVideoPaused = true;
  let reviewVideoLooped = true;
  let playbackRate = 1;

  // Toggle playback of the video to be reviewed. You could add something similar for
  // the reference video too.
  function playPause() {
    reviewVideoPaused = !reviewVideoPaused;
    document.getElementById("playPauseIcon").src = reviewVideoPaused ? "play.svg" : "pause.svg";
  }

  function letLoop() {
    reviewVideoLooped = !reviewVideoLooped;
    videoElement.loop = reviewVideoLooped;
    document.getElementById("loopIcon").src = reviewVideoLooped ? "not-looped.svg" : "loop.svg";
  }

  function handleVideoEnded() {
    !reviewVideoPaused;
    document.getElementById("playPauseIcon").src = "play.svg";
  }

  function slowDown() {
    playbackRate = Math.max(0.25, playbackRate - 0.25);
  }

  function speedUp() {
    playbackRate = Math.min(2, playbackRate + 0.25);
  }

  // Handle key press events for keybinds (e.g., play/pause, approve/reject, etc.)
  function onKeyPress(event) {
    switch (event.key) {
      case " ":
        playPause();
        event.preventDefault();
        break;
    }

    switch (event.key) {
      case "-":
        letLoop();
        event.preventDefault();
        break;
    }

    switch (event.key) {
      case "[":
        slowDown();
        event.preventDefault();
        break;
    }

    switch (event.key) {
      case "]":
        speedUp();
        event.preventDefault();
        break;
    }

  }
</script>

<!-- Video viewer -->
<div class="h-full w-full">
    <!-- See svelte-splitpanes https://orefalo.github.io/svelte-splitpanes/ -->
    <Splitpanes class="p-4" style="height: 100%">
      <Pane class="rounded-xl" minSize={20}>
        <!-- Video to review -->
        <video class="w-full h-full" src="ReviewVideos/all_work_and_no_play_rh_wire.mp4"
            loop
            bind:this={videoElement}
            bind:paused={reviewVideoPaused}
            on:ended={handleVideoEnded}
            bind:playbackRate={playbackRate} />
      </Pane>
      <Pane class="rounded-xl" minSize={15}>
        <!-- Reference video -->
        <video class="w-full h-full"
            src="ReviewVideos/all_work_and_no_play_rh_wire.mp4"
            controls loop />
      </Pane>
    </Splitpanes>
</div>

<!-- Video controls -->
<div class="w-full h-20 flex items-center justify-start">
  <button class="bg-[#D9D9D9] hover:bg-[#A9A9A9] text-white rounded-md p-2 md:p-2 lg:p-2.5 xl:p-3 m-3">
    <img class="w-5 h-5 md:w-6 md:h-6 lg:w-7 lg:h-7 xl:w-8 xl:h-8" src="pause.svg">
  </button>

  <button class="bg-[#D9D9D9] hover:bg-[#A9A9A9] text-white rounded-md p-2 md:p-2 lg:p-2.5 xl:p-3 m-3">
    <img class="w-5 h-5 md:w-6 md:h-6 lg:w-7 lg:h-7 xl:w-8 xl:h-8" src="loop.svg">
  </button>

  <!-- Slow down video button-->
  <button on:click={slowDown} class="bg-[#D9D9D9] hover:bg-[#A9A9A9] text-white rounded-md p-2 md:p-2 lg:p-2.5 xl:p-3 m-3">
    <img class="w-8 h-8 md:w-7.5 md:h-7.5 lg:w-8 lg:h-8 xl:w-9 xl:h-9" src="slow-down-dark.svg">
  </button>

  <!-- Speed up video button-->
  <button on:click={speedUp} class="bg-[#D9D9D9] hover:bg-[#A9A9A9] text-white rounded-md p-2 md:p-2 lg:p-2.5 xl:p-3 m-3">
    <img class="w-5 h-5 md:w-6 md:h-6 lg:w-7 lg:h-7 xl:w-8 xl:h-8" src="speed-up-dark.svg">
  </button>
</div>
