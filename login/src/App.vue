<template>
  <div class="app">
  <n-config-provider :theme-overrides="themeOverrides" >
    <n-el tag="span" style="color: aqua;">
    <n-card title="login" hoverable size="huge" justify-content="center"
  align-items="center">
      卡片内容
    </n-card>
    </n-el>
  <n-global-style />
 </n-config-provider></div>
</template>

<script lang="ts" setup>
import { ref } from 'vue';
import Cookies from 'js-cookie';
import CryptoJS from 'crypto-js';

import { NConfigProvider,type GlobalThemeOverrides } from 'naive-ui'
const themeOverrides: GlobalThemeOverrides = {
    common: {
      primaryColor: '#6260BD',
      baseColor: '#6260BD',
    },
    Button: {
      textColor: '#FF0000'
    }
  }

const username = ref('');
const password = ref('');


function enhance(token: string) {
  console.log(CryptoJS.SHA512(token).toString());
  return CryptoJS.SHA512(token).toString();
}

async function login() {
  try {
    const passwordEnhanced = enhance(password.value);
    
    const response = await fetch('/api/login', {
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
      const responseSuccess = await fetch('/api/login/success', {
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
        const responseCheck = await fetch('/api/login/check', {
          method: 'get' 
        });
        const dataCheck = await responseCheck.json();
        if (dataCheck.flag) {
          console.log("Token 正常");
          const currentDomain = window.location.protocol + '//' + window.location.hostname;
          const newUri = '/';
          const newUrl = currentDomain + newUri;
          window.location.replace(newUrl);
        }
        
      }
    } else {
      console.log("用户名或密码错误");
    }
  } catch (error) {
    console.log(error);
  }
}
</script>

<style scoped>

.n-card{
  width: 500px; 
  height: 300px;
  position: absolute;
	top: 10%;
	left: 37%;
  display: flex;
  justify-content: center;
  align-items: center;
}
</style>

