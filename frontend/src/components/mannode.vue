<template>
  <n-card :title="props.server_name" hoverable>
    <template #header-extra v-if="overview">
      <n-button text size="large" @click="showmore = !showmore" color="#606266">
        展开
      </n-button>
    </template>
    <n-scrollbar style="height: 200px;">
      <mannodeContet :server_name="props.server_name" :url="props.url"/>
    </n-scrollbar>
  </n-card>
  <n-modal preset="card" v-model:show="showmore" style="width: 60%; min-width: 443px;">
    <n-scrollbar style="max-height: 600px;">
      <mannodeContetLarge :server_name="props.server_name" :url="props.url"/>
    </n-scrollbar>
  </n-modal>
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

@media (max-width: 1284px) {
  .n-card {
    width: calc((100vw - 320px));
  }
}

@media (max-width: 800px) {
  .n-card {
    width: 500px;
  }
}


</style>
<script lang="ts" setup>
import { ref } from 'vue'
import mannodeContet from './mannodeContet.vue'
import mannodeContetLarge from './mannodeContetLarge.vue'

const props = defineProps({
  server_name: String,
  url: String,
  overview: Boolean
})
const showmore = ref(false)
const overview = ref(props.overview)

</script>