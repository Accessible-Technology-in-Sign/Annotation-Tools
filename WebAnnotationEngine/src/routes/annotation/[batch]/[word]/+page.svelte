<script>
  export let data;
  import { browser } from '$app/environment';
  import { onMount } from 'svelte';
  import { Pane, Splitpanes } from 'svelte-splitpanes';
  import { writable } from 'svelte/store';
  import { page } from '$app/stores';
  import { goto } from '$app/navigation';

  export const userAnnot = writable({});

  const { batch, word, selectedVideoData } = data;
  const API_BASE = 'http://127.0.0.1:5000';
  const basename = (p) => (p || '').split('/').pop();
  const username = (localStorage.getItem('username') || '').trim();
  const toFlask = (p) => {
    const clean = p.replace(/^\/?/, '');
    return `${API_BASE}/${encodeURI(clean)}`;
  };

  onMount(async () => {
    if (!username || !selectedVideoData?.reviews?.length) return;

    const qVideo = $page.url.searchParams.get('video');
    if (qVideo) {
      const i = selectedVideoData.reviews.findIndex(
        (p) => p === qVideo || basename(p) === basename(qVideo)
      );
      if (i >= 0) currReviewVideo = i;
    }

    const res = await fetch(`${API_BASE}/annots?user=${username}&sign=${word}`);
    if (!res.ok) return;
    const saved = await res.json();
    const next = {};
    selectedVideoData.reviews.forEach((p, idx) => {
      const a = saved[basename(p)];
      if (a?.label) {
        next[idx] = { annot_label: a.label, annot_comments: a.comments || '' };
      }
    });
    userAnnot.set(next);
  });

  let reviewVideoPaused = true;
  let reviewVideoLooped = true;
  let revPlaybackRate = 1;
  let refVisible = true;

  let referenceVideoPaused = true;
  let referenceVideoLooped = true;
  let refPlaybackRate = 1;

  let label = null;
  let comments = '';

  let currReviewVideo = 0;

  let videoEl;
  let duration = 0;
  let clipStart = 0;
  let clipEnd = 0;

  onMount(() => {
    if (!browser) return;
    const setMeta = () => {
      if (!videoEl) return;
      const d = Number.isFinite(videoEl.duration) ? videoEl.duration : 0;
      if (d > 0) {
        duration = d;
        if (clipEnd == null || typeof clipEnd !== 'number' || clipEnd <= 0) {
          clipEnd = duration;
        } else {
          clipEnd = Math.min(clipEnd, duration);
        }
        if (clipStart == null) clipStart = 0;
      }
    };
    if (videoEl) {
      videoEl.addEventListener('loadedmetadata', setMeta);
      setMeta();
    }
  });

  function onTimeUpdate() {
    if (!videoEl) return;
    clipStart = Math.max(0, Math.min(Number(clipStart) || 0, duration || clipStart));
    clipEnd = Math.max(clipStart, Math.min(Number(clipEnd) || clipStart, duration || clipEnd));

    if (videoEl.currentTime >= clipEnd - 0.05) {
      if (reviewVideoLooped) {
        videoEl.currentTime = clipStart;
      } else {
        videoEl.pause();
        reviewVideoPaused = true;
      }
    }
  }

  function revPlayPause() {
    reviewVideoPaused = !reviewVideoPaused;
    if (!reviewVideoPaused) {
      clipStart = Math.max(0, Math.min(clipStart, duration));
      clipEnd = Math.max(clipStart, Math.min(clipEnd, duration));
      if (videoEl && (videoEl.currentTime < clipStart || videoEl.currentTime > clipEnd)) {
        videoEl.currentTime = clipStart;
      }
    }
  }

  const revToggleLoop = () => (reviewVideoLooped = !reviewVideoLooped);
  const revSlowDown = () => (revPlaybackRate = Math.max(0.25, revPlaybackRate - 0.25));
  const revSpeedUp = () => (revPlaybackRate = Math.min(2, revPlaybackRate + 0.25));

  $: current = $userAnnot[currReviewVideo] ?? { annot_label: null, annot_comments: '' };
  $: label = current.annot_label ?? null;

  async function addAnnot(annot_label, annot_comments, annot_user) {
    if (!annot_label || String(annot_label).trim() === '') return;

    const payload = {
      label: annot_label,
      sign: word,
      user: annot_user,
      comments: annot_comments || '',
      time: Date.now(),
      video_path: selectedVideoData.reviews[currReviewVideo]
    };

    try {
      const res = await fetch(`${API_BASE}/add_annot`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });
      if (!res.ok) {
        const data = await res.json();
        console.warn('Save failed:', data?.error || res.statusText);
      } else {
        localStorage.setItem(
          `lastActivity:${username}`,
          JSON.stringify({
            batch,
            word,
            timestamp: new Date().toISOString(),
            video: basename(selectedVideoData.reviews[currReviewVideo])
          })
        );
      }
    } catch (e) {
      console.error('Save error:', e);
    }
  }

  // Handle key press events for keybinds (e.g., play/pause, approve/reject, etc.)
  function onKeyPress(event) {
    if (event.target.tagName === 'INPUT' || event.target.tagName === 'TEXTAREA') return;

    const actions = {
      ' ': revPlayPause,
      '-': revToggleLoop,
      '0': prevVideo,
      '=': nextVideo,
      '[': revSlowDown,
      ']': revSpeedUp,
      z: () => setLabel('Good'),
      x: () => setLabel('Variant'),
      c: () => setLabel('Bad'),
      v: () => setLabel('Further Review')
    };

    if (actions[event.key]) {
      event.preventDefault();
      actions[event.key]();
    }
  }

  function setLabel(newLabel) {
    label = newLabel;

    userAnnot.update((s) => ({
      ...s,
      [currReviewVideo]: { annot_label: newLabel, annot_comments: comments ?? '' }
    }));

    addAnnot(newLabel, comments ?? '', username);
  }

  function prevVideo() {
    if (currReviewVideo > 0) {
      currReviewVideo--;
      updateUrlForCurrentVideo();
      resetClip();
    }
  }

  function nextVideo() {
    if (currReviewVideo < selectedVideoData.reviews.length - 1) {
      currReviewVideo++;
      updateUrlForCurrentVideo();
      resetClip();
      videoEl?.play();
    } else {
      goto(`/summary/${batch}/${word}`);
    }
  }

  function resetClip() {
    clipStart = 0;
    clipEnd = 0;
    try {
      videoEl?.load();
    } catch (e) {}
  }

  const refPlayPause = () => (referenceVideoPaused = !referenceVideoPaused);
  const refToggleLoop = () => (referenceVideoLooped = !referenceVideoLooped);
  const refSlowDown = () => (refPlaybackRate = Math.max(0.25, refPlaybackRate - 0.25));
  const refSpeedUp = () => (refPlaybackRate = Math.min(2, refPlaybackRate + 0.25));
  const toggleRefVisibility = () => (refVisible = !refVisible);

  function updateUrlForCurrentVideo() {
    const video = selectedVideoData.reviews[currReviewVideo];
    goto(`/annotation/${batch}/${word}?video=${video}`, {
      replaceState: true,
      keepFocus: true,
      noScroll: true
    });
  }

  $: total = selectedVideoData?.reviews?.length ?? 0;
  $: completed = Object.values($userAnnot).filter(
    (v) => v && typeof v.annot_label === 'string' && v.annot_label.trim() !== ''
  ).length;
  $: percent = total ? Math.round((completed / total) * 100) : 0;
