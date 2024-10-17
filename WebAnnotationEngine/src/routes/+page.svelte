<script>
  import { Pane, Splitpanes } from 'svelte-splitpanes';
</script>

<!-- Video viewer -->
<div class="h-full w-full">
    <!-- See svelte-splitpanes https://orefalo.github.io/svelte-splitpanes/ -->
    <Splitpanes class="p-4" style="height: 100%">
      <Pane class="rounded-xl" minSize={20}>
        <!-- Video to review -->
        <video class="w-full h-full" src="ReviewVideos/all_work_and_no_play_rh_wire.mp4"
            controls
            loop />
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
<div class="w-full h-20">

</div>
