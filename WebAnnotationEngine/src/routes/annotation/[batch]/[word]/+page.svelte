<script>
  // Accessing the `data` prop containing word and selectedVideoData from `+page.js`
  export let data;
  const { batch, word, selectedVideoData } = data;

  import { Pane, Splitpanes } from 'svelte-splitpanes';

  let reviewVideoPaused = true;
  let reviewVideoLooped = true;
  let revPlaybackRate = 1;

  let referenceVideoPaused = true;
  let referenceVideoLooped = true;
  let refPlaybackRate = 1;

  let label = null;

  let currReferenceVideo = 0;
  let currReviewVideo = 0;

  function revPlayPause() {
    reviewVideoPaused = !reviewVideoPaused;
    console.log(reviewVideoPaused);
  }

  function revToggleLoop() {
    reviewVideoLooped = !reviewVideoLooped;
  }

  function revSlowDown() {
    revPlaybackRate = Math.max(0.25, revPlaybackRate - 0.25);
  }

  function revSpeedUp() {
    revPlaybackRate = Math.min(2, revPlaybackRate + 0.25);
  }

  // Handle key press events for keybinds (e.g., play/pause, approve/reject, etc.)
  function onKeyPress(event) {
    switch (event.key) {
      case " ":
        revPlayPause();
        break;
      case "-":
        revToggleLoop ();
        break;
      case "0":
        prevVideo();
        break;
      case "=":
        nextVideo();
        break;
      case "[":
        revSlowDown();
        break;
      case "]":
        revSpeedUp();
        break;
      case "z":
        setLabel("Good");
        break;
      case "x":
        setLabel("Variant");
        break;
      case "c":
        setLabel("Bad");
        break;
      case "v":
        setLabel("Further Review");
        break;
      default:
        return;
    }

    event.preventDefault();
  }


  function setLabel(newLabel) {
    label = label === newLabel ? null : newLabel;
  }

  function prevVideo() {
    if (currReviewVideo > 0) {
      currReviewVideo--;
    }
  }

  function nextVideo() {
    if (currReviewVideo < selectedVideoData.reviews.length - 1) {
      currReviewVideo++;
    }
    const videoElement = document.getElementById('review-video');
    if (videoElement) {
        videoElement.play();
    }
  }

  function refPlayPause() {
    referenceVideoPaused = !referenceVideoPaused;
  }

  function refToggleLoop() {
    referenceVideoLooped = !referenceVideoLooped;
  }

  function refSlowDown() {
    refPlaybackRate = Math.max(0.25, refPlaybackRate - 0.25);
  }

  function refSpeedUp() {
    refPlaybackRate = Math.min(2, refPlaybackRate + 0.25);
  }
</script>

<svelte:window on:keypress={onKeyPress} />

<!-- Header information -->
<div class="flex justify-start w-full">
  <h1 class="text-3xl justify-start pl-5 py-3">Annotating: {word}</h1>
</div>

<!-- Video viewer -->

<h1>Annotating batch: {batch}, word: {word}</h1>

