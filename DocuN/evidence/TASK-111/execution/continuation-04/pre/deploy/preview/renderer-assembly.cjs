"use strict";
// 与生产宿主共用的纯组装边界，固定资源只作字面插入。
const crypto=require('node:crypto');
function compiledHTML(template,script,style){
 if(typeof template!=='string'||typeof script!=='string'||typeof style!=='string'||
    /<\/script/i.test(script)||/<\/style/i.test(style))throw new Error('renderer_integrity_error');
 for(const token of ['__POLICY__','__STYLE__','__SCRIPT__']){
  if(template.split(token).length!==2)throw new Error('renderer_template_error');
 }
 const hash=value=>crypto.createHash('sha256').update(value,'utf8').digest('base64');
 const policy="default-src 'none'; script-src 'sha256-"+hash(script)+"'; style-src 'sha256-"+hash(style)+"'; frame-src 'none'; connect-src 'none'; img-src 'none'; font-src 'none'; object-src 'none'; worker-src 'none'; form-action 'none'; base-uri 'none'";
 const html=template.replace('__POLICY__',()=>policy).replace('__STYLE__',()=>style).replace('__SCRIPT__',()=>script);
 if(Buffer.byteLength(html,'utf8')>65536)throw new Error('renderer_size_limit');
 return html;
}
module.exports={compiledHTML};
