<template>
  <el-container class="layout-container-demo" style="height: 100%">
    <el-header style="text-align: center; font-size: 12px">
      <h1>进程管理中心</h1>
    </el-header>
    <el-container>
      <el-aside width="200px">
        <h1 style="text-align: center;">服务器列表</h1>
        <div>
          <el-scrollbar max-height="600px">
            <el-row v-for="server in serverListOK" :key="server.id" justify="center"><el-link :underline="false"
                type="primary">{{ server.hostName }}</el-link></el-row>
            <el-row v-for="server in serverListNO" :key="server.id" justify="center"><el-link :underline="false"
                type="danger" disabled>{{ server.hostName }}</el-link></el-row>
          </el-scrollbar>
        </div>
      </el-aside>
      <el-container>
        <el-main>
          <div style="padding: 20px">
            <el-space wrap>
              <el-card v-for="server in serverListOK" :key="server.id" class="box-card" shadow="hover">
                <template #header>
                  <div class="card-header">
                    <el-text class="mx-1" style="font-size: 24px">{{ server.hostName }}</el-text>
                  </div>
                </template>
                <el-scrollbar>
                  <div v-for="runningProcess in processListRunning" :key="runningProcess.id">
                    <el-row v-if="runningProcess.hostName == server.hostName">
                      <el-col :span="8"><el-link :underline="false" type="success">{{ runningProcess.processName
                      }}</el-link> </el-col>
                      <el-col :span="6"> <span style="font-size: 16px; color: grey;">{{ runningProcess.processState
                      }}<br>{{ runningProcess.uptime }}</span> </el-col>
                      <el-col :span="6"><el-button  size="small" type='danger' text='danger' style="font-size: 18px" @click="stopClick(runningProcess)">stop</el-button></el-col>
                      <el-col :span="3"><el-link
                          :href="'http://localhost:5000/log?servername=' + encodeURIComponent(runningProcess.hostName) + '&processname=' + encodeURIComponent(runningProcess.processName)"
                          target="_blank" type="info" style="font-size: 18px">log</el-link></el-col>
                    </el-row>
                  </div>
                  <div v-for="startingProcess in processListStarting" :key="startingProcess.id">
                    <el-row v-if="startingProcess.hostName == server.hostName">
                      <el-col :span="8"><el-link :underline="false" type="warning">{{ startingProcess.processName
                      }}</el-link> </el-col>
                      <el-col :span="6"> <span style="font-size: 16px; color: grey;">{{ startingProcess.processState
                      }}<br>{{ startingProcess.starttime }}</span> </el-col>
                      <el-col :span="6"><el-button  size="small" type='danger' text='danger' style="font-size: 18px" @click="stopClick(startingProcess)">stop</el-button></el-col>
                      <el-col :span="3"><el-link
                          :href="'http://localhost:5000/log?servername=' + encodeURIComponent(startingProcess.hostName) + '&processname=' + encodeURIComponent(startingProcess.processName)"
                          target="_blank" type="info" style="font-size: 18px">log</el-link></el-col>
                    </el-row>
                  </div>
                  <div v-for="stoppedProcess in processListStopped" :key="stoppedProcess.id">
                    <el-row v-if="stoppedProcess.hostName == server.hostName">
                      <el-col :span="8"><el-link :underline="false" type="danger">{{ stoppedProcess.processName
                      }}</el-link></el-col>
                      <el-col :span="6"> <span style="font-size: 18px; color: grey;">{{ stoppedProcess.processState
                      }}<br>{{
  stoppedProcess.stoptime }}</span> </el-col>
                      <el-col :span="6"><el-button type='primary' text='primary' size="small" style="font-size: 18px"  
                          @click="startClick(stoppedProcess)"> start </el-button></el-col>
                      <el-col :span="3"><el-link type="info" style="font-size: 18px"
                          :href="'http://localhost:5000/log?servername=' + encodeURIComponent(stoppedProcess.hostName) + '&processname=' + encodeURIComponent(stoppedProcess.processName)"
                          target="_blank"> log </el-link></el-col>
                    </el-row>
                  </div>
                </el-scrollbar>
              </el-card>
            </el-space>
          </div>
        </el-main>
      </el-container>
    </el-container>
  </el-container>
