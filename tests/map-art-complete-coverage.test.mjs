import test from 'node:test';
import assert from 'node:assert/strict';
import {readFile} from 'node:fs/promises';
import {createHash} from 'node:crypto';
import {mergeSourceMapElements} from '../src/source-map-elements.js';
import {compileOriginalMap} from '../src/original-maps.js';
import {createMapArtCatalog,sourceMapDrawList} from '../src/map-art.js';
import {loadMapCatalog} from '../server/map-catalog.mjs';
const root=new URL('../',import.meta.url),read=p=>readFile(new URL(p,root)),hash=b=>createHash('sha256').update(b).digest('hex');
const baseBytes=await read('references/qqtang-map-data/elements.json'),base=JSON.parse(baseBytes),supplement=JSON.parse(await read('assets/maps/source-elements-supplement.json'));
const options={baseCatalogSha256:hash(baseBytes)};

test('explicit52 supplement rejects conflicts, changed source fields and false unknown flags',async()=>{
  const authorityBytes=await read(supplement.source.file),authority=JSON.parse(authorityBytes);
  assert.equal(hash(authorityBytes),supplement.source.sha256);
  const authorityRows=new Map(authority.records.map(row=>[row.id,row]));
  for(const element of supplement.elements)assert.deepEqual(element.binaryPropertyRecord,authorityRows.get(element.id));
  const merged=mergeSourceMapElements(base,supplement,options);assert.equal(merged.elements.length,773);
  assert.deepEqual(merged.elements.slice(0,721),base.elements);
  for(const extra of merged.elements.slice(721)){assert.equal(extra.properties.canDoSpecial,null);assert.equal(extra.properties.canHide,null);}
  const duplicate=structuredClone(supplement);duplicate.elements[0].id=base.elements[0].id;
  assert.throws(()=>mergeSourceMapElements(base,duplicate,options),/conflicts/);
  const changed=structuredClone(supplement);changed.elements[0].imageOffset[0]++;
  assert.throws(()=>mergeSourceMapElements(base,changed,options),/geometry/);
  const guessed=structuredClone(supplement);guessed.elements[0].properties.canHide=false;
  assert.throws(()=>mergeSourceMapElements(base,guessed,options),/unknown/);
  assert.throws(()=>mergeSourceMapElements(base,supplement,{baseCatalogSha256:'changed'}),/SHA/);
});

test('all377 source files have exact first-frame mappings and unchanged source JSON hashes',async()=>{
  const coverage=JSON.parse(await read('assets/maps/scene-art-coverage.json')),index=JSON.parse(await read('references/qqtang-map-data/index.json'));
  const sourceFiles=new Map(index.maps.map(x=>[x.fileName,x]));assert.equal(coverage.maps.length,377);
  for(const row of coverage.maps){
    const bytes=await read(row.sourceJson),raw=JSON.parse(bytes);assert.equal(hash(bytes),row.sourceJsonSha256);assert.equal(hash(bytes),sourceFiles.get(row.file).exportedJsonSha256);
    assert.deepEqual(row.usedElementIds,[...new Set(raw.layers.flatMap(l=>l.values.filter(v=>v>0)))].sort((a,b)=>a-b));
    assert.deepEqual(row.missingCandidateIds,[]);assert.deepEqual(row.missingDefinitionIds,[]);
  }
});

test('runtime registers773 paintings, preserves every prior projection and keeps unsupported rules closed',async()=>{
  const directory=await loadMapCatalog(),registry=JSON.parse(await read('assets/maps/runtime-manifests.json'));
  const manifests=await Promise.all(registry.manifests.map(async p=>JSON.parse(await read(p))));const art=createMapArtCatalog(manifests);assert.equal(art.size,773);
  const index=JSON.parse(await read('references/qqtang-map-data/index.json')),catalog=JSON.parse(await read('references/qqtang-map-data/catalog.json'));const files=new Map(index.maps.map(x=>[x.fileName,x])),raws=new Map();let oldComparable=0,recovered=0;
  for(const entry of catalog.entries){
    const file=files.get(entry.mapFileName);if(!file)continue;
    let raw=raws.get(file.jsonFile);if(!raw){raw=JSON.parse(await read('references/qqtang-map-data/'+file.jsonFile));raws.set(file.jsonFile,raw);}
    const current=directory.getRuntime('source-'+entry.id);let legacy;
    try{legacy=compileOriginalMap(raw,base,{catalogEntry:entry,id:'source-'+entry.id});}
    catch(error){if(error.code==='SOURCE_UNKNOWN_ELEMENT'){recovered++;assert.ok(current);assert.deepEqual(current.playableModes,[]);}continue;}
    assert.ok(current);for(const key of ['width','height','layers','sceneObjects','collision','spawnGroups','targets','pixelDimensions'])assert.deepEqual(current[key],legacy[key]);oldComparable++;
    if(current.nativeRule!==1)assert.deepEqual(current.playableModes,[]);
  }
  assert.equal(oldComparable,352);assert.equal(recovered,22);
  for(const descriptor of directory.maps){const current=directory.getRuntime(descriptor.id);if(!current)continue;const draw=sourceMapDrawList(current,art);assert.deepEqual(draw.missingElementIds,[]);assert.equal(draw.commands.length,current.sceneObjects.length);assert.equal(descriptor.artCoverage.accepted,false);}
});

test('refresh and legacy maintenance entry cannot regress the pinned773 inventory',async()=>{
  const {spawnSync}=await import('node:child_process');
  const before=await read('assets/maps/production-index.json'),legacy=await read('references/qqtang-map-data/visual-reference/families/index.json');
  for(const script of ['scripts/refresh-map-art-coverage.py','scripts/build-map-art-inventory.py']){
    const result=spawnSync(process.env.PYTHON??'python',['-B',script],{cwd:new URL('../',import.meta.url),encoding:'utf8'});
    assert.equal(result.status,0,result.stderr);const receipt=JSON.parse(result.stdout);assert.equal(receipt.definitions,773);assert.equal(receipt.unchanged,true);
    assert.deepEqual(await read('assets/maps/production-index.json'),before);
    assert.deepEqual(await read('references/qqtang-map-data/visual-reference/families/index.json'),legacy);
  }
});
