/** Data-only source-map adapter. The projection follows one pinned community
 * reverse-engineered implementation and remains a CANDIDATE, not Tencent proof.
 * No source script is imported/executed. Layer2 is retained for rendering;
 * collision uses layer0/1 anchors, full size/GridAttr and last-writer ordering.
 */
export const SOURCE_MAP_EVIDENCE=Object.freeze({
  commit:'4b3a245fd985cabd4abd68ade6c282cc163d9edb',
  projection:'https://github.com/kuuhaku1314/qqtang/blob/4b3a245fd985cabd4abd68ade6c282cc163d9edb/internal/game/mapdata/competitive_battlefield.go#L201-L304',
  directionalBits:'https://github.com/kuuhaku1314/qqtang/blob/4b3a245fd985cabd4abd68ade6c282cc163d9edb/internal/game/battleengine/types.go#L138-L177',
  status:'candidate-community-projection',officialOriginalAuthenticity:'unverified',
  footprintOrigin:'positive anchor + local column/row; last writer in layer/row-major order',
  collisionLayers:[0,1],retainedLayers:[0,1,2],
  playerBits:{right:8,up:4,left:2,down:1},flameBitShift:8,
  logicalCellPixels:40,logicalCellPixelsStatus:'community-implementation-unverified-against-original',
});

export class SourceMapError extends Error{
  constructor(code,message,details={}){super(message);this.name='SourceMapError';this.code=code;this.details=details;}
}
function check(value,code,message,details){if(!value)throw new SourceMapError(code,message,details);}
const clone=value=>value===undefined?null:JSON.parse(JSON.stringify(value));
export const traversalBit=(dx,dy)=>dx===1&&dy===0?8:dx===-1&&dy===0?2:dx===0&&dy===-1?4:dx===0&&dy===1?1:0;
export function projectSourceCollision(map){
  const {width,height}=map;
  const cells=Array.from({length:width*height},()=>({gridAttr:0x0f0f,exitAttr:15,occupied:false,instanceId:null,durability:0}));
  for(const object of map.sceneObjects){
    if(object.layer>1||object.destroyed)continue;
    for(let localY=0;localY<object.height;localY++)for(let localX=0;localX<object.width;localX++){
      const index=(object.y+localY)*width+object.x+localX,attr=object.gridAttrs[localY*object.width+localX],previous=cells[index];
      cells[index]={gridAttr:attr,exitAttr:object.layer===0?attr:previous.exitAttr,occupied:true,
        instanceId:object.id,elementId:object.elementId,anchor:{x:object.x,y:object.y},
        durability:Math.max(0,object.lifeTime),canMove:object.canMove,
        width:object.width,height:object.height};
    }
  }
  return {cells,grid:Array.from({length:height},(_,y)=>Array.from({length:width},(_,x)=>{
    const cell=cells[y*width+x];return cell.gridAttr&15?0:cell.durability>0?2:1;
  }))};
}

