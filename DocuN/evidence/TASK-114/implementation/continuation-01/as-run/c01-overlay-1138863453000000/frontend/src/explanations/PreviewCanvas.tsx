import {useEffect,useRef} from "react";
export function PreviewCanvas({bytes,identity}:{bytes:Uint8Array|null;identity:string}){
  const canvas=useRef<HTMLCanvasElement>(null),generation=useRef(0);
  useEffect(()=>{const version=++generation.current;const context=canvas.current?.getContext("2d");context?.clearRect(0,0,640,480);
    if(bytes)void createImageBitmap(new Blob([bytes as BlobPart],{type:"image/png"})).then(image=>{
      if(version===generation.current&&image.width===640&&image.height===480)context?.drawImage(image,0,0);image.close();
    }).catch(()=>{if(version===generation.current)context?.clearRect(0,0,640,480);});
    return()=>{generation.current++;context?.clearRect(0,0,640,480);};
  },[bytes,identity]);
  return <canvas ref={canvas} width={640} height={480} aria-label="受信程序计算和图形画面" style={{maxWidth:"100%",height:"auto",border:"1px solid #d5dde5"}}/>;
}
