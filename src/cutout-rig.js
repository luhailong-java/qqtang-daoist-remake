// Experimental painted-part animation. It consumes a pose/root and never updates gameplay.
const identity=()=>[1,0,0,1,0,0];
const finitePair=value=>Array.isArray(value)&&value.length===2&&value.every(Number.isFinite);
const safeFile=file=>typeof file==='string'&&/^assets\/[A-Za-z0-9_/-]+\.png$/.test(file)&&!file.includes('..');
export function multiplyMatrix(a,b){return[a[0]*b[0]+a[2]*b[1],a[1]*b[0]+a[3]*b[1],a[0]*b[2]+a[2]*b[3],a[1]*b[2]+a[3]*b[3],a[0]*b[4]+a[2]*b[5]+a[4],a[1]*b[4]+a[3]*b[5]+a[5]];}
export function transformPoint(matrix,point){return[matrix[0]*point[0]+matrix[2]*point[1]+matrix[4],matrix[1]*point[0]+matrix[3]*point[1]+matrix[5]];}
function rotation(degrees,x=0,y=0){const angle=degrees*Math.PI/180,c=Math.cos(angle),s=Math.sin(angle);return[c,s,-s,c,x,y];}
export function validateCutoutRig(rig){
  if(rig?.schemaVersion!==1||rig.animationSource!=='procedural_skeletal_animation')throw new Error('Unsupported painted-part rig schema');
  if(!finitePair(rig.designCanvas)||rig.designCanvas.some(v=>v<=0)||!finitePair(rig.referenceRoot))throw new Error('A measured design canvas and explicit candidate root are required');
  if(!['E','W','N','S'].includes(rig.direction)||!Array.isArray(rig.nodes)||!rig.nodes.length)throw new Error('A genuine direction and painted nodes are required');
  const byId=new Map();
  for(const node of rig.nodes){
    if(typeof node.id!=='string'||byId.has(node.id))throw new Error('Node identifiers must be unique');
    if(!safeFile(node.file)||!finitePair(node.pivot)||!finitePair(node.bindPosition))throw new Error(`Missing source, pivot or bind position: ${node.id}`);
    if(!Number.isFinite(node.imageScale)||node.imageScale<=0||!Number.isFinite(node.layer))throw new Error(`Invalid image scale or layer: ${node.id}`);
    if(node.bindRotationDegrees!==undefined&&!Number.isFinite(node.bindRotationDegrees)||node.imageRotationDegrees!==undefined&&!Number.isFinite(node.imageRotationDegrees))throw new Error('Non-finite bind angle');
    byId.set(node.id,node);
  }
  const complete=new Set(),visiting=new Set();
  function visit(id){if(complete.has(id))return;if(visiting.has(id))throw new Error('Cyclic rig parents');const node=byId.get(id);if(!node)throw new Error(`Missing parent: ${id}`);visiting.add(id);if(node.parent!==null&&node.parent!==undefined)visit(node.parent);visiting.delete(id);complete.add(id);}
  for(const id of byId.keys())visit(id);
  for(const action of Object.values(rig.actions||{}))for(const [id,track]of Object.entries(action.tracks||{})){
    if(!byId.has(id))throw new Error(`Unknown tracked node: ${id}`);
    for(const [name,channel]of Object.entries(track)){
      if(!['rotationDegrees','x','y'].includes(name))throw new Error('Unknown keyframe channel');
      if(!Array.isArray(channel)||!channel.length)throw new Error('Empty keyframe channel');
      let previous=-1;for(const key of channel){if(!Number.isFinite(key.at)||key.at<0||key.at>1||key.at<=previous||!Number.isFinite(key.value))throw new Error('Invalid ordered keyframe');previous=key.at;}
      if(action.loop&&(channel[0].at!==0||channel.at(-1).at!==1||channel[0].value!==channel.at(-1).value))throw new Error('Loop endpoints must close explicitly');
    }
  }
  return rig;
}
function sampleChannel(keys,phase){if(!keys)return 0;if(phase<=keys[0].at)return keys[0].value;for(let i=1;i<keys.length;i++)if(phase<=keys[i].at){const before=keys[i-1],after=keys[i],t=(phase-before.at)/(after.at-before.at),smooth=t*t*(3-2*t);return before.value+(after.value-before.value)*smooth;}return keys.at(-1).value;}
export function sampleCutoutPose(rig,{action='idle',phase=0,amplitude=1}={}){
  if(!Number.isFinite(phase)||!Number.isFinite(amplitude))throw new Error('Finite visual pose parameters required');
  const clip=rig.actions?.[action];if(!clip)return{};
  const progress=clip.loop?((phase%1)+1)%1:Math.max(0,Math.min(1,phase)),strength=Math.max(0,Math.min(1,amplitude)),pose={};
  for(const[id,track]of Object.entries(clip.tracks||{}))pose[id]={rotationDegrees:sampleChannel(track.rotationDegrees,progress)*strength,x:sampleChannel(track.x,progress)*strength,y:sampleChannel(track.y,progress)*strength};
  return pose;
}
export function cutoutMatrices(rig,pose={}){
  const nodes=new Map(rig.nodes.map(node=>[node.id,node])),matrices=new Map(),visiting=new Set();
  function resolve(id){if(matrices.has(id))return matrices.get(id);if(visiting.has(id))throw new Error('Cyclic pose graph');const node=nodes.get(id);if(!node)throw new Error('Missing pose parent');visiting.add(id);const delta=pose[id]||{},angle=(node.bindRotationDegrees??0)+(delta.rotationDegrees??0),dx=delta.x??0,dy=delta.y??0;if(![angle,dx,dy].every(Number.isFinite))throw new Error('Non-finite pose');const local=rotation(angle,node.bindPosition[0]+dx,node.bindPosition[1]+dy),parent=node.parent===null||node.parent===undefined?identity():resolve(node.parent);const matrix=multiplyMatrix(parent,local);visiting.delete(id);matrices.set(id,matrix);return matrix;}
  for(const id of nodes.keys())resolve(id);return matrices;
}
function imageMatrix(node,bone){const rotated=multiplyMatrix(bone,rotation(node.imageRotationDegrees||0));return multiplyMatrix(rotated,[node.imageScale,0,0,node.imageScale,-node.pivot[0]*node.imageScale,-node.pivot[1]*node.imageScale]);}
export function cutoutLandmarks(rig,pose={}){const matrices=cutoutMatrices(rig,pose),nodes=new Map(rig.nodes.map(node=>[node.id,node])),points={};for(const[name,landmark]of Object.entries(rig.landmarks||{})){const node=nodes.get(landmark.node);if(!node||!finitePair(landmark.point)||!['joint','image'].includes(landmark.space))throw new Error('Invalid explicit rig landmark');points[name]=transformPoint(landmark.space==='image'?imageMatrix(node,matrices.get(node.id)):matrices.get(node.id),landmark.point);}return points;}
export async function loadCutoutImages(rig){
  validateCutoutRig(rig);const files=[...new Set(rig.nodes.map(node=>node.file))],images=new Map();let cursor=0;
  async function worker(){while(cursor<files.length){const file=files[cursor++],image=new Image();image.decoding='async';image.src=file;await image.decode();if(!image.naturalWidth)throw new Error(`Empty painted part: ${file}`);images.set(file,image);}}
  await Promise.all(Array.from({length:Math.min(4,files.length)},worker));return images;
}
export function drawCutoutRig(ctx,rig,images,{root,size,pose={},allowCandidate=false,joints=false}={}){
  if(!allowCandidate||!finitePair(root)||!Number.isFinite(size)||size<=0)return false;
  if(rig.nodes.some(node=>!images.get(node.file)?.naturalWidth))return false;
  const matrices=cutoutMatrices(rig,pose),scale=size/rig.designCanvas[0];ctx.save();ctx.translate(root[0],root[1]);ctx.scale(scale,scale);ctx.translate(-rig.referenceRoot[0],-rig.referenceRoot[1]);
  for(const node of [...rig.nodes].sort((a,b)=>a.layer-b.layer)){ctx.save();ctx.transform(...imageMatrix(node,matrices.get(node.id)));ctx.drawImage(images.get(node.file),0,0);ctx.restore();}
  if(joints){ctx.lineWidth=1.5/scale;ctx.font=`${12/scale}px sans-serif`;for(const node of rig.nodes){const point=transformPoint(matrices.get(node.id),[0,0]);ctx.strokeStyle=node.anatomicalSide==='RIGHT'?'#cb4c34':'#248398';ctx.fillStyle=ctx.strokeStyle;if(node.parent){const parent=transformPoint(matrices.get(node.parent),[0,0]);ctx.beginPath();ctx.moveTo(...parent);ctx.lineTo(...point);ctx.stroke();}ctx.beginPath();ctx.arc(...point,3/scale,0,Math.PI*2);ctx.fill();ctx.fillText(node.id,point[0]+5/scale,point[1]);}}
  ctx.restore();return true;
}
