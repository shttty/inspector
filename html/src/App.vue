<template>
  <el-container class="layout-container-demo" style="height: 100%">
    <el-header>
      <n-space justify="space-between">
        <div></div>
        <h1 style="margin: 0; padding-top: 10px;">进程管理中心</h1>
        <div style="padding-top: 10px;" @click="logout"><n-button>退出</n-button></div>
      </n-space>
    </el-header>
    <el-container>
      <el-aside width="200px">
        <h1 style="text-align: center;">服务器列表</h1>
        <div>
          <n-scrollbar max-height="600px">
            <el-row v-for="server in serverListOK" :key="server.id" justify="center"><el-link :underline="false"
                type="primary">{{ server.hostName }}</el-link></el-row>
            <el-row v-for="server in serverListNO" :key="server.id" justify="center"><el-link :underline="false"
                type="danger" disabled>{{ server.hostName }}</el-link></el-row>
          </n-scrollbar>
        </div>
      </el-aside>
      <el-container>
        <el-main v-loading="loadFlag" element-loading-text="加载中" style="width: 100%">
          <div style="padding: 20px">
            <n-space>
              <n-card v-for="server in serverListOK" :key="server.id" class="box-card" hoverable>
                  <div class="card-header">
                    <el-text class="mx-1" style="font-size: 24px">{{ server.hostName }}</el-text>
                  </div>
                  <n-divider />
                <n-scrollbar style="max-height: 170px; width: 100%;" trigger="none" x-scrollable>
                  <div v-for="runningProcess in processListRunning" :key="runningProcess.id">
                    <el-row v-if="runningProcess.hostName == server.hostName">
                      <el-col :span="8"><el-text type="success">{{ runningProcess.processName
                      }}</el-text> </el-col>
                      <el-col :span="6"> <el-text type="info">{{ runningProcess.processState
                      }}</el-text> <br><span style="font-size: 10px; color: grey;">{{ runningProcess.uptime }}</span></el-col>
                      <el-col :span="6"><el-button size="small" type='danger' text='danger' style="font-size: 18px"
                          @click="stopClick(runningProcess)">stop</el-button></el-col>
                      <el-col :span="3"><el-button type='info' text='info' size="small" style="font-size: 18px"
                          @click="logClick(runningProcess)">log</el-button></el-col>
                          <n-modal v-model:show="runningProcess.showLog" :mask-closable="false" class="custom-card"
                        preset="card" size="huge" title="日志" :bordered="false" :style="{ width: '600px' }">
                        <template #header-extra>
                          <h2>{{ runningProcess.processName }}</h2>
                        </template>
                        <n-scrollbar style="max-height: 500px" trigger="none" x-scrollable>
                            <pre>{{ runningProcess.log }}</pre>
                        </n-scrollbar>
                        <template #footer>
                          <n-space justify="end">
                            <n-button strong secondary type="success" @click="logClick(runningProcess)">
                              刷新
                            </n-button>
                            </n-space>
                        </template>
                      </n-modal>
                    </el-row>
                  </div>
                  <div v-for="startingProcess in processListStarting" :key="startingProcess.id">
                    <el-row v-if="startingProcess.hostName == server.hostName">
                      <el-col :span="8"><el-text type="warning">{{ startingProcess.processName
                      }}</el-text></el-col>
                      <el-col :span="6"> <el-text type="info">{{ startingProcess.processState
                      }}</el-text> <br><el-text type="info" style="font-size: 10px;">{{ startingProcess.starttime }}</el-text></el-col>
                      <el-col :span="6"><el-button size="small" type='danger' text='danger' style="font-size: 18px"
                          @click="stopClick(startingProcess)">stop</el-button></el-col>
                      <el-col :span="3"><el-button type='info' text='info' size="small" style="font-size: 18px"
                          @click="logClick(startingProcess)">log</el-button></el-col>
                          <n-modal v-model:show="startingProcess.showLog" :mask-closable="false" class="custom-card"
                        preset="card" size="huge" title="日志" :bordered="false" :style="{ width: '600px' }">
                        <template #header-extra>
                          <h2>{{ startingProcess.processName }}</h2>
                        </template>
                        <n-scrollbar style="max-height: 500px" trigger="none" x-scrollable>
                            <pre>{{ startingProcess.log }}</pre>
                        </n-scrollbar>
                        <template #footer>
                          <n-space justify="end">
                            <n-button strong secondary type="success" @click="logClick(startingProcess)">
                              刷新
                            </n-button>
                          </n-space>
                        </template>
                      </n-modal>
                    </el-row>
                  </div>
                  <div v-for="stoppedProcess in processListStopped" :key="stoppedProcess.id">
                    <el-row v-if="stoppedProcess.hostName == server.hostName">
                      <el-col :span="8"><el-text type="danger">{{ stoppedProcess.processName
                      }}</el-text></el-col>
                      <el-col :span="6"> <el-text type="info">{{ stoppedProcess.processState
                      }}</el-text><br><el-text type="info" style="font-size: 10px;">{{stoppedProcess.stoptime }}</el-text> </el-col>
                      <el-col :span="6"><el-button type='primary' text='primary' size="small" style="font-size: 18px"
                          @click="startClick(stoppedProcess)">start</el-button></el-col>
                      <el-col :span="3"><el-button type='info' text='info' size="small" style="font-size: 18px"
                          @click="logClick(stoppedProcess)">log</el-button></el-col>
                      <n-modal v-model:show="stoppedProcess.showLog" :mask-closable="false" class="custom-card"
                        preset="card" size="huge" title="日志" :bordered="false" :style="{ width: '600px' }">
                        <template #header-extra>
                          <h2>{{ stoppedProcess.processName }}</h2>
                        </template>
                        <n-scrollbar style="max-height: 500px" trigger="none" x-scrollable>
                            <pre>{{ stoppedProcess.log }}</pre>
                        </n-scrollbar>
                        <template #footer>
                          <n-space justify="end">
                            <n-button strong secondary type="success" @click="logClick(stoppedProcess)">
                              刷新
                            </n-button>
                          </n-space>
                        </template>
                      </n-modal>
                    </el-row>
                  </div>
                </n-scrollbar>
              </n-card>
            </n-space>
          </div>
        </el-main>
      </el-container>
    </el-container>
  </el-container>
