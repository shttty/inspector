<template>
  <n-card :title="props.server_name" hoverable>
    <n-scrollbar style="height: 200px;">
      <nodeInfo :server_name="props.server_name" :url="props.url"/>
    </n-scrollbar>
  </n-card>
</template>

<style scoped>
.n-card {
  width: calc((100vw - 344px)/3);
}


@media (max-width: 1694px) {
  .n-card {
    width: calc((100vw - 332px)/2);
  }
}

@media (max-width: 1253px) {
  .n-card {
    width: calc((100vw - 320px));
  }
}

@media (max-width: 800px) {
  .n-card {
    width: 480px;
  }
}

</style>
<script lang="ts" setup>

import nodeInfo from './nodeInfo.vue';

const props = defineProps({
  server_name: String,
  url: String,
})

</script>