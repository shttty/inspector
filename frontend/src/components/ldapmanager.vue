<template>
  <n-config-provider :locale="zhCN" :date-locale="dateZhCN">
    <n-space vertical size="large">
      <n-space justify="space-between" align="center">
        <h1>LDAP 服务器配置</h1>
        <n-button type="primary" @click="openAdd">添加服务器</n-button>
      </n-space>

      <n-data-table :columns="columns" :data="servers" :row-key="(row: LdapServer) => row.name" />

      <!-- Add / Edit modal -->
      <n-modal v-model:show="showModal" preset="card" :title="editing ? '编辑 LDAP 服务器' : '添加 LDAP 服务器'" style="width: 640px">
        <n-form ref="formRef" :model="form" label-placement="left" label-width="auto">
          <n-form-item label="名称" path="name">
            <n-input v-model:value="form.name" :disabled="editing" placeholder="如 wequant" />
          </n-form-item>
          <n-form-item label="主机" path="host">
            <n-input v-model:value="form.host" placeholder="10.1.2.5" />
          </n-form-item>
          <n-form-item label="端口" path="port">
            <n-input-number v-model:value="form.port" :min="1" :max="65535" style="width: 100%" />
          </n-form-item>
          <n-form-item label="SSL" path="use_ssl">
            <n-switch v-model:value="form.use_ssl" />
          </n-form-item>
          <n-divider>Service Account</n-divider>
          <n-form-item label="Bind DN" path="bind_dn">
            <n-input v-model:value="form.bind_dn" placeholder="CN=svc-inspector,OU=Service Accounts,DC=..." />
          </n-form-item>
          <n-form-item label="Bind 密码" path="bind_password">
            <n-input v-model:value="form.bind_password" type="password" show-password-on="mousedown"
              placeholder="留空不修改" />
          </n-form-item>
          <n-divider>用户搜索</n-divider>
          <n-form-item label="Search Base" path="user_search_base">
            <n-input v-model:value="form.user_search_base" placeholder="DC=wequant,DC=com" />
          </n-form-item>
          <n-form-item label="Search Filter" path="user_search_filter">
            <n-input v-model:value="form.user_search_filter"
              placeholder="(sAMAccountName={username})" />
          </n-form-item>
          <n-divider>属性映射</n-divider>
          <n-form-item label="用户名属性">
            <n-input v-model:value="form.attr_username" placeholder="sAMAccountName" />
          </n-form-item>
          <n-form-item label="显示名属性">
            <n-input v-model:value="form.attr_display_name" placeholder="cn" />
          </n-form-item>
          <n-form-item label="邮箱属性">
            <n-input v-model:value="form.attr_email" placeholder="mail" />
          </n-form-item>
          <n-divider>组 → 角色映射</n-divider>
          <n-form-item label="Admin 组 DN">
            <n-input v-model:value="form.role_mapping_admin"
              placeholder="CN=Inspector-Admins,OU=Groups,DC=..." />
          </n-form-item>
          <n-form-item label="值班 组 DN">
            <n-input v-model:value="form.role_mapping_onduty"
              placeholder="CN=Inspector-OnDuty,OU=Groups,DC=..." />
          </n-form-item>
          <n-divider>域</n-divider>
          <n-form-item label="关联域名">
            <n-dynamic-tags v-model:value="form.domains" />
          </n-form-item>
        </n-form>
        <n-space justify="end">
          <n-button @click="testConn" :loading="testing">测试连接</n-button>
          <n-button type="primary" @click="submit" :loading="submitting">
            {{ editing ? '保存' : '添加' }}
          </n-button>
        </n-space>
        <n-alert v-if="testResult !== null" :type="testResult.ok ? 'success' : 'error'" :title="testResult.message"
          style="margin-top: 12px" />
      </n-modal>

      <!-- Delete confirm -->
      <n-modal v-model:show="showDeleteConfirm" preset="dialog" title="确认删除？"
        :content="`删除 LDAP 服务器 '${deleteTarget}'？`" positive-text="删除" negative-text="取消"
        @positive-click="doDelete" />
    </n-space>
  </n-config-provider>
</template>

<script setup lang="ts">
import { ref, h, onMounted } from 'vue'
import { NButton, NSpace, zhCN, dateZhCN, type DataTableColumns } from 'naive-ui'

const props = defineProps({
  url: String,
})

