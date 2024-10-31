<script>
  import { Pane, Splitpanes } from 'svelte-splitpanes';
  let reviewVideoPaused = true;
  let reviewVideoLooped = true;
  let playbackRate = 1;

  let currReferenceVideo = 0;
  let currReviewVideo = 0;

  function playPause() {
    reviewVideoPaused = !reviewVideoPaused;
  }

  function toggleLoop() {
    reviewVideoLooped = !reviewVideoLooped;
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
        break;
      case "-":
        toggleLoop();
        break;
      case "0":
        prevVideo();
        break;
      case "=":
        nextVideo();
        break;
      case "[":
        slowDown();
        break;
      case "]":
        speedUp();
        break;
      default:
        return;
    }

    event.preventDefault();
  }

  const videoData = [
    {
      referenceVideo: "/ReviewVideos/all_work_and_no_play_rh_wire.mp4",
      reviewVideos: [
         "/ReviewVideos/all_work_and_no_play_rh_wire.mp4",
         "/ReviewVideos/coming_up_with_killer_sound_bites_rh_wire.mp4",
         "/ReviewVideos/did_you_have_a_good_time_rh_wire.mp4"
      ]
    },
    {
      referenceVideo: "/ReviewVideos/coming_up_with_killer_sound_bites_rh_wire.mp4",
      reviewVideos: [
         "/ReviewVideos/coming_up_with_killer_sound_bites_rh_wire.mp4"
      ]
    }
  ];

  function prevVideo() {
    if (currReviewVideo > 0) {
      currReviewVideo--;
    }
  }

  function nextVideo() {
    if (currReviewVideo < videoData[currReferenceVideo].reviewVideos.length - 1) {
      currReviewVideo++;
    }
  }

</script>

<svelte:window on:keypress={onKeyPress} />

<!-- Video viewer -->
<div class="h-full w-full">
    <!-- See svelte-splitpanes https://orefalo.github.io/svelte-splitpanes/ -->
    <Splitpanes class="p-4" style="height: 100%">
      <Pane class="rounded-xl" minSize={20}>
        <!-- Video to review -->
        <video class="w-full h-full" src={videoData[currReferenceVideo].reviewVideos[currReviewVideo]}
            loop={reviewVideoLooped}
            bind:paused={reviewVideoPaused}
            bind:playbackRate={playbackRate} />
      </Pane>
      <Pane class="rounded-xl" minSize={15}>
        <!-- Reference video -->
        <video class="w-full h-full"
            src={videoData[currReferenceVideo].referenceVideo}
            controls loop />
      </Pane>
    </Splitpanes>
</div>

<!-- Video controls -->
<div class="w-full h-20 flex items-center justify-start">

  <!-- Pause/Play button-->
  <button on:click={playPause}
      class="bg-[#D9D9D9] hover:bg-[#A9A9A9] text-white rounded-md p-2 md:p-2 lg:p-2.5 xl:p-3 m-3">
    <img id="playPauseIcon" class="w-5 h-5 md:w-6 md:h-6 lg:w-7 lg:h-7 xl:w-8 xl:h-8"
        src="{reviewVideoPaused ? "play" : "pause"}.svg"
        alt="paused icon">
  </button>

  <button on:click={toggleLoop}
      class="bg-[#D9D9D9] hover:bg-[#A9A9A9] text-white rounded-md p-2 md:p-2 lg:p-2.5 xl:p-3 m-3">
    <img id="loopIcon" class="w-5 h-5 md:w-6 md:h-6 lg:w-7 lg:h-7 xl:w-8 xl:h-8"
        src="{reviewVideoLooped ? "loop" : "not-looped" }.svg"
        alt="play icon">
  </button>

  <!-- Slow down video button-->
  <button on:click={slowDown} class="bg-[#D9D9D9] hover:bg-[#A9A9A9] text-white rounded-md p-2 md:p-2 lg:p-2.5 xl:p-3 m-3">
    <img class="w-8 h-8 md:w-7.5 md:h-7.5 lg:w-8 lg:h-8 xl:w-9 xl:h-9" src="slow-down-dark.svg" alt="turtle icon to indicate slow down">
  </button>

  <!-- Speed up video button-->
  <button on:click={speedUp} class="bg-[#D9D9D9] hover:bg-[#A9A9A9] text-white rounded-md p-2 md:p-2 lg:p-2.5 xl:p-3 m-3">
    <img class="w-5 h-5 md:w-6 md:h-6 lg:w-7 lg:h-7 xl:w-8 xl:h-8" src="speed-up-dark.svg" alt="bunny icon to indicate speed up">
  </button>

  <!-- Previous video -->
  <button on:click={prevVideo} class="bg-[#D9D9D9] hover:bg-[#A9A9A9] text-white rounded-md p-2 md:p-2 lg:p-2.5 xl:p-3 m-3">
    <img class="w-5 h-5 md:w-6 md:h-6 lg:w-7 lg:h-7 xl:w-8 xl:h-8" src="previous.svg">
  </button>

  <!-- Next video -->
  <button on:click={nextVideo} class="bg-[#D9D9D9] hover:bg-[#A9A9A9] text-white rounded-md p-2 md:p-2 lg:p-2.5 xl:p-3 m-3">
    <img class="w-5 h-5 md:w-6 md:h-6 lg:w-7 lg:h-7 xl:w-8 xl:h-8" src="next.svg">
  </button>
</div>
