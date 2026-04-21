<template>
    <n-config-provider :locale="zhCN" :date-locale="dateZhCN">
        <h1>支持人员权限</h1>
        <n-space justify="space-between">
            <n-select style="width: calc(100vw - 320px)" filterable  :options="userlist" @update:value="getUserOwn" />
            <n-transfer style="width: calc(100vw - 320px)"  ref="transfer" v-model:value="value" :options="options"
                :render-source-list="renderSourceList" source-filterable />
        <n-button style="width: calc(100vw - 320px)" type="primary" @click="setUserOwn">提交</n-button>
        <n-modal v-model:show="setUserOwnSuccess" preset="dialog" title="修改已完成" positive-text="确认"/>
        </n-space>
        <h1>添加新的支持人员</h1>
        <n-space justify="space-between">
        <span>
            <span style="font-size: 16px; padding: 4px">windows域登录名：</span>
            <n-input v-model:value="newUserDomain" round style="width: 250px;" placeholder="域"></n-input>
            <span style="font-size: 18px;"> \ </span>
            <n-input v-model:value="newUsername" round style="width: 250px;" @keyup.enter="addUser" placeholder="用户名">
            </n-input>    
        </span>
        <n-button  type="primary" @click="addUser"> 确认 </n-button>
        </n-space>
        <n-modal v-model:show="userNotExist">
            <n-card style="width: 200px; text-align: center;">
                <n-result status="error" title="添加失败(用户可能不存在)">
                </n-result>
            </n-card>
        </n-modal>
        <n-modal v-model:show="addUserSuccess">
            <n-card style="width: 200px; text-align: center;">
                <n-result status="success" title="添加成功">
                </n-result>
            </n-card>
        </n-modal>
        <h1>删除支持人员</h1>
        <n-space justify="space-between">
        <n-select filterable style="width: 300px;" v-model:value="UserToDelet" :options="userlist" />
        <n-button type="error"
            @click="commitDeleteUser = true">删除</n-button>
        </n-space>
        <n-modal v-model:show="commitDeleteUser" preset="dialog" title="确认删除用户？" positive-text="确认" negative-text="取消"
            @positive-click="deleteUser"/>
        <h1>添加管理员</h1>
        <n-space justify="space-between">
        <n-select filterable style="width: 300px;"  v-model:value="UserToAdmin" :options="userlist" />
        <n-button type="primary"  @click="commitAddAdmin = true">提交</n-button>
        </n-space>
        <n-modal v-model:show="commitAddAdmin" preset="dialog" title="确认将此用户添加为管理员？" positive-text="确认" negative-text="取消"
            @positive-click="addAdmin" />
        <!-- <h1>移除管理员权限</h1>
        <n-select filterable style="padding: 4px;" v-model:value="AdminToUser" :options="adminlist"/>
        <n-button size="large" type="error" style="position: relative; left: calc(100vw - 430px);"
            @click="removeAdmin">移除权限</n-button>
        <n-list>
            <n-list-item v-for="group in adminList" :key="group.id">
                <n-thing title="{{ group.groupname }}">
                    <p v-for="admin in group.admins" :key="admin.id">{{ admin.username }}</p>
                </n-thing>
            </n-list-item>
        </n-list> -->
    </n-config-provider>
</template>
  
<script setup lang="ts">
import { ref, h, onMounted } from 'vue'
import { NTree, TransferRenderSourceList, NConfigProvider, SelectOption, zhCN, dateZhCN, SelectGroupOption } from 'naive-ui'


const props = defineProps({
    url: String,
})

interface Option {
    label: string
    value?: string | number
    children?: Option[]
}

const treeData = ref<Option[]>([])
const value = ref<string[]>([])
const options = ref(flattenTree(treeData.value))
const userlist = ref<SelectGroupOption[]>([])
const userSelect = ref<{
    username: string
    domain: string
}>()
const newUserDomain = ref<string>()
const newUsername = ref<string>()
const userNotExist = ref(false)
const setUserOwnFail = ref(false)
const setUserOwnSuccess = ref(false)
const addUserSuccess = ref(false)
const commitDeleteUser = ref(false)
const commitAddAdmin = ref(false)
const UserToDelet = ref('')
const UserToAdmin = ref('')

let serverList: Set<string> = new Set()

async function getTreeData() {
    const treeOptions: Option[] = []
    const serverListRes = await fetch(`${props.url}/serverList`)
    const data = await serverListRes.json()
    for (const hostName of data.ConnecctSucceed) {
        const option: Option = {
            label: hostName,
            value: hostName,
            children: [],
        }
        serverList.add(hostName)
        if (option.children === undefined) {
            continue
        }
        const processListRes = await fetch(`${props.url}/processList?servername=${hostName}`)
        const processData = await processListRes.json()
        for (const processName of processData) {
            const fullprocess = () => {
                if (processName.group === processName.name) {
                    return `${processName.name}`
                }
                return `${processName.group}:${processName.name}`
            }
            const fullprocessName = fullprocess()
            const processInfo = { hostname: hostName, process: fullprocessName }
            option.children.push({
                label: fullprocessName,
                value: JSON.stringify(processInfo),
            })
        }
        treeOptions.push(option)
    }
    treeData.value = treeOptions
    options.value = flattenTree(treeOptions)
    return treeOptions
}

