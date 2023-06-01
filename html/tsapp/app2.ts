
interface allProcessList {
   servers: any[] 
  } 
// 发送 GET 请求获取数据
fetch('http://127.0.0.1:5000/all/all')
  .then(response => response.json())
  .then((data: allProcessList) => {
    console.log(data.servers[0].name)

//     for(let i of data.ConnecctSucceed){
//     }
  })
  .catch(error => {
    console.error('Error:', error);
  });
