"use strict";
// 固定启动目录，无页面或stdin命令解释。
const fs=require('node:fs');
for(const path of ['/tmp/preview-private','/home/preview/home','/home/preview/config','/home/preview/cache']){
  fs.mkdirSync(path,{recursive:true,mode:0o700});fs.chmodSync(path,0o700);
  const value=fs.statSync(path);if(value.uid!==10001||value.gid!==10001||(value.mode&0o777)!==0o700)throw new Error('runtime_directory_identity');
}
process.env.HOME='/home/preview/home';process.env.XDG_CONFIG_HOME='/home/preview/config';
process.env.XDG_CACHE_HOME='/home/preview/cache';process.env.TMPDIR='/tmp/preview-private';
require('./renderer-host.cjs');
