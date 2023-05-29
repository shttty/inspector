// // 定义一个接口表示从后端返回的数据类型
// let id: number = 0;
// var serverList: { id: number; hostName: string; }[] = []
// // serverList.push({id: id++ , hostName: 'node4'})
// interface ServerList {
//     AllNodes: any;
//     ConnecctSucceed: string[];
//     ConnectFailled: string[];
//   } 
// // 发送 GET 请求获取数据
// fetch('http://127.0.0.1:5000/serverList')
//   .then(response => response.json())
//   .then((data: ServerList) => {
//     // console.log(data)
//     // console.log(data.AllNodes[data.ConnecctSucceed[0]])
//     for(let i of data.ConnecctSucceed){
//       serverList.push({id: id++ , hostName: i})
//       console.log(serverList)
//     }
//   })
//   .catch(error => {
//     console.error('Error:', error);
//   });
// console.log(serverList)
var id = 1;
console.log([
    { id: id++, text: 'Learn HTML' },
    { id: id++, text: 'Learn JavaScript' },
]);
