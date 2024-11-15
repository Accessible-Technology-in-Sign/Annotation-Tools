<script>
  // Accessing the `data` prop containing word and selectedVideoData from `+page.js`
  export let data;
  const { word, selectedVideoData } = data;

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

  function prevVideo() {
    if (currReviewVideo > 0) {
      currReviewVideo--;
    }
  }

  function nextVideo() {
    if (currReviewVideo < selectedVideoData.reviewVideos.length - 1) {
      currReviewVideo++;
    }
  }

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
</script>

<svelte:window on:keypress={onKeyPress} />

<!-- Video viewer -->
<h1>Annotating: {word}</h1>
{#if selectedVideoData}
  <div class="h-full w-full">
    <Splitpanes class="p-4" style="height: 100%">
      <Pane class="rounded-xl" minSize={20}>
        <!-- Video to review -->
        <video class="w-full h-full" src={selectedVideoData.reviewVideos[currReviewVideo]}
            loop={reviewVideoLooped}
            bind:paused={reviewVideoPaused}
            bind:playbackRate={playbackRate} />
      </Pane>
      <Pane class="rounded-xl" minSize={15}>
        <!-- Reference video -->
        <video class="w-full h-full"
            src={selectedVideoData.referenceVideo}
            controls loop />  
      </Pane>
    </Splitpanes>
  </div>

  <!-- Video controls -->
  <div class="w-full h-20 flex items-center justify-start">
    <button on:click={playPause} class="bg-[#D9D9D9] hover:bg-[#A9A9A9] text-white rounded-md p-2 md:p-2 lg:p-2.5 xl:p-3 m-3 transition-colors">
      <img id="playPauseIcon" class="w-5 h-5 md:w-6 md:h-6 lg:w-7 lg:h-7 xl:w-8 xl:h-8" src={reviewVideoPaused ? "/play.svg" : "/pause.svg"} alt="paused icon">
    </button>

    <button on:click={toggleLoop} class="bg-[#D9D9D9] hover:bg-[#A9A9A9] text-white rounded-md p-2 md:p-2 lg:p-2.5 xl:p-3 m-3 transition-colors">
      <img id="loopIcon" class="w-5 h-5 md:w-6 md:h-6 lg:w-7 lg:h-7 xl:w-8 xl:h-8" src={reviewVideoLooped ? "/loop.svg" : "/not-looped.svg"} alt="play icon">
    </button>

    <div class="join m-3">
      <button on:click={slowDown} class="bg-[#D9D9D9] hover:bg-[#A9A9A9] text-white p-2 md:p-2 lg:p-2.5 xl:p-3 rounded-md join-item transition-colors">
        <img class="w-8 h-8 md:w-7.5 md:h-7.5 lg:w-8 lg:h-8 xl:w-9 xl:h-9" src="/slow-down-dark.svg" alt="turtle icon to indicate slow down">
      </button>

      <div class="bg-[#D9D9D9] flex text-black w-20 rounded-md p-2 md:p-2 lg:p-2.5 xl:p-3 join-item transition-colors">
        <div class="flex items-center m-auto">{playbackRate.toFixed(2)}&times;</div>
      </div>

      <button on:click={speedUp} class="bg-[#D9D9D9] hover:bg-[#A9A9A9] text-white rounded-md  p-2 md:p-2 lg:p-2.5 xl:p-3 join-item transition-colors">
        <img class="w-5 h-5 md:w-6 md:h-6 lg:w-7 lg:h-7 xl:w-8 xl:h-8" src="/speed-up-dark.svg" alt="bunny icon to indicate speed up">
      </button>
    </div>

    <!-- Previous and Next Video Buttons -->
    <div class="join m-3">
      <button on:click={prevVideo} class="bg-[#D9D9D9] hover:bg-[#A9A9A9] text-white rounded-md p-2 md:p-2 lg:p-2.5 xl:p-3 join-item transition-colors">
        <img class="w-5 h-5 md:w-6 md:h-6 lg:w-7 lg:h-7 xl:w-8 xl:h-8" src="/previous.svg">
      </button>
      <button on:click={nextVideo} class="bg-[#D9D9D9] hover:bg-[#A9A9A9] text-white rounded-md p-2 md:p-2 lg:p-2.5 xl:p-3 join-item transition-colors">
        <img class="w-5 h-5 md:w-6 md:h-6 lg:w-7 lg:h-7 xl:w-8 xl:h-8" src="/next.svg">
      </button>
    </div>

    <!-- Additional control buttons (like thumbs up/down) -->
    <div class="flex gap-3 ml-6">
      <button class="bg-[#D9D9D9] hover:bg-[#A9A9A9] text-white rounded-md p-2 md:p-2 lg:p-2.5 xl:p-3 join-item transition-colors">
        <img class="w-5 h-5 md:w-6 md:h-6 lg:w-7 lg:h-7 xl:w-8 xl:h-8" src="/thumbs-up.svg">
      </button>
      <button class="bg-[#D9D9D9] hover:bg-[#A9A9A9] text-white rounded-md p-2 md:p-2 lg:p-2.5 xl:p-3 join-item transition-colors">
        <img class="w-5 h-5 md:w-6 md:h-6 lg:w-7 lg:h-7 xl:w-8 xl:h-8" src="/thumbs-down.svg">
      </button>
      <button class="bg-[#D9D9D9] hover:bg-[#A9A9A9] text-white rounded-md p-2 md:p-2 lg:p-2.5 xl:p-3 join-item transition-colors">
        <img class="w-5 h-5 md:w-6 md:h-6 lg:w-7 lg:h-7 xl:w-8 xl:h-8" src="/archive.svg">
      </button>
    </div>
  </div>
{:else}
  <p>No video data available for the word "{word}".</p>
{/if}
