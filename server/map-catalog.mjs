import {readFile} from 'node:fs/promises';
import {createHash} from 'node:crypto';
import {compileOriginalMap,SOURCE_MAP_EVIDENCE} from '../src/original-maps.js';

const REFERENCE_ROOT=new URL('../references/qqtang-map-data/',import.meta.url);
export const DRAFT_MAPS=Object.freeze([
  {id:'courtyard',name:'庭院 · 自定义技术试稿',width:15,height:13,maxSeats:8,kind:'draft-map',playableModes:['classic','brawl','bun','soccer','push','adventure'],geometryStatus:'unaccepted-custom-draft',playable:true},
  {id:'town',name:'街区 · 自定义技术试稿',width:15,height:13,maxSeats:8,kind:'draft-map',playableModes:['classic','brawl','bun','soccer','push','adventure'],geometryStatus:'unaccepted-custom-draft',playable:true},
  {id:'factory',name:'工场 · 自定义技术试稿',width:15,height:13,maxSeats:8,kind:'draft-map',playableModes:['classic','brawl','bun','soccer','push','adventure'],geometryStatus:'unaccepted-custom-draft',playable:true},
]);
const hash=bytes=>createHash('sha256').update(bytes).digest('hex');
function parse(bytes,label){try{return JSON.parse(bytes.toString('utf8'));}catch{throw new Error(`地图目录JSON无效：${label}`);}}
async function currentPaintedElements(){
  const project=new URL('../',import.meta.url),ids=new Set();
  const directory=parse(await readFile(new URL('assets/maps/runtime-manifests.json',project)),'art-directory');
  for(const file of directory.manifests){
    if(!/^assets\/maps\/[a-z-]+\/art\.json$/.test(file))throw new Error('美术清单路径无效');
    const manifest=parse(await readFile(new URL(file,project)),file);
    for(const piece of manifest.pieces){
      if(!/^assets\/maps\/[a-z-]+\/pieces\/[a-zA-Z0-9_-]+\.png$/.test(piece.file))throw new Error('美术资源路径无效');
      const bytes=await readFile(new URL(piece.file,project));
      if(hash(bytes)!==piece.sha256)throw new Error(`美术文件哈希与清单不符：${piece.file}`);
      ids.add(piece.elementId);
    }
  }
  return ids;
}

/** Loads local exported JSON only. Never loads inspected Python/native code. */
export async function loadMapCatalog({referenceRoot=REFERENCE_ROOT}={}){
  const read=async relative=>readFile(new URL(relative,referenceRoot));
  const[indexBytes,catalogBytes,elementsBytes,paintedIds]=await Promise.all([...['index.json','catalog.json','elements.json'].map(read),currentPaintedElements()]);
  const index=parse(indexBytes,'index'),catalog=parse(catalogBytes,'catalog'),elements=parse(elementsBytes,'elements');
  const files=new Map(index.maps.map(item=>[item.fileName,item])),runtime=new Map(),descriptors=[];
  const bytesByFile=new Map();
  for(const entry of catalog.entries){
    const id=`source-${entry.id}`,source=files.get(entry.mapFileName);
    const descriptor={id,catalogId:entry.id,name:entry.name,family:entry.family,kind:'source-map',
      mapFileName:entry.mapFileName,width:source?.width??null,height:source?.height??null,
      catalogWidth:entry.catalogWidth,catalogHeight:entry.catalogHeight,maxSeats:entry.playerLimit,
      nativeRule:source?.nativeRule??null,sourceSha256:source?.sha256??null,
      sourceType:'community-patched-client-data',officialOriginalAuthenticity:'unverified',
      geometryStatus:'source-data-exact-projection-candidate',playable:false,playableModes:[],
      projectionStatus:SOURCE_MAP_EVIDENCE.status,catalogDimensionsMatch:source?source.width===entry.catalogWidth&&source.height===entry.catalogHeight:null};
    try{
      if(!source)throw Object.assign(new Error('目录对应.map文件缺失。'),{code:'SOURCE_FILE_MISSING'});
      if(!/^maps\/[a-zA-Z0-9_-]+\.json$/.test(source.jsonFile))throw new Error('索引路径格式无效。');
      let raw=bytesByFile.get(source.jsonFile);
      if(!raw){
        const bytes=await read(source.jsonFile);
        if(hash(bytes)!==source.exportedJsonSha256)throw Object.assign(new Error('导出JSON哈希与索引不符。'),{code:'SOURCE_HASH_MISMATCH'});
        raw=parse(bytes,source.jsonFile);
        if(raw.source.sha256!==source.sha256||raw.header.width!==source.width||raw.header.height!==source.height)throw new Error('地图头/来源与索引不符。');
        bytesByFile.set(source.jsonFile,raw);
      }
      const compiled=compileOriginalMap(raw,elements,{catalogEntry:entry,id});
      const required=[...new Set(compiled.sceneObjects.map(object=>object.elementId))];
      const missing=required.filter(elementId=>!paintedIds.has(elementId));
      descriptor.artCoverage={requiredCount:required.length,paintedCandidateCount:required.length-missing.length,missingCount:missing.length,
        missingElementIds:missing,status:missing.length?'painted-art-incomplete':'painted-candidates-awaiting-validation',accepted:false};
      descriptor.playableModes=compiled.playableModes;descriptor.playable=compiled.playableModes.length>0;
      descriptor.spawnCounts={A:compiled.spawnGroups.A.length,B:compiled.spawnGroups.B.length};
      descriptor.targetCount=compiled.targets.length;
      if(!descriptor.playable){descriptor.unavailableCode='SOURCE_RULE_UNSUPPORTED';descriptor.unavailableReason=`原生规则${compiled.nativeRule}尚未由本引擎核验支持。`;}
      runtime.set(id,compiled);
    }catch(error){descriptor.unavailableCode=error.code||'SOURCE_MAP_REJECTED';descriptor.unavailableReason=error.message;}
    descriptors.push(descriptor);
  }
  descriptors.sort((a,b)=>a.catalogId-b.catalogId);
  const sources=new Map(descriptors.map(item=>[item.id,item])),drafts=new Map(DRAFT_MAPS.map(item=>[item.id,{...item}]));
  return{
    source:{...index.source,indexSha256:hash(indexBytes),catalogSha256:hash(catalogBytes),elementsSha256:hash(elementsBytes)},
    maps:descriptors,draftMaps:DRAFT_MAPS.map(item=>({...item})),
    get(id){return sources.get(String(id))||drafts.get(String(id))||null;},
    getRuntime(id){const map=runtime.get(String(id));return map?structuredClone(map):null;},
    publicDirectory(){return{maps:descriptors,draftMaps:DRAFT_MAPS,source:this.source,projectionEvidence:SOURCE_MAP_EVIDENCE};},
  };
}
