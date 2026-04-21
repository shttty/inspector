<template>
  <n-layout has-sider position="absolute">
    <n-layout-header>
      <n-space justify="space-between" style=" padding: 14px; background-color: #336680;">
        <n-space>
          <n-gradient-text style=" color: #d9d9db" :size="24"> 进程管理</n-gradient-text>
        </n-space>
        <!-- <n-space>
          <n-input placeholder="搜索">
            <template #prefix>
              <n-icon color="#d9d9db" size="20">
                <Search />
              </n-icon>
            </template>
          </n-input>
        </n-space> -->
        <n-space>
          <n-gradient-text v-show="loginFlag" style="color: #d9d9db" :size="18"> {{ username }}@{{ domain
            }}</n-gradient-text>
          <n-dropdown trigger="hover" :options="options" @select="handleSelect">
            <n-icon v-show="loginFlag" color="#d9d9db" size="35">
              <People />
            </n-icon>
          </n-dropdown>
          <n-button v-show="!loginFlag" ghost color="#d9d9db" @click="showLogin = true">login</n-button>
        </n-space>
      </n-space>
    </n-layout-header>
    <n-layout has-sider position="absolute" style="top: 60px">
      <n-layout-sider content-style="background: #FAFAFA; padding: 20px">
        <n-gradient-text style="color: #383A42" :size="28">Servers</n-gradient-text>
        <n-divider />
        <n-scrollbar style="height: calc(100vh - 200px)" trigger="none">
          <n-button v-for="server in serverListOK" :key="server.id" size="large" quaternary color="#0084BC"
            style="width: 100px; padding-right: 200px; font-size: 22px" @click="ChoseServer(server.hostName)">{{
            server.hostName }}</n-button>
          <n-button v-for="server in serverListNO" :key="server.id" size="large" quaternary color="#E45649"
            style="width: 100px; padding-right: 200px; font-size: 22px">{{ server.hostName }}</n-button>
        </n-scrollbar>
      </n-layout-sider>
      <n-scrollbar x-scrollable>
        <n-layout-content content-style="padding: 24px">
          <n-space v-if="switchFlag === 0">
            <node v-for="server in serverListOK" :key="server.id" :server_name="server.hostName" :url="address" />
          </n-space>
          <n-space v-if="switchFlag === 1">
            <mannode v-for="server in serverOwn" :key="server.id" :server_name="server.hostName" :url="address"
              :overview="true" />
          </n-space>
          <n-space v-if="switchFlag === 2">
            <usermanager :url="address" />
          </n-space>
          <n-space v-if="switchFlag === 3">
            <ldapmanager :url="address" />
          </n-space>
        </n-layout-content>
      </n-scrollbar>
    </n-layout>
  </n-layout>
  <n-modal v-model:show="showLogin">
    <n-card style="max-width:500px;">
      <n-space vertical>
        <n-space justify="center" style="font-size: 20px;">login </n-space>
        <div style="height: 20px;"></div>
        <n-space justify="center"><span style="font-size: 16px;">账号：</span>
          <span>
            <n-input v-model:value="domainL" round style="width: 150px;" placeholder="域"></n-input>
            <span style="font-size: 18px;"> \ </span>
            <n-input v-model:value="usernameL" round style="width: 150px;" placeholder="用户名">
            </n-input>
          </span>
        </n-space>
        <div style="height: 20px;"></div>
        <n-space justify="center"><span style="font-size: 16px;">密码：</span>
          <n-input @keyup.enter="login" v-model:value="password" round type="password" show-password-on="mousedown"
            style="width: 300px;" placeholder="password"></n-input>
        </n-space>
        <div style="height: 30px;"></div>
        <n-space justify="center"><n-button @click="login" type="primary" style="width: 360px;">登录</n-button></n-space>
        <n-alert v-if="loginFail" title="登录出错" type="error">
          用户名或密码错误
        </n-alert>
      </n-space>
    </n-card>
  </n-modal>
  <n-modal preset="card" v-model:show="showServerToManage" style="width: 60%; min-width: 443px;">
    <MannodeContetLarge :server_name="NameOfServerToManage" :url="address" />
  </n-modal>
  <n-modal preset="card" v-model:show="showServerToShow" style="width: 60%; min-width: 443px;">
    <nodeInfo :server_name="NameOfServerToShow" :url="address" />
  </n-modal>
</template>

<script lang="ts" setup >

import { ref, onMounted, h, Component } from 'vue'
import { People, LogOutOutline, Cog, Build, Home, ServerOutline } from '@vicons/ionicons5'
import { NIcon } from 'naive-ui'
import CryptoJS from "crypto-js"

import node from './components/node.vue'
import mannode from './components/mannode.vue'
import usermanager from './components/usermanager.vue'
import ldapmanager from './components/ldapmanager.vue'
import nodeInfo from './components/nodeInfo.vue'
import MannodeContetLarge from './components/mannodeContetLarge.vue'