{#if selectedVideoData}
  <div class="h-full w-full">
      <!-- See svelte-splitpanes https://orefalo.github.io/svelte-splitpanes/ -->
      <Splitpanes class="p-4" style="height: 100%">
        <Pane minSize={20} maxSize={63}>
          <!-- Video to review -->
          <video id="review-video" class="w-full h-full" 
              src={`${selectedVideoData.reviews[currReviewVideo]}`}
              loop={reviewVideoLooped}   
              autoplay
              bind:paused={reviewVideoPaused}
              bind:playbackRate={revPlaybackRate} />
        </Pane>
        <Pane minSize={15} maxSize={63}>
          <!-- Reference video -->
          <video class="w-full h-full"
              src={`${selectedVideoData.reference}`}
              loop={referenceVideoLooped}
              autoplay
              bind:paused={referenceVideoPaused}
              bind:playbackRate={refPlaybackRate} />
        </Pane>
      </Splitpanes>
  </div>

  <!-- Video controls -->
  <div class="w-full h-20 flex items-center justify-start">

    <!-- Review Video controls -->
    <div class="w-1/3 h-20 flex items-center justify-start">
      <!-- Pause/Play button-->
      <button on:click={revPlayPause}
          class="bg-[#D9D9D9] hover:bg-[#A9A9A9] text-white rounded-md p-2 md:p-2 lg:p-2.5 xl:p-3 m-3 transition-colors" 
          tabindex="-1">
        <img id="playPauseIcon" class="w-5 h-5 md:w-6 md:h-6 lg:w-7 lg:h-7 xl:w-8 xl:h-8"
            src="{reviewVideoPaused ? "/play" : "/pause"}.svg"
            alt="paused icon">
      </button>

      <button on:click={revToggleLoop}
          class="bg-[#D9D9D9] hover:bg-[#A9A9A9] text-white rounded-md p-2 md:p-2 lg:p-2.5 xl:p-3 m-3 transition-colors"
          tabindex="-1">
        <img id="loopIcon" class="w-5 h-5 md:w-6 md:h-6 lg:w-7 lg:h-7 xl:w-8 xl:h-8"
            src="{reviewVideoLooped ? "/loop" : "/not-looped" }.svg"
            alt="play icon">
      </button>

      <div class="join m-3">
          <!-- Slow down video button-->
          <button on:click={revSlowDown}
            class="bg-[#D9D9D9] hover:bg-[#A9A9A9] text-white p-2 md:p-2 lg:p-2.5 xl:p-3 rounded-md join-item transition-colors"
            tabindex="-1">
            <img class="w-8 h-8 md:w-7.5 md:h-7.5 lg:w-8 lg:h-8 xl:w-9 xl:h-9" src="/slow-down-dark.svg" alt="turtle icon to indicate slow down">
          </button>

          <!-- Playback rate reporter -->
          <div class="bg-[#D9D9D9] flex text-black w-20 rounded-md p-2 md:p-2 lg:p-2.5 xl:p-3 join-item transition-colors">
            <div class="flex items-center m-auto">{revPlaybackRate.toFixed(2)}&times;</div>
          </div>

          <!-- Speed up video button-->
          <button on:click={revSpeedUp} 
            class="bg-[#D9D9D9] hover:bg-[#A9A9A9] text-white rounded-md  p-2 md:p-2 lg:p-2.5 xl:p-3 join-item transition-colors"
            tabindex="-1">
            <img class="w-5 h-5 md:w-6 md:h-6 lg:w-7 lg:h-7 xl:w-8 xl:h-8" src="/speed-up-dark.svg" alt="bunny icon to indicate speed up">
          </button>
      </div>

      <!-- Previous video -->
      <div class="join m-3">
          <button on:click={prevVideo}
            class="bg-[#D9D9D9] hover:bg-[#A9A9A9] text-white rounded-md p-2 md:p-2 lg:p-2.5 xl:p-3 join-item transition-colors"
            tabindex="-1">
            <img class="w-5 h-5 md:w-6 md:h-6 lg:w-7 lg:h-7 xl:w-8 xl:h-8" src="/previous.svg" alt="previous video icon">
          </button>

          <!-- Next video -->
          <button on:click={nextVideo}
            class="bg-[#D9D9D9] hover:bg-[#A9A9A9] text-white rounded-md p-2 md:p-2 lg:p-2.5 xl:p-3 join-item transition-colors"
            tabindex="-1">
            <img class="w-5 h-5 md:w-6 md:h-6 lg:w-7 lg:h-7 xl:w-8 xl:h-8" src="/next.svg" alt="next video icon">
          </button>
      </div>
    </div>

    <!-- Annotation labeling -->
    <div class="w-1/3 h-20 flex items-center justify-start">
      <!-- Good button -->
      <button on:click={() => setLabel("Good")}
          class="bg-[#D9D9D9] hover:bg-[#A9A9A9] text-white rounded-md p-2 md:p-2 lg:p-2.5 xl:p-3 m-3 transition-colors"
          tabindex="-1">
        <img id="good-button" class="w-5 h-5 md:w-6 md:h-6 lg:w-7 lg:h-7 xl:w-8 xl:h-8"
            src="/thumbs-up.svg"
            alt="thumbs up icon">
      </button>

      <!-- Variant button -->
      <button on:click={() => setLabel("Variant")}
          class="bg-[#D9D9D9] hover:bg-[#A9A9A9] text-white rounded-md p-2 md:p-2 lg:p-2.5 xl:p-3 m-3 transition-colors"
          tabindex="-1">
        <img id="variant-button" class="w-5 h-5 md:w-6 md:h-6 lg:w-7 lg:h-7 xl:w-8 xl:h-8"
            src="/variant.svg"
            alt="icon">
      </button>

      <!-- Bad button -->
      <button on:click={() => setLabel("Bad")}
          class="bg-[#D9D9D9] hover:bg-[#A9A9A9] text-white rounded-md p-2 md:p-2 lg:p-2.5 xl:p-3 m-3 transition-colors"
          tabindex="-1">
        <img id="bad-button" class="w-5 h-5 md:w-6 md:h-6 lg:w-7 lg:h-7 xl:w-8 xl:h-8"
            src="/thumbs-down.svg"
            alt="thumbs down icon">
      </button>

      <!-- Further Review button -->
      <button on:click={() => setLabel("Further Review")}
          class="bg-[#D9D9D9] hover:bg-[#A9A9A9] text-white rounded-md p-2 md:p-2 lg:p-2.5 xl:p-3 m-3 transition-colors"
          tabindex="-1">
        <img id="further-review-button" class="w-5 h-5 md:w-6 md:h-6 lg:w-7 lg:h-7 xl:w-8 xl:h-8"
            src="/archive.svg"
            alt="archive icon">
      </button>

      <!-- Label -->
      <div class="flex w-100px ml-3 min-w-[3rem] md:min-w-[6rem] lg:min-w-[8rem] h-20">
        <div 
          class="flex items-center gap-2 p-2 md:p-2 lg:p-2.5 xl:p-3 m-3 rounded-md transition-colors whitespace-nowrap"
          class:bg-green-200={label === "Good"}
          class:bg-yellow-200={label === "Variant"}
          class:bg-red-200={label === "Bad"}
          class:bg-blue-200={label === "Further Review"}
          class:bg-[#D9D9D9]={!label}>
          {#if label}
            {#if label === "Good"}
              <img src="/thumbs-up.svg" class="w-6 h-6" alt="thumbs up icon" />
            {:else if label === "Variant"}
              <img src="/variant.svg" class="w-6 h-6" alt="variant icon" />
            {:else if label === "Bad"}
              <img src="/thumbs-down.svg" class="w-6 h-6" alt="thumbs down icon" />
            {:else if label === "Further Review"}
              <img src="/archive.svg" class="w-6 h-6" alt="archive icon" />
            {/if}
            <p class="text-sm md:text-md lg:text-lg">{label}</p>
          {:else}
            <p class="text-sm md:text-md lg:text-lg">None</p>
          {/if}
        </div>
      </div>
    </div>

    <!-- Reference Video buttons -->
    <div class="w-1/3 h-20 flex items-center justify-end">
      <!-- Pause/Play button-->
      <button on:click={refPlayPause}
          class="bg-[#D9D9D9] hover:bg-[#A9A9A9] text-white rounded-md p-2 md:p-2 lg:p-2.5 xl:p-3 m-3 transition-colors"
          tabindex="-1">
        <img id="playPauseIcon" class="w-5 h-5 md:w-6 md:h-6 lg:w-7 lg:h-7 xl:w-8 xl:h-8"
            src="{referenceVideoPaused ? "/play" : "/pause"}.svg"
            alt="paused icon">
      </button>

      <button on:click={refToggleLoop}
          class="bg-[#D9D9D9] hover:bg-[#A9A9A9] text-white rounded-md p-2 md:p-2 lg:p-2.5 xl:p-3 m-3 transition-colors"
          tabindex="-1">
        <img id="loopIcon" class="w-5 h-5 md:w-6 md:h-6 lg:w-7 lg:h-7 xl:w-8 xl:h-8"
            src="{referenceVideoLooped ? "/loop" : "/not-looped" }.svg"
            alt="play icon">
      </button>

      <div class="join m-3">
          <!-- Slow down video button-->
          <button on:click={refSlowDown} 
            class="bg-[#D9D9D9] hover:bg-[#A9A9A9] text-white p-2 md:p-2 lg:p-2.5 xl:p-3 rounded-md join-item transition-colors"
            tabindex="-1">
            <img class="w-8 h-8 md:w-7.5 md:h-7.5 lg:w-8 lg:h-8 xl:w-9 xl:h-9" src="/slow-down-dark.svg" alt="turtle icon to indicate slow down">
          </button>

          <!-- Playback rate reporter -->
          <div class="bg-[#D9D9D9] flex text-black w-20 rounded-md p-2 md:p-2 lg:p-2.5 xl:p-3 join-item transition-colors">
            <div class="flex items-center m-auto">{refPlaybackRate.toFixed(2)}&times;</div>
          </div>

          <!-- Speed up video button-->
          <button on:click={refSpeedUp}
            class="bg-[#D9D9D9] hover:bg-[#A9A9A9] text-white rounded-md  p-2 md:p-2 lg:p-2.5 xl:p-3 join-item transition-colors"
            tabindex="-1">
            <img class="w-5 h-5 md:w-6 md:h-6 lg:w-7 lg:h-7 xl:w-8 xl:h-8" src="/speed-up-dark.svg" alt="bunny icon to indicate speed up">
          </button>
      </div>
    </div>

  </div>
{:else}
  <p>No video data available for the word "{word}".</p>
{/if}