</script>

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
        <button on:click={() => goto(`/summary/${batch}/${word}`)} class="visibility-button" style="margin-left: 8px;">
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
          <div class="flex flex-col h-full overflow-hidden">
            <div class="flex-1 overflow-hidden">
              <video
                id="review-video"
                class="w-full h-full object-contain"
                bind:this={videoEl}
                src={toFlask(selectedVideoData.reviews[currReviewVideo])}
                loop={reviewVideoLooped}
                autoplay
                on:timeupdate={onTimeUpdate}
                bind:paused={reviewVideoPaused}
                bind:playbackRate={revPlaybackRate}
              />
            </div>

            <!-- Clip controls: numeric fields + sliders always visible below video -->
            <div class="shrink-0 p-4 bg-gray-50 border-t border-gray-200">
              <div class="flex items-center gap-3 mb-3">
                <label class="text-sm font-medium whitespace-nowrap"
                  >Start:
                  <input
                    type="number"
                    min="0"
                    max={duration || 10}
                    step="0.1"
                    bind:value={clipStart}
                    class="ml-1 w-20 px-2 py-1 border border-gray-300 rounded"
                  />
                  <span class="ml-1">s</span>
                </label>
                <label class="text-sm font-medium whitespace-nowrap"
                  >End:
                  <input
                    type="number"
                    min="0"
                    max={duration || 10}
                    step="0.1"
                    bind:value={clipEnd}
                    class="ml-1 w-20 px-2 py-1 border border-gray-300 rounded"
                  />
                  <span class="ml-1">s</span>
                </label>
                <div class="text-sm font-medium ml-auto">
                  Duration: {duration ? duration.toFixed(1) + 's' : '—'}
                </div>
              </div>

              <!-- Dual-handle range slider -->
              <div class="relative w-full" style="height: 20px; padding: 10px 0;">
                <!-- background line -->
                <div
                  class="absolute w-full h-1 bg-gray-300 rounded"
                  style="top: 50%; transform: translateY(-50%);"
                ></div>

                <!-- active range line -->
                <div
                  class="absolute h-1 bg-blue-500 rounded pointer-events-none"
                  style="top: 50%; transform: translateY(-50%); 
                  left: {(clipStart / (duration || 10)) * 100}%; 
                  width: {((clipEnd - clipStart) / (duration || 10)) * 100}%;"
                ></div>

                <!-- End handle slider (bottom layer) -->
                <input
                  type="range"
                  min="0"
                  max={duration || 60}
                  step="0.01"
                  bind:value={clipEnd}
                  class="range-slider-end"
                  style="position: absolute; width: 100%; top: 0; z-index: 1;"
                />

                <!-- Start handle slider (top layer) -->
                <input
                  type="range"
                  min="0"
                  max={duration || 60}
                  step="0.01"
                  bind:value={clipStart}
                  class="range-slider-start"
                  style="position: absolute; width: 100%; top: 0; z-index: 2;"
                />
              </div>
            </div>
          </div>
        </Pane>
        {#if refVisible}
          <Pane>
            <Splitpanes horizontal={true}>
              <Pane minSize={15} maxSize={80}>
                <!-- Reference video -->
                <video
                  class="w-full h-full"
                  src={toFlask(selectedVideoData.reference)}
                  loop={referenceVideoLooped}
                  autoplay
                  bind:paused={referenceVideoPaused}
                  bind:playbackRate={refPlaybackRate}
                />
              </Pane>
              <Pane>
                <!-- Comment panel -->
                <div class="w-full h-full bg-aquamarine p-0">
                  <textarea
                    bind:value={comments}
                    on:blur={() => {
                      if (label) addAnnot(label, comments ?? '', username);
                    }}
                    on:keydown={(e) => {
                      if ((e.metaKey || e.ctrlKey) && e.key === 'Enter' && label) {
                        addAnnot(label, comments ?? '', username);
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
          <img id="playPauseIcon"
              class="w-5 h-5 md:w-6 md:h-6 lg:w-7 lg:h-7 xl:w-8 xl:h-8"
              src="{reviewVideoPaused ? '/play' : '/pause'}.svg"
              alt="paused icon">
        </button>

        <button on:click={revToggleLoop}
          class="bg-[#D9D9D9] hover:bg-[#A9A9A9] text-white rounded-md p-2 md:p-2 lg:p-2.5 xl:p-3 m-3 transition-colors"
          tabindex="-1">
          <img id="loopIcon"
              class="w-5 h-5 md:w-6 md:h-6 lg:w-7 lg:h-7 xl:w-8 xl:h-8"
              src="{reviewVideoLooped ? '/loop' : '/not-looped'}.svg"
              alt="play icon">
        </button>

        <div class="join m-3">
          <!-- Slow down video button-->
          <button on:click={revSlowDown}
            class="bg-[#D9D9D9] hover:bg-[#A9A9A9] text-white p-2 md:p-2 lg:p-2.5 xl:p-3 rounded-md join-item transition-colors"
            tabindex="-1">
            <img class="w-8 h-8 md:w-7.5 md:h-7.5 lg:w-8 lg:h-8 xl:w-9 xl:h-9"
                src="/slow-down-dark.svg"
                alt="turtle icon to indicate slow down">
          </button>

          <!-- Playback rate reporter -->
          <div
            class="bg-[#D9D9D9] flex text-black w-20 rounded-md p-2 md:p-2 lg:p-2.5 xl:p-3 join-item transition-colors"
          >
            <div class="flex items-center m-auto">{revPlaybackRate.toFixed(2)}&times;</div>
          </div>

          <!-- Speed up video button-->
          <button on:click={revSpeedUp}
            class="bg-[#D9D9D9] hover:bg-[#A9A9A9] text-white rounded-md p-2 md:p-2 lg:p-2.5 xl:p-3 join-item transition-colors"
            tabindex="-1">
            <img class="w-5 h-5 md:w-6 md:h-6 lg:w-7 lg:h-7 xl:w-8 xl:h-8"
                src="/speed-up-dark.svg"
                alt="bunny icon to indicate speed up">
          </button>
        </div>

        <!-- Previous video -->
        <div class="join m-3">
          <button on:click={prevVideo}
            class="bg-[#D9D9D9] hover:bg-[#A9A9A9] text-white rounded-md p-2 md:p-2 lg:p-2.5 xl:p-3 join-item transition-colors"
            tabindex="-1">
            <img class="w-5 h-5 md:w-6 md:h-6 lg:w-7 lg:h-7 xl:w-8 xl:h-8"
                src="/previous.svg"
                alt="previous video icon">
          </button>

          <!-- Next video -->
          <button on:click={nextVideo}
            class="bg-[#D9D9D9] hover:bg-[#A9A9A9] text-white rounded-md p-2 md:p-2 lg:p-2.5 xl:p-3 join-item transition-colors"
            tabindex="-1">
            <img class="w-5 h-5 md:w-6 md:h-6 lg:w-7 lg:h-7 xl:w-8 xl:h-8"
                src="/next.svg"
                alt="next video icon">
          </button>
        </div>
      </div>

      <!-- Annotation labeling -->
      <div class="w-1/3 h-20 flex items-center justify-start">
        <!-- Good button -->
        <button on:click={() => setLabel('Good')}
          class="bg-[#D9D9D9] hover:bg-[#A9A9A9] text-white rounded-md p-2 md:p-2 lg:p-2.5 xl:p-3 m-3 transition-colors"
          tabindex="-1">
          <img id="good-button"
              class="w-5 h-5 md:w-6 md:h-6 lg:w-7 lg:h-7 xl:w-8 xl:h-8"
              src="/thumbs-up.svg"
              alt="thumbs up icon">
        </button>

        <!-- Variant button -->
        <button on:click={() => setLabel('Variant')}
          class="bg-[#D9D9D9] hover:bg-[#A9A9A9] text-white rounded-md p-2 md:p-2 lg:p-2.5 xl:p-3 m-3 transition-colors"
          tabindex="-1">
          <img id="variant-button"
              class="w-5 h-5 md:w-6 md:h-6 lg:w-7 lg:h-7 xl:w-8 xl:h-8"
              src="/variant.svg"
              alt="icon">
        </button>

        <!-- Bad button -->
        <button on:click={() => setLabel('Bad')}
          class="bg-[#D9D9D9] hover:bg-[#A9A9A9] text-white rounded-md p-2 md:p-2 lg:p-2.5 xl:p-3 m-3 transition-colors"
          tabindex="-1">
          <img id="bad-button"
              class="w-5 h-5 md:w-6 md:h-6 lg:w-7 lg:h-7 xl:w-8 xl:h-8"
              src="/thumbs-down.svg"
              alt="thumbs down icon">
        </button>

        <!-- Further Review button -->
        <button on:click={() => setLabel('Further Review')}
          class="bg-[#D9D9D9] hover:bg-[#A9A9A9] text-white rounded-md p-2 md:p-2 lg:p-2.5 xl:p-3 m-3 transition-colors"
          tabindex="-1">
          <img id="further-review-button" 
              class="w-5 h-5 md:w-6 md:h-6 lg:w-7 lg:h-7 xl:w-8 xl:h-8"
              src="/archive.svg"
              alt="archive icon">
        </button>

        <!-- Label -->
        <div class="flex w-100px ml-3 min-w-[3rem] md:min-w-[6rem] lg:min-w-[8rem] h-20">
          <div
            class="flex items-center gap-2 p-2 md:p-2 lg:p-2.5 xl:p-3 m-3 rounded-md transition-colors whitespace-nowrap"
            class:bg-green-200={label === 'Good'}
            class:bg-yellow-200={label === 'Variant'}
            class:bg-red-200={label === 'Bad'}
            class:bg-blue-200={label === 'Further Review'}
            class:bg-[#D9D9D9]={!label}
          >
            {#if label}
              {#if label === 'Good'}
                <img src="/thumbs-up.svg" class="w-6 h-6" alt="thumbs up icon" />
              {:else if label === 'Variant'}
                <img src="/variant.svg" class="w-6 h-6" alt="variant icon" />
              {:else if label === 'Bad'}
                <img src="/thumbs-down.svg" class="w-6 h-6" alt="thumbs down icon" />
              {:else if label === 'Further Review'}
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
              src="{referenceVideoPaused ? '/play' : '/pause'}.svg" 
              alt="paused icon">
        </button>

        <button on:click={refToggleLoop}
          class="bg-[#D9D9D9] hover:bg-[#A9A9A9] text-white rounded-md p-2 md:p-2 lg:p-2.5 xl:p-3 m-3 transition-colors"
          tabindex="-1">
          <img id="loopIcon" class="w-5 h-5 md:w-6 md:h-6 lg:w-7 lg:h-7 xl:w-8 xl:h-8" 
              src="{referenceVideoLooped ? '/loop' : '/not-looped'}.svg" 
              alt="play icon">
        </button>

        <div class="join m-3">
          <!-- Slow down video button-->
          <button on:click={refSlowDown} 
            class="bg-[#D9D9D9] hover:bg-[#A9A9A9] text-white p-2 md:p-2 lg:p-2.5 xl:p-3 rounded-md join-item transition-colors" 
            tabindex="-1">
            <img class="w-8 h-8 md:w-7.5 md:h-7.5 lg:w-8 lg:h-8 xl:w-9 xl:h-9" 
                src="/slow-down-dark.svg" 
                alt="turtle icon to indicate slow down">
          </button>

          <!-- Playback rate reporter -->
          <div class="bg-[#D9D9D9] flex text-black w-20 rounded-md p-2 md:p-2 lg:p-2.5 xl:p-3 join-item transition-colors">
            <div class="flex items-center m-auto">{refPlaybackRate.toFixed(2)}&times;</div>
          </div>

          <!-- Speed up video button-->
          <button on:click={refSpeedUp}
            class="bg-[#D9D9D9] hover:bg-[#A9A9A9] text-white rounded-md p-2 md:p-2 lg:p-2.5 xl:p-3 join-item transition-colors"
            tabindex="-1">
            <img class="w-5 h-5 md:w-6 md:h-6 lg:w-7 lg:h-7 xl:w-8 xl:h-8" 
                src="/speed-up-dark.svg" 
                alt="bunny icon to indicate speed up">
          </button>
        </div>
      </div>
    </div>
  </div>
{:else}
  <p>No video data available for the word "{word}".</p>
{/if}

<style>
  .visibility-button {
    background: #3b82f6;
    color: white;
    border: none;
    padding: 6px 12px;
    border-radius: 6px;
    cursor: pointer;
  }

  .visibility-button:hover {
    background: #2563eb;
  }

  /* Custom range slider styling */
  .range-slider-start,
  .range-slider-end {
    -webkit-appearance: none;
    appearance: none;
    background: transparent;
    outline: none;
    height: 20px;
    margin: 0;
    padding: 0;
    pointer-events: none;
  }

  /* Webkit (Chrome, Safari) track styling - make invisible */
  .range-slider-start::-webkit-slider-runnable-track,
  .range-slider-end::-webkit-slider-runnable-track {
    background: transparent;
    height: 0;
    border: none;
  }

  /* Webkit (Chrome, Safari) thumb styling */
  .range-slider-start::-webkit-slider-thumb,
  .range-slider-end::-webkit-slider-thumb {
    -webkit-appearance: none;
    appearance: none;
    width: 20px;
    height: 20px;
    border-radius: 50%;
    background: #3b82f6;
    cursor: grab;
    border: 3px solid white;
    box-shadow: 0 2px 6px rgba(0, 0, 0, 0.3);
    margin-top: -10px;
    pointer-events: auto;
  }

  .range-slider-start::-webkit-slider-thumb:hover,
  .range-slider-end::-webkit-slider-thumb:hover {
    background: #2563eb;
  }

  .range-slider-start::-webkit-slider-thumb:active,
  .range-slider-end::-webkit-slider-thumb:active {
    background: #1d4ed8;
    cursor: grabbing;
  }

  /* Firefox track styling - make invisible */
  .range-slider-start::-moz-range-track,
  .range-slider-end::-moz-range-track {
    background: transparent;
    height: 0;
    border: none;
  }

  /* Firefox thumb styling */
  .range-slider-start::-moz-range-thumb,
  .range-slider-end::-moz-range-thumb {
    width: 20px;
    height: 20px;
    border-radius: 50%;
    background: #3b82f6;
    cursor: grab;
    border: 3px solid white;
    box-shadow: 0 2px 6px rgba(0, 0, 0, 0.3);
    pointer-events: auto;
  }

  .range-slider-start::-moz-range-thumb:hover,
  .range-slider-end::-moz-range-thumb:hover {
    background: #2563eb;
  }

  .range-slider-start::-moz-range-thumb:active,
  .range-slider-end::-moz-range-thumb:active {
    background: #1d4ed8;
    cursor: grabbing;
  }
</style>