interface LdapServer {
  id?: number
  name: string
  host: string
  port: number
  use_ssl: boolean | number
  bind_dn: string
  bind_password: string
  user_search_base: string
  user_search_filter: string
  attr_username: string
  attr_display_name: string
  attr_email: string
  role_mapping_admin: string
  role_mapping_onduty: string
  domains: string[]
}

const servers = ref<LdapServer[]>([])
const showModal = ref(false)
const editing = ref(false)
const editingName = ref('')
const submitting = ref(false)
const testing = ref(false)
const testResult = ref<{ ok: boolean; message: string } | null>(null)
const showDeleteConfirm = ref(false)
const deleteTarget = ref('')

const emptyForm = (): LdapServer => ({
  name: '',
  host: '',
  port: 389,
  use_ssl: false,
  bind_dn: '',
  bind_password: '',
  user_search_base: '',
  user_search_filter: '(sAMAccountName={username})',
  attr_username: 'sAMAccountName',
  attr_display_name: 'cn',
  attr_email: 'mail',
  role_mapping_admin: '',
  role_mapping_onduty: '',
  domains: [],
})

const form = ref<LdapServer>(emptyForm())

const columns: DataTableColumns<LdapServer> = [
  { title: '名称', key: 'name', width: 120 },
  { title: '主机', key: 'host', width: 140 },
  { title: '端口', key: 'port', width: 70 },
  { title: 'Search Base', key: 'user_search_base', ellipsis: { tooltip: true } },
  {
    title: '域',
    key: 'domains',
    width: 140,
    render(row: LdapServer) {
      const d = row.domains
      return Array.isArray(d) ? d.join(', ') : String(d || '')
    },
  },
  {
    title: '操作',
    key: 'actions',
    width: 180,
    render(row: LdapServer) {
      return h(NSpace, {}, {
        default: () => [
          h(NButton, { size: 'small', onClick: () => openEdit(row) }, { default: () => '编辑' }),
          h(NButton, { size: 'small', type: 'error', onClick: () => confirmDelete(row.name) }, { default: () => '删除' }),
        ]
      })
    },
  },
]

async function loadServers() {
  try {
    const res = await fetch(`${props.url}/ldap/servers`)
    if (res.ok) {
      servers.value = await res.json()
    }
  } catch (e) {
    console.error('Failed to load LDAP servers', e)
  }
}

function openAdd() {
  editing.value = false
  editingName.value = ''
  form.value = emptyForm()
  testResult.value = null
  showModal.value = true
}

function openEdit(row: LdapServer) {
  editing.value = true
  editingName.value = row.name
  form.value = {
    ...emptyForm(),
    ...row,
    use_ssl: Boolean(row.use_ssl),
    domains: Array.isArray(row.domains) ? [...row.domains] : [],
    bind_password: '',  // don't show masked password
  }
  testResult.value = null
  showModal.value = true
}

function confirmDelete(name: string) {
  deleteTarget.value = name
  showDeleteConfirm.value = true
}

async function doDelete() {
  try {
    await fetch(`${props.url}/ldap/servers/${deleteTarget.value}`, { method: 'DELETE' })
    await loadServers()
  } catch (e) {
    console.error(e)
  }
}

async function testConn() {
  testing.value = true
  testResult.value = null
  try {
    const payload = {
      host: form.value.host,
      port: form.value.port,
      use_ssl: form.value.use_ssl,
      bind_dn: form.value.bind_dn,
      bind_password: form.value.bind_password,
      user_search_base: form.value.user_search_base,
    }
    const res = await fetch(`${props.url}/ldap/servers/test`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    })
    const data = await res.json()
    testResult.value = { ok: data.flag, message: data.message || (data.flag ? '连接成功' : '连接失败') }
  } catch (e) {
    testResult.value = { ok: false, message: String(e) }
  }
  testing.value = false
}

async function submit() {
  submitting.value = true
  try {
    const payload = { ...form.value, use_ssl: form.value.use_ssl ? 1 : 0 }
    // Don't send empty password on edit (backend keeps old value)
    if (editing.value && !payload.bind_password) {
      payload.bind_password = '******'
    }

    if (editing.value) {
      await fetch(`${props.url}/ldap/servers/${editingName.value}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      })
    } else {
      await fetch(`${props.url}/ldap/servers`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      })
    }
    showModal.value = false
    await loadServers()
  } catch (e) {
    console.error(e)
  }
  submitting.value = false
}

onMounted(() => {
  loadServers()
})
</script>
