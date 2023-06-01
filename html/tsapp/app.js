"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
fetch('http://127.0.0.1:5000/all/all')
    .then(function (response) { return response.json(); })
    .then(function (data) {
    console.log(data);
    var serverNames = Object.keys(data);
    console.log(serverNames);
    for (var i in serverNames) {
        console.log(data[serverNames[i]]);
        for (var a in data[serverNames[i]]) {
            console.log("a");
            console.log(data[serverNames[i]][a].name);
        }
    }
    console.log(data[serverNames[0]][0]);
    // console.log(data[serverNames[0]][0])
})
    .catch(function (error) {
    console.error('Error:', error);
});
// const serversInfo = servers[serverListOK[0]];
// for (const serverName of serverNames) {
//   const serversInfo = servers[serverName];
//   console.log(`Servers in group ${serverName}:`);
//   for (const server of serversInfo) {
//     console.log(`- ${server.name}`);
//   }
// }