</template>

<style scoped>
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.text {
  font-size: 14px;
}

.item {
  margin-bottom: 18px;
}

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
  font-size: 22px;
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
<script lang="ts" >

import { defineComponent, ref, onMounted } from 'vue';




interface ServerList {
  AllNodes: any;
  ConnecctSucceed: string[];
  ConnectFailled: string[];
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
  const month = ('0' + (date.getMonth() + 1)).padStart(2, '0');
  const day = ('0' + date.getDate()).padStart(2, '0');
  const hours = ('0' + date.getHours()).padStart(2, '0');
  const minutes = ('0' + date.getMinutes()).padStart(2, '0');
  const seconds = ('0' + date.getSeconds()).padStart(2, '0');

  return `${year}-${month}-${day} ${hours}:${minutes}:${seconds}`;
}

export default defineComponent({
  name: 'MyComponent',
  setup() {
    const serverListOK = ref<{ id: number; hostName: string }[]>([]);
    const serverListNO = ref<{ id: number; hostName: string }[]>([]);
    const processListRunning = ref<{ id: number; hostName: string; uptime: string; processName: string; processState: string }[]>([]);
    const processListStarting = ref<{ id: number; hostName: string; starttime: string; processName: string; processState: string }[]>([]);
    const processListStopped = ref<{ id: number; hostName: string; stoptime: string; processName: string; processState: string }[]>([]);

    const startClick = async (item: { hostName: string, processName: string }) => {
      const url = `http://localhost:5000/start?servername=${item.hostName}&processname=${item.processName}`;
      await fetch(url);
      await new Promise((resolve) => setTimeout(resolve, 0)); // 等待异步操作完成
      location.reload();
      console.log("ok")
    };

    const stopClick = async (item: { hostName: string, processName: string }) => {
      const url = `http://localhost:5000/stop?servername=${item.hostName}&processname=${item.processName}`;
      await fetch(url);
      await new Promise((resolve) => setTimeout(resolve, 0)); // 等待异步操作完成
      location.reload();
      console.log("ok")
    };

    async function getServerList() {
      await fetch('http://localhost:5000/serverList')
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
      await fetch('http://localhost:5000/processList/all/')
        .then(response => response.json())
        .then((data: Servers) => {
          let id = 0;
          console.log(data);
          const serverNames = Object.keys(data);
          console.log(serverNames);
          console.log(serverNames[0]);
          for (let i in serverNames) {
            console.log("test2")
            for (let a in data[serverNames[i]]) {
              if (data[serverNames[i]][a].state == 20) {
                processListRunning.value.push({ id: id++, hostName: serverNames[i], uptime: convertTime(data[serverNames[i]][a].start), processName: data[serverNames[i]][a].name, processState: data[serverNames[i]][a].statename });
                console.log(a)
              }
              else if (data[serverNames[i]][a].state == 10) {
                processListStarting.value.push({ id: id++, hostName: serverNames[i], starttime: convertTime(data[serverNames[i]][a].start), processName: data[serverNames[i]][a].name, processState: data[serverNames[i]][a].statename });
              } else {
                processListStopped.value.push({ id: id++, hostName: serverNames[i], stoptime: convertTime(data[serverNames[i]][a].stop), processName: data[serverNames[i]][a].name, processState: data[serverNames[i]][a].statename });
              }
            }
          }
        })
        .catch(error => {
          console.error('Error:', error);
        });
    }
    async function test() {
      await getServerList()
      await getProcessList()
    }
    onMounted(() => {
      test()
    });
    return {
      serverListOK,
      serverListNO,
      processListRunning,
      processListStopped,
      processListStarting,
      startClick,
      stopClick
    };
  }
});
</script>