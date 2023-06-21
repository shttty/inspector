<template>
  <div style="height: 100px;"></div>
  <n-grid :x-gap="50" :cols="3" >
    <n-grid-item :offset="1">
    <n-card  hoverable size="huge" justify-content="center"
  align-items="center">
      <h1 align="center">Login</h1>
      <n-space vertical size="large" style=";">
      <n-input size="large" v-model:value="username" placeholder="Username" />
      <n-input type="password" show-password-on="mousedown" size="large" v-model:value="password" placeholder="Password" />
      <div style="padding-left: 42%;"><n-button size="large"  @click="login">登录</n-button> </div>  
      <n-alert v-if="loginFlag" type="warning">
      用户名或密码错误
      </n-alert>
    </n-space>
    </n-card>
    </n-grid-item>
  </n-grid>
</template>

<script lang="ts" setup>
import { ref } from 'vue';
import Cookies from 'js-cookie';
import CryptoJS from 'crypto-js';



const username = ref('');
const password = ref('');
const loginFlag = ref(false);

const url = "/api";

function enhance(token: string) {
  console.log(CryptoJS.SHA512(token).toString());
  return CryptoJS.SHA512(token).toString();
}

async function login() {
  try {
    const passwordEnhanced = enhance(password.value);
    const response = await fetch(`${url}/login`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        userName: username.value,
        password: passwordEnhanced
      })
    });
    const data = await response.json();
    if (data.flag) {
      console.log("用户登录成功");
      const token = enhance(`${username.value}:${password.value}`);
      console.log(token);
      Cookies.set('userName', username.value);
      Cookies.set('userToken', token);
      const responseSuccess = await fetch(`${url}/login/success`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          userName: username.value,
          userToken: token
        })
      });
      const dataSuccess = await responseSuccess.json();
      if (dataSuccess.flag) {
        console.log("Token 已被接受");
        const responseCheck = await fetch(`${url}/login/check`, {
          method: 'get' 
        });
        const dataCheck = await responseCheck.json();
        if (dataCheck.flag) {
          console.log("Token 正常");
          window.location.replace("../");
        }
      }
    } else {
      loginFlag.value = true;
      console.log("用户名或密码错误");
    }
  } catch (error) {
    console.log(error);
  }
}
</script>

<style scoped>
.n-card{
  height: 400px;
} 
</style>

