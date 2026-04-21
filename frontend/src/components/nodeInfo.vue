<template>
  <n-space v-for="process in processList" justify="space-between">
    <n-ellipsis style="width: 200px">
      <el-text :type=statusShow(process.state)> {{ process.groupname }}{{ process.processname }}</el-text>
    </n-ellipsis>
    <div style="text-align: center;">
      <el-text type="info">{{ process.statename }}</el-text>
      <br>
      <n-ellipsis style="width: 120px;position: relative;top: -10px;">
        <el-text type="info" style="font-size: 10px ">{{ process.time }}</el-text>
      </n-ellipsis>
    </div>
    <n-button @click="details(process.processname)" quaternary size="large">详情</n-button>
  </n-space>
  <n-modal v-model:show="showdetails" preset="card" :title="alertname" size="huge" style="width: 600px;">
      <p>负责人：{{ supportor }}</p>
      <p>启停时间：{{ bootTime }}</p>
      <pre>{{ detaildata }}</pre>
    </n-modal>
</template>

<style scoped>
.el-text {
  font-size: 18px;
}
</style>

<script lang="ts" setup>
import { onMounted, ref } from 'vue'

const props = defineProps({
  server_name: String,
  url: String,
})

const processList = ref<{ time: string; processname: string; groupname: string; state: number; statename: string }[]>([]);
const showdetails = ref(false)
const detaildata = ref('')
const alertname = ref('')
const supportor = ref('')
const bootTime = ref('')

async function details(processname: string) {
  const res = await fetch(`${props.url}/details?servername=${props.server_name}&processname=${processname}`)
  const data = await res.json()
  alertname.value = data.alterName
  supportor.value = data.supportor
  bootTime.value = data.time
  detaildata.value = data.description
  showdetails.value = true
}

function convertTime(unixTimestamp: number): string {
  if (unixTimestamp === 0) {
    return " ";
  }

  const date = new Date(unixTimestamp * 1000);
  const year = date.getFullYear();
  const month = ('' + (date.getMonth() + 1)).padStart(2, '0');
  const day = ('' + date.getDate()).padStart(2, '0');
  const hours = ('' + date.getHours()).padStart(2, '0');
  const minutes = ('' + date.getMinutes()).padStart(2, '0');
  const seconds = ('' + date.getSeconds()).padStart(2, '0');

  return `${year}-${month}-${day} ${hours}:${minutes}:${seconds}`;
}

async function getProcessList() {
  const res = await fetch(`${props.url}/processList?servername=${props.server_name}`)
  const data = await res.json()
  let timestamp = ""
  for (let i in data) {
    if (data[i].start > data[i].stop) {
      timestamp = convertTime(data[i].start)
    } else {
      timestamp = convertTime(data[i].stop)
    }
    if (data[i].group === data[i].name) {
      processList.value.push({
        groupname: ``,
        processname: `${data[i].name}`,
        time: timestamp,
        statename: data[i].statename,
        state: data[i].state
      })
    } else {
      processList.value.push({
        groupname: `${data[i].group}:`,
        processname: `${data[i].name}`,
        time: timestamp,
        statename: data[i].statename,
        state: data[i].state
      })
    }
  }
}

function statusShow(state: number) {
  if (state == 20) {
    return 'success'
  } else if (state == 10) {
    {
      return 'Warning'
    }
  } else {
    return 'danger'
  }
}
onMounted(() => {
  getProcessList()
})
</script>
