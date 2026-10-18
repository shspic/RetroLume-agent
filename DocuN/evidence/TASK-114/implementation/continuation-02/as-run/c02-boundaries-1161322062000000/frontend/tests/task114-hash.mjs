// 独立 node:crypto oracle 校验流式哈希，包括块和填充边界。
import fs from 'node:fs';
import crypto from 'node:crypto';
import assert from 'node:assert/strict';
import {fileHash} from '../src/data/fileHash.ts';
const cases=[0,1,3,55,56,63,64,65,127,128,65535,65536,65537,131073];
for(const size of cases){const bytes=Buffer.alloc(size);for(let i=0;i<size;i++)bytes[i]=(i*37+9)&255;
  assert.equal(await fileHash(new Blob([bytes])),crypto.createHash('sha256').update(bytes).digest('hex'),String(size));}
assert.equal(await fileHash(new Blob(['abc'])),'ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad');
console.log(JSON.stringify({status:'PASS',cases:cases.length+1,oracle:'node:crypto',whole_file_buffer:false}));
