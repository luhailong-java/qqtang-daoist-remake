import test from 'node:test';
import assert from 'node:assert/strict';
import {readFile} from 'node:fs/promises';
import {createMapArtCatalog,sourceMapDrawList,MAP_ART_PLACEMENT} from '../src/map-art.js';
import {loadMapCatalog} from '../server/map-catalog.mjs';

test('China Town 01 has painted candidates for every source object, preserving all footprints',async()=>{
  const art=JSON.parse(await readFile(new URL('../assets/maps/town/art.json',import.meta.url)));
  const source=(await loadMapCatalog()).getRuntime('source-201');
  const before=JSON.stringify(source),result=sourceMapDrawList(source,createMapArtCatalog([art]));
  assert.deepEqual(result.missingElementIds,[]);
  assert.equal(result.commands.length,source.sceneObjects.length);
  const shop=source.sceneObjects.find(object=>object.elementId===3019);
  const command=result.commands.find(item=>item.instanceId===shop.id);
  assert.deepEqual(command.footprint,{x:shop.x,y:shop.y,width:4,height:2});
  assert.deepEqual([command.width,command.height],[161,110]);
  assert.deepEqual([command.x,command.y],[shop.x*40-shop.imageOffset[0],shop.y*40-shop.imageOffset[1]]);
  assert.equal(JSON.stringify(source),before,'painting must not mutate geometry or collision');
  assert.ok(result.commands.every(item=>item.geometryAccepted===false));
  assert.equal(MAP_ART_PLACEMENT.geometryAccepted,false);
  const firstObject=result.commands.findIndex(item=>item.layer!==2);
  assert.ok(result.commands.slice(0,firstObject).every(item=>item.layer===2));
});

test('missing art stays missing and destroyed instances vanish without a generic replacement',()=>{
  const piece={elementId:7,file:'new.png',worldFrameWidth:43,worldFrameHeight:58};
  const catalog=createMapArtCatalog([{tilePixels:40,pieces:[piece]}]);
  const object={id:'a',elementId:7,layer:1,x:2,y:3,width:1,height:1,imageOffset:[3,17]};
  const source={kind:'source-map',sceneObjects:[object,{...object,id:'b',elementId:999},{...object,id:'c',destroyed:true}]};
  const result=sourceMapDrawList(source,catalog);
  assert.deepEqual(result.missingElementIds,[999]);assert.equal(result.commands.length,1);
  assert.deepEqual([result.commands[0].x,result.commands[0].y],[77,103]);
  assert.throws(()=>sourceMapDrawList({...source,sceneObjects:[{...object,imageOffset:null}]},catalog),/偏移/);
});