</template>

<style scoped>
.box-card {
  width: 550px;
  height: 300px;
}

.layout-container-demo .el-header {
  position: relative;
  background-color: var(--el-color-primary-light-3);
  color: var(--el-text-color-primary);
}

.layout-container-demo .el-aside {
  color: var(--el-text-color-primary);
  background: var(--el-color-primary-light-8);
}

.layout-container-demo .el-main {
  padding: 0;
}

.el-link {
  font-size: 18px;
}
.el-text {
  font-size: 18px;
}

.el-link .el-icon--right.el-icon {
  vertical-align: text-bottom;
}

.el-row {
  margin: 10px;
}

.el-row:last-child {
  margin-bottom: 0;
}
</style>
<script lang="ts" setup >

import { ref, onMounted } from 'vue';
import Cookies from 'js-cookie';

const url = `/api`;
interface ServerList {
  AllNodes: any;
  ConnecctSucceed: string[];
  ConnectFailled: string[];
}


interface logText {
  text: string;
}

interface process {
  name: string;
  group: string;
  start: number;
  stop: number;
  now: number;
  state: number;
  statename: string;
  spawnerr: string;
  exitstatus: number;
  logfile: string;
  stdout_logfile: string;
  stderr_logfile: string;
  pid: number;
  description: string;
}
interface Servers {
  [key: string]: process[];
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

const serverListOK = ref<{ id: number; hostName: string }[]>([]);
const serverListNO = ref<{ id: number; hostName: string }[]>([]);
const processListRunning = ref<{ id: number; hostName: string; uptime: string; processName: string; processState: string; showLog: boolean; log: string }[]>([]);
const processListStarting = ref<{ id: number; hostName: string; starttime: string; processName: string; processState: string; showLog: boolean; log: string }[]>([]);
const processListStopped = ref<{ id: number; hostName: string; stoptime: string; processName: string; processState: string; showLog: boolean; log: string }[]>([]);
const loadFlag = ref(true);

const startClick = async (item: { hostName: string, processName: string }) => {
  const url2 = `${url}/start?servername=${item.hostName}&processname=${item.processName}`;
  try {
    await Promise.all([
      fetch(url2),
      setTimeout(() => load(), 100),
    ]);
    setTimeout(() => load(), 100)
  } catch (error) {
    console.error(error);
  }
};

const stopClick =  (item: { hostName: string, processName: string }) => {
  const url2 = `${url}/stop?servername=${item.hostName}&processname=${item.processName}`;
  fetch(url2)
  setTimeout(() => load(), 100)
  console.log("ok")
};

const logClick = async (item: { hostName: string, processName: string, showLog: boolean, log: string }) => {
  const url2 = `${url}/log?servername=${item.hostName}&processname=${item.processName}`;
  await fetch(url2)
    .then((response) => response.json())
    .then((data: logText) => {
      item.log = data.text;
      console.log(data);
      console.log(item.log);
      item.showLog = true;
    })
};

async function getServerList() {
  await fetch(`${url}/serverList`)
    .then(response => response.json())
    .then((data: ServerList) => {
      let id = 0;
      for (let i of data.ConnecctSucceed) {
        serverListOK.value.push({ id: id++, hostName: i });
      }
      let idf = 0;
      for (let i of data.ConnectFailled) {
        serverListNO.value.push({ id: idf++, hostName: i });
      }
    })
    .catch(error => {
      console.error('Error:', error);
    });
}

async function getProcessList() {
  await fetch(`${url}/processList/all/`)
    .then(response => response.json())
    .then((data: Servers) => {
      let id = 0;
      const serverNames = Object.keys(data);
      for (let i in serverNames) {
        for (let a in data[serverNames[i]]) {
          if (data[serverNames[i]][a].name !=  data[serverNames[i]][a].group) {
            data[serverNames[i]][a].name = `${data[serverNames[i]][a].group}:${data[serverNames[i]][a].name}`             
          }
          if (data[serverNames[i]][a].state == 20) {
            processListRunning.value.push({ id: id++, hostName: serverNames[i], uptime: convertTime(data[serverNames[i]][a].start), processName: data[serverNames[i]][a].name, processState: data[serverNames[i]][a].statename, showLog: false, log: " " });
            console.log(a)
          }
          else if (data[serverNames[i]][a].state == 10) {
            processListStarting.value.push({ id: id++, hostName: serverNames[i], starttime: convertTime(data[serverNames[i]][a].start), processName: data[serverNames[i]][a].name, processState: data[serverNames[i]][a].statename, showLog: false, log: " " });
          } else {
            processListStopped.value.push({ id: id++, hostName: serverNames[i], stoptime: convertTime(data[serverNames[i]][a].stop), processName: data[serverNames[i]][a].name, processState: data[serverNames[i]][a].statename, showLog: false, log: " " });
          }
        }
      }
    })
    .catch(error => {
      console.error('Error:', error);
    });
}

async function load() {
  processListRunning.value = [];
  processListStarting.value = [];
  processListStopped.value = [];
  serverListNO.value = [];
  serverListOK.value = [];
  loadFlag.value = false
  await getServerList()
  await getProcessList()
}

function logout() {
  Cookies.remove('userToken');
  Cookies.remove('userName');
  location.reload();
}

onMounted(() => {
  load()
});
</script>
