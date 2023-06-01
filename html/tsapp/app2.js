// 发送 GET 请求获取数据
fetch('http://127.0.0.1:5000/all/all')
    .then(function (response) { return response.json(); })
    .then(function (data) {
    console.log(data.servers[0].name);
    //     for(let i of data.ConnecctSucceed){
    //     }
})
    .catch(function (error) {
    console.error('Error:', error);
});
