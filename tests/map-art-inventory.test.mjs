import test from 'node:test';
import assert from 'node:assert/strict';
import {readFile,readdir} from 'node:fs/promises';
import {createHash} from 'node:crypto';

const root=new URL('../',import.meta.url);
const read=path=>readFile(new URL(path,root));
const hash=bytes=>createHash('sha256').update(bytes).digest('hex');

test('721-element art inventory distinguishes source references, original candidates and pending production',async()=>{
  const index=JSON.parse(await read('assets/maps/production-index.json'));
  assert.deepEqual(index,JSON.parse(await read('references/qqtang-map-data/visual-reference/families/index.json')));
  const original=JSON.parse(await read('references/qqtang-map-data/elements.json'));
  assert.equal(index.elements.length,721);
  assert.deepEqual(new Set(index.elements.map(item=>item.elementId)),new Set(original.elements.map(item=>item.id)));
  assert.equal(index.summary.acceptedCount,0);
  let candidates=0,pending=0;
  for(const entry of index.elements){
    const raw=original.elements.find(item=>item.id===entry.elementId);
    assert.deepEqual(entry.footprintCells,[raw.widthCells,raw.heightCells]);
    assert.deepEqual(entry.gridAttr,raw.gridAttr);
    assert.deepEqual(entry.mapElemOffsetRaw,raw.imageOffset);
    assert.match(entry.familyMappingStatus,/candidate/);
    assert.equal(entry.referenceOnly,true);
    if(entry.runtimeOriginalArt){
      candidates++;const art=entry.runtimeOriginalArt;
      assert.equal(hash(await read(art.file)),art.sha256);
      const provenance=JSON.parse(await read(art.provenanceRecord));
      assert.equal(provenance.elementId,entry.elementId);
      assert.equal(art.geometryAccepted,false);
      assert.equal(entry.productionStatus,'painted-candidate-awaiting-validation');
    }else{pending++;assert.equal(entry.productionStatus,'pending');}
  }
  assert.equal(candidates,index.summary.paintedCandidateCount);
  assert.equal(pending,index.summary.pendingCount);
  assert.equal(candidates+pending,721);
});

test('source PNGs are deduplicated, native-size, reference-only and fully indexed',async()=>{
  const index=JSON.parse(await read('assets/maps/production-index.json'));
  const seen=new Set(),familyFiles=new Set();
  for(const group of index.visualGroups){
    assert.equal(seen.has(group.visibleContentSha256),false);seen.add(group.visibleContentSha256);
    assert.ok(group.file.startsWith('references/qqtang-map-data/visual-reference/'));
    const bytes=await read(group.file);
    assert.equal(hash(bytes),group.sha256);
    assert.equal(bytes.subarray(0,8).toString('hex'),'89504e470d0a1a0a');
    assert.deepEqual([bytes.readUInt32BE(16),bytes.readUInt32BE(20)],group.nativeFrameSize);
    assert.equal(bytes[25],6,'retained frames carry true RGBA alpha');
    if(!group.reusedExistingReference)familyFiles.add(group.file);
    for(const id of group.elementIds){const element=index.elements.find(item=>item.elementId===id);assert.equal(element.visualGroupId,group.id);assert.equal(element.referencePng.file,group.file);}
  }
  assert.equal(seen.size,index.summary.uniqueVisiblePictureCount);
  const onDisk=new Set();
  for(const family of index.families){
    const relative=`references/qqtang-map-data/visual-reference/families/${family.family}/frames/`;
    let names;try{names=await readdir(new URL(relative,root));}catch(error){if(error.code==='ENOENT')continue;throw error;}
    for(const name of names)if(name.endsWith('.png'))onDisk.add(relative+name);
  }
  assert.deepEqual(onDisk,familyFiles,'no unindexed duplicate native PNG remains');
  for(const family of index.families){
    assert.ok(family.contactSheet.representatives.length<=24);
    assert.equal(hash(await read(family.contactSheet.file)),family.contactSheet.sha256);
    assert.equal(family.contactSheet.notRuntimeArt,true);
  }
});