const switchFlag = ref<number>(0)
const loginFlag = ref(false)
const username = ref<string | undefined>('')
const domain = ref<string | undefined>('')
const showLogin = ref(false)
const usernameL = ref('')
const domainL = ref('')
const password = ref('')
const loginFail = ref(false)
const showServerToManage = ref(false)
const NameOfServerToManage = ref('')
const showServerToShow = ref(false)
const NameOfServerToShow = ref('')

const url = `/api`
const address = ref(`${url}`)


const serverListOK = ref<{ id: number; hostName: string }[]>([])
const serverListNO = ref<{ id: number; hostName: string }[]>([])
const serverOwn = ref<{ id: number; hostName: string }[]>([])

let keyword = ""

interface ServerList {
  AllNodes: any
  ConnecctSucceed: string[]
  ConnectFailled: string[]
}

const renderIcon = (icon: Component) => {
  return () => {
    return h(NIcon, null, {
      default: () => h(icon)
    })
  }
}

const options = ref<any[]>([{
  label: '登出',
  key: 'logout',
  icon: renderIcon(LogOutOutline)
}])

function ChoseServer(serverName: string) {
  if (switchFlag.value === 0) {
    NameOfServerToShow.value = serverName
    showServerToShow.value = true
    return
  }
  if (switchFlag.value === 1) {
    for (let server in serverOwn.value) {
      if (serverOwn.value[server].hostName === serverName) {
        console.log("yes")
        NameOfServerToManage.value = serverName
        showServerToManage.value = true
        return
      }
    }
    alert("你没有程序跑在这个服务器上");
  }
}

async function premission() {
  if (loginFlag.value === false) {
    return 0
  }
  const res = await fetch(`${url}/premissionTest`)
  const data = await res.json()
  if (data.flag === true) {
    options.value = [
      {
        label: '主页',
        key: 'main',
        icon: renderIcon(Home)
      },
      {
        label: '程序管理',
        key: 'manage',
        icon: renderIcon(Cog)
      },
      {
        label: '管理员',
        key: 'userManage',
        icon: renderIcon(Build)
      },
      {
        label: 'LDAP 配置',
        key: 'ldapManage',
        icon: renderIcon(ServerOutline)
      },
      {
        label: '登出',
        key: 'logout',
        icon: renderIcon(LogOutOutline)
      }
    ]
  } else {
    options.value = [
      {
        label: '主页',
        key: 'main',
        icon: renderIcon(Home)
      },
      {
        label: '程序管理',
        key: 'manage',
        icon: renderIcon(Cog)
      },
      {
        label: '登出',
        key: 'logout',
        icon: renderIcon(LogOutOutline)
      }
    ]
  }
}



function handleSelect(key: string) {
  if (key === 'main') {
    return switchFlag.value = 0
  }
  if (key === 'manage') {
    return switchFlag.value = 1
  }
  if (key === 'userManage') {
    return switchFlag.value = 2
  }
  if (key === 'ldapManage') {
    return switchFlag.value = 3
  }
  if (key === 'logout') {
    fetch(`${url}/logout`)
    loginFlag.value = false
    window.location.reload()
    return 0
  }
}

async function getServerList() {
  await fetch(`${url}/serverList`)
    .then(response => response.json())
    .then((data: ServerList) => {
      let id = 0
      for (let i of data.ConnecctSucceed) {
        serverListOK.value.push({ id: id++, hostName: i })
      }
      let idf = 0
      for (let i of data.ConnectFailled) {
        serverListNO.value.push({ id: idf++, hostName: i })
      }
    })
    .catch(error => {
      console.error('Error:', error)
    })
}

async function getserverOwn() {
  if (loginFlag.value === false) {
    return 0
  }
  const res = await fetch(`${url}/serverOwn`)
  const data = await res.json()
  let id = 0
  for (let i of data) {
    serverOwn.value.push({ id: id++, hostName: i })
  }
}


async function loginState() {
  const res = await fetch(`${url}/loginstate`)
  const data = await res.json()
  if (data.flag === false) {
    loginFlag.value = false
    keyword = data.key
    return 0
  } else {
    loginFlag.value = true
    switchFlag.value = 1
    username.value = data.username
    domain.value = data.domain
    await premission()
    await getserverOwn()
  }
}

async function load() {
  serverListNO.value = []
  serverListOK.value = []
  await getServerList()
}
async function login() {
  const passwd = CryptoJS.enc.Utf8.parse(password.value)
  const enhanced = CryptoJS.AES.encrypt(passwd, CryptoJS.MD5(keyword), {
    iv: CryptoJS.MD5(keyword),
    mode: CryptoJS.mode.CBC, // 加密模式为CBC
    padding: CryptoJS.pad.Pkcs7 // 填充方式为Pkcs7
  })
  const res = await fetch(`${url}/login`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      domain: domainL.value,
      username: usernameL.value,
      password: enhanced.toString()
    })
  })
  const data = await res.json()
  if (data.flag === false) {
    loginFail.value = true
    loginState()
    return
  }
  window.location.reload()
}
onMounted(() => {
  loginState()
  load()

})
</script>
