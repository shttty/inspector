import { da } from "element-plus/es/locale";

interface process {
        name: string;
        group: string;
        start: number;
        stop: number;
        now: number;
        state: number;
        statename: string;
        spawnerr: string;
        exitstatus: number;
        logfile: string;
        stdout_logfile: string;
        stderr_logfile: string;
        pid: number;
        description: string;
}
interface Servers {
        [key: string]: process[];
}
fetch('http://127.0.0.1:5000/all/all')
        .then(response => response.json())
        .then((data: Servers) => {
                console.log(data);
                const serverNames = Object.keys(data);
                console.log(serverNames);
                for(let i in serverNames){
                    console.log(data[serverNames[i]])
                    for(let a in data[serverNames[i]]){
                        console.log("a")
                        console.log(data[serverNames[i]][a].name)
                    }
                }
                console.log(data[serverNames[0]][0])
                
                // console.log(data[serverNames[0]][0])
        })
        .catch(error => {
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