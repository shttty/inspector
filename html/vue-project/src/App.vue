<template>
  <el-container class="layout-container-demo" style="height: 100%">
    <el-header style="text-align: center; font-size: 12px">
      <h1>Header</h1>
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
                    <!-- <span>{{ server.hostName }}</span> -->
                    <el-link href="https://element-plus.org" target="_blank" style="font-size: 18px">{{ server.hostName }}</el-link>
                  </div>
                </template>
                <el-scrollbar>
                  <!-- <el-row v-for="process in processRunning" :key="process.id" justify="left" :span="6"><el-link :underline="false"
                type="success">{{ process.name }}</el-link></el-row>
                <el-row v-for="process in processStopped" :key="process.id" justify="left" :span="6"><el-link :underline="false"
                type="warrning">{{ process.name }}</el-link></el-row>
                <el-row v-for="process in processErr" :key="process.id" justify="left" :span="6"><el-link :underline="false"
                type="danger">{{ process.name }}</el-link></el-row> -->
                  <el-row>
                    <el-col :span="8"><el-link :underline="false" type="success">running</el-link> </el-col>
                    <el-col :span="6"> <span style="font-size: 18px; color: grey;">{{ uptime }}</span> </el-col>
                    <el-col :span="3"><el-link type="info" style="font-size: 18px">restart</el-link></el-col>
                    <el-col :span="3"><el-link type="info" style="font-size: 18px">stop</el-link></el-col>
                    <el-col :span="3"><el-link type="info" style="font-size: 18px">log</el-link></el-col>
                  </el-row>
                  <el-row>
                    <el-col :span="8"><el-link :underline="false" type="warning">stopped</el-link></el-col>
                    <el-col :span="6"> <span style="font-size: 18px; color: grey;">{{ stopTime }}</span> </el-col>
                    <el-col :span="6"><el-link type="info" style="font-size: 18px"> start </el-link></el-col>
                    <el-col :span="3"><el-link type="info" style="font-size: 18px"> log </el-link></el-col>
                  </el-row>
                  <el-row>
                    <el-col :span="8"><el-link :underline="false" type="danger">exitederr</el-link></el-col>
                    <el-col :span="6"> <span style="font-size: 18px; color: grey;">{{ stopTime }}</span> </el-col>
                    <el-col :span="6"><el-link type="info" style="font-size: 18px"> start </el-link></el-col>
                    <el-col :span="3"><el-link type="info" style="font-size: 18px"> log </el-link></el-col>
                  </el-row>
                </el-scrollbar>
              </el-card>
            </el-space>
          </div>
        </el-main>
        <!-- <el-footer><el-row justify="center"> <el-pagination background layout="prev, pager, next" :total="100"
              :hide-on-single-page="true" /></el-row></el-footer> -->
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

export default defineComponent({
  name: 'MyComponent',
  setup() {
    const serverListOK = ref<{ id: number; hostName: string }[]>([]);
    const serverListNO = ref<{ id: number; hostName: string }[]>([]);

    onMounted(() => {
      fetch('http://127.0.0.1:5000/serverList')
        .then(response => response.json())
        .then((data: ServerList) => {
          let id = 0;
          for (let i of data.ConnecctSucceed) {
            serverListOK.value.push({ id: id++, hostName: i });
            console.log(serverListOK.value);
          }
          let idf = 0;
          for (let i of data.ConnectFailled) {
            serverListNO.value.push({ id: idf++, hostName: i });
            console.log(serverListNO.value);
          }
        })
        .catch(error => {
          console.error('Error:', error);
        });
    });

    return {
      serverListOK,
      serverListNO
    };
  }
});
</script>