function flattenTree(list: Option[]): Option[] {
    const result: Option[] = []
    function flatten(_list: Option[] = []) {
        _list.forEach((item) => {
            result.push(item)
            flatten(item.children)
        })
    }
    flatten(list)
    return result
}

const renderSourceList: TransferRenderSourceList = function ({ onCheck, pattern }) {
    return h(NTree, {
        style: 'margin: 0 4px;',
        keyField: 'value',
        cascade: true,
        checkable: true,
        selectable: false,
        showIrrelevantNodes: false,
        blockLine: true,
        checkOnClick: true,
        data: treeData.value,
        pattern,
        checkedKeys: value.value,
        onUpdateCheckedKeys: (checkedKeys: string[]) => {
            let tmp = checkedKeys.filter((server) => !serverList.has(server))
            checkedKeys = tmp
            value.value = tmp
            console.log(checkedKeys)
            onCheck(checkedKeys)
        },
    })
}

async function getUserList() {
    userlist.value = []
    const res = await fetch(`${props.url}/userList`)
    const data = await res.json()
    for (let domain in data) {
        let usernamelist: SelectOption[] = []
        for (let username of data[domain]) {
            usernamelist.push({
                label: username,
                value: `{"username": "${username}", "domain": "${domain}"}`,
            })
        }
        let group: SelectGroupOption[] = [{
            type: 'group',
            label: domain,
            key: domain,
            children: usernamelist
        }]
        userlist.value = userlist.value.concat(group)
    }
}

async function getUserOwn(username: string) {
    const user = JSON.parse(username)
    userSelect.value = {
        username: user.username as string,
        domain: user.domain as string
    }
    const userown = await fetch(`${props.url}/userOwn?username=${user.username}&domain=${user.domain}`)
    const data = await userown.json()
    value.value = []
    for (let hostName in data) {
        for (let fullprocessName of data[hostName]) {
            const processInfo = { hostname: hostName, process: fullprocessName }
                value.value.push(JSON.stringify(processInfo))
        }
    }
}

async function setUserOwn() {
  let userWillOwn: { [key: string]: string[] } = {};
  for (let processInfo of value.value) {
    const process = JSON.parse(processInfo);
    if ((process.hostname as string) in userWillOwn) {
      userWillOwn[process.hostname as string].push(process.process as string);
    } else {
      userWillOwn[process.hostname as string] = [process.process as string];
    }
  }
  console.log(JSON.stringify({
    userown: userWillOwn
  }));

  try {
    if (userSelect.value === undefined) {
      return 0;
    }
    const res = await fetch(`${props.url}/setUserOwn?username=${userSelect.value.username}&domain=${userSelect.value.domain}`, {
      method: 'post',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        userown: userWillOwn
      })
    });
    const data = await res.json();
    if (data.flag === true) {
      setUserOwnSuccess.value = true;
    } else {
      setUserOwnFail.value = true;
    }
  } catch (error) {
    setUserOwnFail.value = true;
  }
}
async function addUser() {
    try{
        const res = await fetch(`${props.url}/addUser?username=${newUsername.value}&domain=${newUserDomain.value}`, {
            method: 'get',
        })
        const data = await res.json()
        if (data.flag === true) {
            addUserSuccess.value = true
            newUsername.value = ''
            newUserDomain.value = ''
            getUserList()
        } else {
            userNotExist.value = true
        }
    }catch(error){
        userNotExist.value = true
        console.log(error)
    }
}

async function deleteUser() {
    if (UserToDelet.value === '') {
        return 0
    }
    const userInfo = JSON.parse(UserToDelet.value as string)
    try{
        const res = await fetch(`${props.url}/deleteUser?username=${userInfo.username}&domain=${userInfo.domain}`)
        const data = await res.json()
        if (data.flag === true) {
            UserToDelet.value = ''
            getUserList()
        }
    }catch(error){
        console.log(error)
    }

}
async function addAdmin() {
    if (UserToAdmin.value === '') {
        return 0
    }
    const userInfo = JSON.parse(UserToAdmin.value as string)
    try{
        const res = await fetch(`${props.url}/userToAdmin?username=${userInfo.username}&domain=${userInfo.domain}`)
        const data = await res.json()
        if (data.flag === true) {
            UserToAdmin.value = ''
            getUserList()
        }
    }catch(error){
        console.log(error)
    }

}


onMounted(() => {
    getTreeData()
    getUserList()
})
</script>