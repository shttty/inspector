<template>
  <n-spin :show=getDataLoading>
 <n-spin :show=downloadLoading>
  <n-button @click="getData()">
    刷新
  </n-button>
  <n-tree
    block-line
    :data="tree"
    default-expand-all
  />
  </n-spin></n-spin>
  <template v-if="downloadLoading">正在传输至"/mnt/Public/operation/tmp/{{ user }}"</template>
  <template v-if="getDataLoading">正在加载目录</template>
</template>

<script lang="ts" setup>
import { ref, h, onMounted } from 'vue'
import { NButton, NSpin, type TreeOption } from 'naive-ui'
import type { Key } from 'naive-ui/es/cascader/src/interface';
import Cookies from 'js-cookie';

const tree = ref<TreeOption[]>([])
const getDataLoading = ref(false)
const downloadLoading = ref(false)
const user = Cookies.get('userName')

const url = '/api'

async function getData() {
  const urlParams = new URLSearchParams(window.location.search);
  const progress = urlParams.get('process');
  const server = urlParams.get('hostName');
  getDataLoading.value = true
  await fetch(`${url}/tree?progress=${progress}&server=${server}`)
  .then(res=> res.json())
  .then((data) => {
    if (!Array.isArray(data)) {
    // 如果data不是一个数组，则将其转换为一个数组
    data = [data];
  }
    tree.value = addElement(data)
    console.log(data)
  }).then(() => {
    getDataLoading.value = false
  })
}

async function download( key: Key | undefined) {
  const urlParams = new URLSearchParams(window.location.search);
  const server = urlParams.get('hostName');
  console.log(downloadLoading.value)
  downloadLoading.value = true
  fetch(`${url}/download`, {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    path: key,
    server: server
  })})
  .then(response => response.json())
  .then(data => {
    console.log(data);
  }).then(() => {
    downloadLoading.value = false
    console.log(downloadLoading.value)
  })
  .catch(error => {
    console.error(error);
  });
}

function addElement(data: TreeOption[] | undefined ): TreeOption[] {
  if (!data) {
    return []
  }
  for (let i = 0; i < data.length; i++) {
    data[i].suffix = () =>
        h(
          NButton,
          { text: true, type: 'primary', onClick: ()=>{download(data[i].key)}, },
          { default: () => '下载' }
        )
    if (data[i].children) {
      data[i].children = addElement(data[i].children)
    }
  }
  return data
}
onMounted(() => {
  getData()
})

</script>



