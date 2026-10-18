// Pure offline control check. Lock lifecycle is a JS substitute, never a browser proof.
const assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path'),vm=require('node:vm');
// Only this small function's erased TS annotations; the final build separately
// checks the complete module. No assumption about a compiler runtime JS API.
const source=fs.readFileSync(path.resolve(__dirname,'../src/activities/teachingIntents.ts'),'utf8');
const start=source.indexOf('const EDITOR_OWNER_KEY'),end=source.indexOf('export type TeachingIntentSummary');
assert.ok(start>=0&&end>start);
const compiled=source.slice(start,end)
 .replace('let editorOwner: Promise<string | null> | null = null;','let editorOwner = null;')
 .replace('export function teachingEditorOwner(): Promise<string | null>','function teachingEditorOwner()')
 .replace('let candidate: string;','let candidate;').replace(/new Promise<(boolean|void)>/g,'new Promise')
 +'\nexports.teachingEditorOwner=teachingEditorOwner;';
const locks=new Set(),OWNER='retrolume.teaching-editor-owner.v1';let ordinal=0;
function moduleFor(saved,options={}){
 const values=new Map(saved?[[OWNER,saved]]:[]),exports={};
 const context={exports,crypto:{randomUUID:()=>`00000000-0000-4000-8000-${String(++ordinal).padStart(12,'0')}`},
  navigator:options.unsupported?{}:{locks:{request:async(name,_options,callback)=>{
   if(locks.has(name))return callback(null);locks.add(name);try{return await callback({name});}finally{locks.delete(name);}
  }}},sessionStorage:{getItem:key=>{if(options.denied)throw new Error('denied');return values.get(key)||null;},setItem:(key,value)=>values.set(key,value)}};
 vm.runInNewContext(compiled,context);return {owner:exports.teachingEditorOwner,values};
}
(async()=>{
 const first=moduleFor(null),promise=first.owner();assert.equal(first.owner(),promise);const a=await promise;
 assert.equal(first.values.get(OWNER),a);
 const cloned=moduleFor(a),b=await cloned.owner();assert.notEqual(b,a);assert.equal(cloned.values.get(OWNER),b);
 locks.delete(`${OWNER}:${a}`);const reloaded=moduleFor(a);assert.equal(await reloaded.owner(),a);
 assert.equal(await moduleFor(null,{denied:true}).owner(),null);assert.equal(await moduleFor(null,{unsupported:true}).owner(),null);
 console.log(JSON.stringify({status:'pass',cases:['cached_owner','cloned_owner_collision','reload_owner','denied_storage','unsupported_locks'],
  grade:'pure_JS_lock_substitute_no_browser_launch'}));
})().catch(error=>{console.error(error.stack);process.exitCode=1;});
