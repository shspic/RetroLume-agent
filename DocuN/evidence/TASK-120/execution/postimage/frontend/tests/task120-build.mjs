// Exact existing build script components, without Windows npm.cmd quoting.
import {spawnSync} from 'node:child_process';
for(const args of [['node_modules/typescript/bin/tsc','--noEmit'],['node_modules/vite/bin/vite.js','build']]){
  const result=spawnSync(process.execPath,args,{stdio:'inherit',timeout:140000,shell:false});
  if(result.error)throw result.error;
  if(result.status!==0)process.exit(result.status??1);
}
