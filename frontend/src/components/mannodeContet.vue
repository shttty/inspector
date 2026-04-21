<template>

    <n-space v-for="process in processList" justify="space-between">
      <el-link @click="download(`${process.groupname}${process.processname}`)" :underline="false"
        :type="statusShow(process.state)" style="font-size: 18px;"><n-ellipsis style="width: 200px;">{{
          process.groupname
          }}{{ process.processname }}</n-ellipsis></el-link>
      <div style="text-align: center;">
        <el-text type="info">{{ process.statename }}</el-text>
        <br>
        <n-ellipsis style="width: 120px;position: relative;top: -10px;">
          <el-text type="info" style="font-size: 10px ">{{ process.time }}</el-text>
        </n-ellipsis>
      </div>
      <div>
        <n-button v-if="process.state != 20 && process.state != 10"
          @click="() => { commitStart = true; processTOstart = `${process.groupname}${process.processname}` }"
          type="primary" quaternary size="large">启动</n-button>
        <n-button v-if="process.state === 20 || process.state === 10"
          @click="() => { commitStop = true; processTOsop = `${process.groupname}${process.processname}` }" type="error"
          quaternary size="large">停止</n-button>
      </div>
      <n-button @click="getLog(`${process.groupname}${process.processname}`)">Log</n-button>
    </n-space>

  <n-modal v-model:show="commitStart" preset="dialog" title="确认启动" content="是否确认启动该程序？" positive-text="确认"
    negative-text="取消" @positive-click="startProcess(serverName, processTOstart)"
    @negative-click="commitStart = false"></n-modal>
  <n-modal v-model:show="commitStop" preset="dialog" title="确认停止" content="是否确认停止该程序？" positive-text="确认"
    negative-text="取消" @positive-click="stopProcess(serverName, processTOsop)" />
  <n-modal v-model:show="waiting">
    <n-card style="width: 200px; text-align: center;">
      <n-spin v-model:show="waiting"></n-spin>
      <br>
      <el-text>正在尝试</el-text>
    </n-card>
  </n-modal>
  <n-modal v-model:show="operationComplete">
    <n-card style="width: 200px; text-align: center;">
      <n-result v-if="operationSuccess" status="success" title="操作成功">
      </n-result>
      <n-result v-if="!operationSuccess" status="error" title="操作失败">
      </n-result>
    </n-card>
  </n-modal>
  <n-modal v-model:show="showLog" :mask-closable="false">
    <n-card :title="logTitle" style="width: 700px">
      <template #header-extra>
        <n-button @click="freshLog()">刷新</n-button>
      </template>
      <n-scrollbar x-scrollable style="max-height: 600px">
        <pre>{{ logContent }}</pre>
      </n-scrollbar>
      <template #action>
        <n-button @click="showLog = false">关闭</n-button>
      </template>
    </n-card>
  </n-modal>
</template>

<style scoped>
.el-text {
  font-size: 18px;
}
</style>

<script setup lang="ts">
import { onMounted, ref } from 'vue'
const props = defineProps({
  server_name: String,
  url: String
})


const processList = ref<{ time: string; processname: string; groupname: string | undefined; state: number; statename: string }[]>([]);
const serverName = ref(props.server_name)
const commitStart = ref<boolean>(false)
const commitStop = ref<boolean>(false)
const waiting = ref(false)
const operationComplete = ref(false)
const operationSuccess = ref(false)
const processTOstart = ref("")
const processTOsop = ref("")
const showLog = ref(false)
const logContent = ref("")
const logTitle = ref("")


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
  const res = await fetch(`${props.url}/processListInServerOwn?servername=${props.server_name}`)
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
      return 'warning'
    }
  } else {
    return 'danger'
  }
}

async function startProcess(serverName: string | undefined, processname: string) {
  waiting.value = true
  commitStart.value = false
  try {
    const res = await fetch(`${props.url}/start?servername=${serverName}&processname=${processname}`)
    const data = await res.json()
    console.log(data.status)
    if (data.flag == true) {
      waiting.value = false
      operationComplete.value = true
      operationSuccess.value = true
      processList.value = []
      getProcessList()
    } else {
      waiting.value = false
      operationComplete.value = true
      operationSuccess.value = false
    }
  } catch (error) {
    waiting.value = false
    operationComplete.value = true
    operationSuccess.value = false
    console.error('Error:', error)
  }
}

async function stopProcess(serverName: string | undefined, processname: string) {
  waiting.value = true
  commitStop.value = false
  try {
    const res = await fetch(`${props.url}/stop?servername=${serverName}&processname=${processname}`)
    const data = await res.json()
    console.log(data.status)
    if (data.flag == true) {
      waiting.value = false
      operationComplete.value = true
      operationSuccess.value = true
      processList.value = []
      getProcessList()
    } else {
      waiting.value = false
      operationComplete.value = true
      operationSuccess.value = false
    }
  } catch (error) {
    waiting.value = false
    operationComplete.value = true
    operationSuccess.value = false
    console.error('Error:', error)
  }
}

async function getLog(processname: string) {
  const res = await fetch(`${props.url}/log?servername=${props.server_name}&processname=${processname}`)
  const data = await res.json()
  logContent.value = data.text
  logTitle.value = processname
  showLog.value = true
}

async function freshLog() {
  const res = await fetch(`${props.url}/log?servername=${props.server_name}&processname=${logTitle.value}`)
  const data = await res.json()
  logContent.value = data.text
}

async function download(processname: string) {
  let windowFeatures = "width=800,height=600,location=no,menubar=no,toolbar=no,scrollbars=yes,status=no";
  window.open(`/tree?server=${props.server_name}&process=${processname}`, "_blank", windowFeatures);
}

onMounted(() => {
  getProcessList()
})
</script>