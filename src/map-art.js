// Paint is replaceable; source map anchors, layers and footprints are not.
// The offset interpretation remains a documented community-data candidate.
export const MAP_ART_PLACEMENT = Object.freeze({
  cellPixels:40, offsetRule:'anchor * 40 - mapElem.imageOffset',
  status:'candidate-awaiting-original-client-render-comparison',
  geometryAccepted:false,
});
const byElement=new Map(),images=new Map(),pendingImages=new Map(),failedImages=new Map(),imageQueue=[];
let decoding=0,activeFiles=new Set(),activeMapId=null;
const MAX_IDLE_IMAGE_BYTES=64*1024*1024;
let ready=null,loadErrors=[];

function discardIdleImages(){
  let bytes=[...images.values()].reduce((sum,image)=>sum+image.naturalWidth*image.naturalHeight*4,0);
  for(const[file,image]of images){
    if(bytes<=MAX_IDLE_IMAGE_BYTES)break;
    if(!activeFiles.has(file)){bytes-=image.naturalWidth*image.naturalHeight*4;images.delete(file);}
  }
}
function pumpImages(){
  while(decoding<4&&imageQueue.length){
    const{file,resolve}=imageQueue.shift();decoding++;
    const image=new Image();image.decoding='async';image.src='./'+file;
    image.decode().then(()=>{images.set(file,image);discardIdleImages();resolve(true);})
      .catch(error=>{failedImages.set(file,error.message);loadErrors.push({file,error:error.message});resolve(false);})
      .finally(()=>{pendingImages.delete(file);decoding--;pumpImages();});
  }
}
function ensureImage(file){
  if(images.has(file))return Promise.resolve(true);
  if(failedImages.has(file))return Promise.resolve(false);
  if(!pendingImages.has(file)){
    const pending=new Promise(resolve=>imageQueue.push({file,resolve}));pendingImages.set(file,pending);pumpImages();
  }
  return pendingImages.get(file);
}

export function createMapArtCatalog(manifests){
  const catalog=new Map();
  for(const manifest of manifests){
    if(manifest?.tilePixels!==40||!Array.isArray(manifest.pieces))continue;
    for(const piece of manifest.pieces){
      if(!Number.isInteger(piece.elementId)||!piece.file||!(piece.worldFrameWidth>0)||!(piece.worldFrameHeight>0))continue;
      if(catalog.has(piece.elementId))throw new Error(`地图元素 ${piece.elementId} 有重复美术条目`);
      catalog.set(piece.elementId,piece);
    }
  }
  return catalog;
}

export function sourceMapDrawList(source,catalog=byElement){
  if(!source||source.kind!=='source-map'||!Array.isArray(source.sceneObjects))throw new Error('缺少源地图场景对象');
  const missing=new Set(),commands=[];
  for(const object of source.sceneObjects){
    if(object.destroyed)continue;
    const art=catalog.get(object.elementId);
    if(!art){missing.add(object.elementId);continue;}
    const offset=object.imageOffset;
    if(!Array.isArray(offset)||offset.length!==2||!offset.every(Number.isFinite))throw new Error(`元素 ${object.elementId} 缺少源图像偏移`);
    commands.push({instanceId:object.id,elementId:object.elementId,layer:object.layer,
      x:object.x*40-offset[0],y:object.y*40-offset[1],
      width:art.worldFrameWidth,height:art.worldFrameHeight,
      sortY:(object.y+object.height)*40,sortX:object.x,
      file:art.file,geometryAccepted:art.geometryAccepted===true,
      // Separate exact logical footprint from the candidate visual bounds.
      footprint:{x:object.x,y:object.y,width:object.width,height:object.height},
    });
  }
  commands.sort((a,b)=>(a.layer===2?0:1)-(b.layer===2?0:1)||a.sortY-b.sortY||a.layer-b.layer||a.sortX-b.sortX);
  return{commands,missingElementIds:[...missing].sort((a,b)=>a-b),placement:MAP_ART_PLACEMENT};
}

export async function loadMapArt(){
  if(!ready)ready=(async()=>{
    const response=await fetch('./assets/maps/runtime-manifests.json');
    if(!response.ok)throw new Error(`地图美术目录读取失败：${response.status}`);
    const directory=await response.json();
    const manifests=await Promise.all(directory.manifests.map(async file=>{
      try{const result=await fetch('./'+file);if(!result.ok)throw new Error(String(result.status));return await result.json();}
      catch(error){loadErrors.push({file,error:error.message});return null;}
    }));
    for(const[id,piece]of createMapArtCatalog(manifests))byElement.set(id,piece);
    return{elementCount:byElement.size,loadedImages:images.size,errors:loadErrors};
  })().catch(error=>{loadErrors.push({file:'runtime-manifests',error:error.message});return{elementCount:0,loadedImages:0,errors:loadErrors};});
  return ready;
}

export async function prepareMapArt(source,{retry=false}={}){
  if(retry&&!byElement.size){ready=null;loadErrors=[];}
  await loadMapArt();
  if(!byElement.size)throw new Error('地图美术目录未能读取，请重试。');
  const list=sourceMapDrawList(source);activeMapId=source.id;activeFiles=new Set(list.commands.map(command=>command.file));discardIdleImages();
  if(retry)for(const file of activeFiles)failedImages.delete(file);
  const results=await Promise.all([...activeFiles].map(ensureImage));
  return{...list,decoded:results.filter(Boolean).length,failed:results.filter(value=>!value).length};
}

export function paintSourceMap(ctx,source,{drawActorRows=null}={}){
  const list=sourceMapDrawList(source);
  if(activeMapId!==source.id){activeMapId=source.id;activeFiles=new Set(list.commands.map(command=>command.file));discardIdleImages();}
  let drawn=0,notDecoded=0;
  for(const command of list.commands){
    const image=images.get(command.file);if(!image){notDecoded++;void ensureImage(command.file);continue;}
    if(command.layer!==2&&drawActorRows)drawActorRows(command.sortY,false);
    ctx.drawImage(image,command.x,command.y,command.width,command.height);drawn++;
  }
  if(drawActorRows)drawActorRows(Infinity,true);
  return{drawn,notDecoded,failedFiles:[...new Set(list.commands.map(command=>command.file))].filter(file=>failedImages.has(file)),missingElementIds:list.missingElementIds,placement:list.placement,loadErrors};
}