/** Reject unknown elements and invalid footprints rather than inventing walls. */
export function compileOriginalMap(raw,elementCatalog,{catalogEntry=null,id=null,name=null}={}){
  check(raw&&raw.header&&Array.isArray(raw.layers),'SOURCE_SCHEMA','地图数据结构不完整。');
  const {width,height}=raw.header;
  check(Number.isInteger(width)&&Number.isInteger(height)&&width>0&&height>0&&width<=256&&height<=256,'SOURCE_DIMENSIONS','地图文件头宽高无效。');
  check(raw.layers.length===3,'SOURCE_LAYERS','原数据必须恰有三层。');
  const elements=Array.isArray(elementCatalog)?elementCatalog:elementCatalog?.elements;
  check(Array.isArray(elements),'SOURCE_ELEMENTS','缺少元素字典。');
  const byId=new Map(elements.map(item=>[item.id,item])),used=new Set(),objects=[];
  for(let layer=0;layer<3;layer++){
    const values=raw.layers[layer].values;
    check(Array.isArray(values)&&values.length===width*height&&values.every(Number.isInteger),'SOURCE_LAYERS','图层格值数量与文件头不匹配。',{layer});
    for(let index=0;index<values.length;index++){
      const value=values[index];if(value<=0)continue;
      const element=byId.get(value);check(element,'SOURCE_UNKNOWN_ELEMENT',`地图引用未定义元素 ${value}，已停止导入。`,{layer,index,elementId:value});
      const w=element.widthCells,h=element.heightCells,attrs=element.gridAttr;
      check(Number.isInteger(w)&&w>0&&Number.isInteger(h)&&h>0&&Array.isArray(attrs)&&attrs.length===w*h&&attrs.every(attr=>Number.isInteger(attr)&&attr>=0&&attr<=0xffffffff),'SOURCE_ELEMENT_SCHEMA',`元素${value}的size/GridAttr不完整。`);
      const x=index%width,y=Math.floor(index/width);
      check(x+w<=width&&y+h<=height,'SOURCE_FOOTPRINT_BOUNDS',`元素${value}的${w}×${h}占地超出地图。`,{layer,x,y,w,h});
      const life=element.properties?.LifeTime,canMove=element.properties?.canMove;
      check(Number.isInteger(life)&&Number.isInteger(canMove),'SOURCE_ELEMENT_SCHEMA',`元素${value}缺少LifeTime/canMove。`);
      objects.push({id:`layer-${layer}-anchor-${index}`,layer,elementId:value,x,y,width:w,height:h,
        gridAttrs:[...attrs],lifeTime:life,canMove,imageOffset:clone(element.imageOffset),properties:clone(element.properties),destroyed:false});
      used.add(value);
    }
  }
  const tables=clone(raw.tables),coordinates=section=>{
    const entries=tables?.[section]?.entries;check(Array.isArray(entries),'SOURCE_COORDINATES',`缺少${section}坐标表。`);
    const seen=new Set();return entries.map(cell=>{
      check(Number.isInteger(cell.row)&&Number.isInteger(cell.col)&&cell.row>=0&&cell.col>=0&&cell.row<height&&cell.col<width,'SOURCE_COORDINATES',`${section}坐标超界。`);
      const identity=cell.row*width+cell.col;check(!seen.has(identity),'SOURCE_COORDINATES',`${section}重复坐标。`);seen.add(identity);return{x:cell.col,y:cell.row};
    });
  };
  const spawnGroups={A:coordinates('spawnGroupA'),B:coordinates('spawnGroupB')},targets=coordinates('objectives');
  const entry=catalogEntry||raw.catalogEntries?.[0]||null;
  const declaredLimit=entry?.playerLimit;
  check(Number.isInteger(declaredLimit)&&declaredLimit>0&&declaredLimit<=8,'SOURCE_PLAYER_LIMIT','缺少可核验的地图人数上限。');
  const map={kind:'source-map',id:id||`source-${entry.id}`,catalogId:entry.id,name:name||entry.name,
    width,height,playerLimit:declaredLimit,nativeRule:raw.header.nativeRule,version:raw.header.version,
    dimensionSource:raw.header.dimensionSource,source:clone(raw.source),catalogEntry:clone(entry),
    header:clone(raw.header),layers:clone(raw.layers),tables,spawnGroups,targets,
    elements:elements.filter(item=>used.has(item.id)).map(clone),sceneObjects:objects,
    projectionEvidence:clone(SOURCE_MAP_EVIDENCE),authenticity:'community-patched-client-unverified',
    geometryStatus:'source-data-exact-projection-candidate',
    pixelDimensions:{width:width*40,height:height*40,cellWidth:40,cellHeight:40,status:'candidate-community-40px-constant'},
    playableModes:raw.header.nativeRule===1?['classic']:[],
    runtimeLimitations:['格级候选投影；未实现原客户端像素碰撞/转角滑动和普通竞技原生推物细节','地图物品表原值保留，尚无原道具ID行为映射；不随机替代','原美术锚点与渲染偏移尚未验收','仅规则1普通竞技可在此引擎启动；其他规则保留数据但不冒用'],
  };
  const projected=projectSourceCollision(map);map.collision=projected.cells;map.grid=projected.grid;
  const spawns=[...spawnGroups.A,...spawnGroups.B];
  check(spawns.length>=declaredLimit,'SOURCE_SPAWNS','文件出生点少于目录人数上限。');
  for(const point of spawns)check(map.grid[point.y][point.x]===0,'SOURCE_SPAWN_BLOCKED','出生点在候选投影中不可通行，已拒绝启动。',point);
  check(new Set(spawns.map(point=>point.y*width+point.x)).size>=declaredLimit,'SOURCE_SPAWNS','去重后出生点不足。');
  return map;
}

export function canTraverseSource(map,fromX,fromY,toX,toY){
  const dx=toX-fromX,dy=toY-fromY,bit=traversalBit(dx,dy),reverse=traversalBit(-dx,-dy);
  if(!bit||fromX<0||fromY<0||toX<0||toY<0||fromX>=map.width||toX>=map.width||fromY>=map.height||toY>=map.height)return false;
  const from=map.collision[fromY*map.width+fromX],to=map.collision[toY*map.width+toX];
  return !!(from.exitAttr&reverse)&&!!(to.gridAttr&bit);
}
export function sourceFlameStep(map,fromX,fromY,toX,toY){
  const bit=traversalBit(toX-fromX,toY-fromY),reverse=traversalBit(fromX-toX,fromY-toY);
  if(!bit||toX<0||toY<0||toX>=map.width||toY>=map.height)return{enter:false,continue:false};
  const from=map.collision[fromY*map.width+fromX],to=map.collision[toY*map.width+toX];
  const leave=!!(from.gridAttr&(reverse<<8)),enter=leave&&(to.durability>0||!!(to.gridAttr&(bit<<8)));
  return{enter,continue:enter&&to.durability===0&&!!(to.gridAttr&(bit<<8))};
}
