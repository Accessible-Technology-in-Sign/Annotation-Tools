<script>
  // Accessing the `data` prop containing word and selectedVideoData from `+page.js`
  export let data;
  import { onMount } from 'svelte';
  import { Pane, Splitpanes } from 'svelte-splitpanes';
  import {writable} from "svelte/store";
  import { page } from '$app/stores';
  import { goto } from '$app/navigation';

  export const userAnnot = writable({})

  const { batch, word, selectedVideoData } = data;

  const API_BASE = "http://127.0.0.1:5000";
  const basename = (p) => (p || "").split("/").pop();
  const username = (localStorage.getItem("username") || "").trim();
  const toFlask = (p) => {
    const clean = p.replace(/^\/?/, "");
    return `${API_BASE}/${encodeURI(clean)}`;
  };

  onMount(async () => {
    if (!username || !selectedVideoData?.reviews?.length) return;

    const url = $page.url; // SvelteKit store value
    const qVideo = url.searchParams.get('video');
    const qIdx   = url.searchParams.get('idx');

    if (qIdx !== null) {
      const i = Number(qIdx);
      if (!Number.isNaN(i) && i >= 0 && i < (selectedVideoData?.reviews?.length ?? 0)) {
        currReviewVideo = i;
      }
    } else if (qVideo) {
      const i = selectedVideoData.reviews.findIndex(p =>
        p === qVideo || basename(p) === basename(qVideo)
      );
      if (i >= 0) currReviewVideo = i;
    }

    const res = await fetch(
      `${API_BASE}/annots?user=${encodeURIComponent(username)}&sign=${encodeURIComponent(word)}`
    );
    if (!res.ok) return;
    const saved = await res.json(); 
    const next = {};
    selectedVideoData.reviews.forEach((p, idx) => {
      const a = saved[basename(p)];
      if (a && a.label) {
        next[idx] = { annot_label: a.label, annot_comments: a.comments || "" };
      }
    });
    userAnnot.set(next);

    // Pre-fill current video’s fields if present
    const cur = saved[basename(selectedVideoData.reviews[currReviewVideo])];
    if (cur) {
      label = cur.label;
      comments = cur.comments || "";
    }
  });

  let reviewVideoPaused = true;
  let reviewVideoLooped = true;
  let revPlaybackRate = 1;

  let referenceVideoPaused = true;
  let referenceVideoLooped = true;
  let refPlaybackRate = 1;

  // @ts-ignore 
  let label = null;

  let comments = "";

  let currReviewVideo = 0;

  let refVisible = true;

  function revPlayPause() {
    reviewVideoPaused = !reviewVideoPaused;
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

  $: current = $userAnnot[currReviewVideo] ?? { annot_label: null, annot_comments: "" };
  $: label = current.annot_label ?? null;

  async function addAnnot(annot_label, annot_comments, annot_user) {
    if (!annot_label || String(annot_label).trim() === "") return;

    const payload = {
      label: annot_label,
      sign: word,
      user: annot_user,
      comments: annot_comments ?? "",
      time: Date.now(),
      video_path: selectedVideoData.reviews[currReviewVideo],
    };

    try {
      const res = await fetch(`${API_BASE}/add_annot`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });
      const data = await res.json();
      if (!res.ok) console.warn("Save failed:", data?.error || res.statusText);
    } catch (e) {
      console.error("Save error:", e);
    }
  }

  // Handle key press events for keybinds (e.g., play/pause, approve/reject, etc.)
  function onKeyPress(event) {
    if (event.target.tagName === "INPUT" || event.target.tagName === "TEXTAREA") {
        return;
    }
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
    label = newLabel;

      userAnnot.update(s => ({
        ...s,
        [currReviewVideo]: { annot_label: newLabel, annot_comments: comments ?? "" }
      }));

      addAnnot(newLabel, comments ?? "", username);
  }

  function prevVideo() {
    if (currReviewVideo > 0) {
      currReviewVideo--;
      updateUrlForCurrentVideo();
    }
  }

  function resetState(){
    // reviewVideoPaused = true;
    // referenceVideoPaused = true;

    label = null;
    comments = "";
  }

  function nextVideo() {
    if (currReviewVideo < selectedVideoData.reviews.length - 1) {
      currReviewVideo++;
      updateUrlForCurrentVideo();
      const videoElement = document.getElementById('review-video');
      if (videoElement) {
          videoElement.play();
      }
    }  else {
      viewSummary();
    }

    resetState();

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

  function toggleRefVisibility() {
    refVisible = !refVisible;
  }

  function viewSummary() {
    goto(`/summary/${batch}/${word}`);
  }

  function updateUrlForCurrentVideo() {
    const full = selectedVideoData.reviews[currReviewVideo];
    const q = new URLSearchParams({ video: full });
    goto(`/annotation/${batch}/${word}?${q.toString()}`, {
      replaceState: true, keepfocus: true, noscroll: true
    });
  }

  $: total = selectedVideoData?.reviews?.length ?? 0;
  $: completed = Object.values($userAnnot)
    .filter(v => v && typeof v.annot_label === "string" && v.annot_label.trim() !== "")
    .length;
  $: percent = total ? Math.round((completed / total) * 100) : 0;
</script>

<style>
    .visibility-button {
    background: rgb(0, 176, 251);
    color: white;
    border: none;
    padding: 6px 12px;
    border-radius: 6px;
    cursor: pointer;
  }

  .visibility-button:hover {
    background: rgb(2, 109, 155);
  }
</style>


<svelte:window on:keypress={onKeyPress} />

{#if selectedVideoData}
    <div class="flex flex-col h-screen">
      <!-- header -->
      <div class="shrink-0 px-4 py-2 flex justify-between items-center">
        <h1 class="text-3xl">Annotating: {word}</h1>
        <h2 class="text-md text-center">Annotating batch: {batch}, word: {word}</h2>
        <div>
          <button on:click={toggleRefVisibility} class="visibility-button">
            {refVisible ? 'Hide Reference Video' : 'Show Reference Video'}
          </button>
          <button on:click={viewSummary} class="visibility-button" style="margin-left: 8px;">
            View Summary
          </button>
        </div>
      </div>

      <div class="px-4 pb-2">
        <div class="flex items-center justify-between mb-1">
          <div class="text-sm text-gray-700">
            {completed}/{total} • {percent}% complete
          </div>
          <div class="text-sm text-gray-500">
            Video {currReviewVideo + 1} of {total}
          </div>
        </div>
        <div class="w-full h-3 bg-gray-200 rounded">
          <div
            class="h-3 rounded bg-blue-500 transition-all"
            style="width: {percent}%;"
            aria-valuemin="0"
            aria-valuemax="100"
            aria-valuenow={percent}
            role="progressbar"
          />
        </div>
      </div>

      <!-- See svelte-splitpanes https://orefalo.github.io/svelte-splitpanes/ -->
      <div class="flex-grow overflow-hidden">
        <Splitpanes class="h-full w-full">
          <Pane minSize={20} maxSize={63}>
            <!-- Video to review -->
            <video id="review-video" class="w-full h-full" 
                src={toFlask(selectedVideoData.reviews[currReviewVideo])}
                loop={reviewVideoLooped}   
                autoplay
                bind:paused={reviewVideoPaused}
                bind:playbackRate={revPlaybackRate} />
          </Pane>
          {#if refVisible}
            <Pane>
              <Splitpanes horizontal={true}>
                <Pane minSize={15} maxSize={80}>
                  <!-- Reference video -->
                  <video class="w-full h-full"
                      src={toFlask(selectedVideoData.reference)}
                      loop={referenceVideoLooped}
                      autoplay
                      bind:paused={referenceVideoPaused}
                      bind:playbackRate={refPlaybackRate} />
                </Pane>
                <Pane>
                  <!-- Comment panel -->
                  <div class="w-full h-full bg-aquamarine p-0">
                    <textarea
                      bind:value={comments}
                      on:blur={() => { if (label) addAnnot(label, comments ?? "", username); }}
                      on:keydown={(e) => {
                        if ((e.metaKey || e.ctrlKey) && e.key === 'Enter' && label) {
                          addAnnot(label, comments ?? "", username);
                        }
                      }}
                      class="w-full h-full p-10 text-left align-top resize-none outline-none bg-transparent text-black text-mn"
                      placeholder="Add any comments here..."
                    ></textarea>
                  </div>
                </Pane>
              </Splitpanes>
            </Pane>
          {/if}
        </Splitpanes>
    </div>

  <!-- Video controls -->
    <div class="shrink-0 h-20 flex items-center bg-white border-t border-gray-300 z-30">
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
  </div>
{:else}
  <p>No video data available for the word "{word}".</p>
{/if}