import test from 'node:test';
import assert from 'node:assert/strict';
import {spawnSync} from 'node:child_process';
import {fileURLToPath} from 'node:url';
import {createHash} from 'node:crypto';
import {readFile, readdir} from 'node:fs/promises';

const staticReaderPath = fileURLToPath(new URL('../scripts/export-reference-map-data.py', import.meta.url));
const python = process.env.PYTHON ?? 'python';
const pythonAvailable = !spawnSync(python, ['--version'], {encoding: 'utf8'}).error;

function staticParse(kind, source) {
  const wrapper = [
    'import importlib.util,json,sys',
    'spec=importlib.util.spec_from_file_location("our_static_reader",sys.argv[1])',
    'module=importlib.util.module_from_spec(spec)',
    'spec.loader.exec_module(module)', // Only our locally authored reader is imported.
    'try:',
    ' value=getattr(module,"parse_"+sys.argv[2]+"_text")(sys.argv[3])',
    ' print(json.dumps({"ok":True,"value":value},ensure_ascii=True))',
    'except Exception as error:',
    ' print(json.dumps({"ok":False,"error":type(error).__name__,"message":str(error)},ensure_ascii=True))',
  ].join('\n');
  const result = spawnSync(python, ['-B', '-c', wrapper, staticReaderPath, kind, source], {encoding: 'utf8'});
  assert.equal(result.status, 0, result.stderr);
  return JSON.parse(result.stdout);
}

test('static catalog reader preserves ordered Chinese literal fields without importing inspected files', {skip: !pythonAvailable && 'Python is required only for offline reference export'}, () => {
  const result = staticParse('catalog', "mapDesc=[(77,'example','人工测试',4,2,8,'artificial.map','preview.img','music.ogg',0,'',1,3)]");
  assert.equal(result.ok, true, result.message);
  assert.equal(result.value.entryCount, 1);
  assert.equal(result.value.entries[0].name, '人工测试');
  assert.deepEqual(result.value.entries[0].rawFields, [77, 'example', '人工测试', 4, 2, 8, 'artificial.map', 'preview.img', 'music.ogg', 0, '', 1, 3]);
  assert.equal(result.value.entries[0].field12, 3);
});

test('static element reader resolves literal inheritance and registry names without constructing classes', {skip: !pythonAvailable && 'Python is required only for offline reference export'}, () => {
  const source = [
    'class Base:',
    ' size=(2,1)',
    ' offset=(-2,10)',
    ' GridAttr=(15,0)',
    ' LifeTime=-1',
    'class Artificial(Base):',
    ' imageID=77',
    ' LifeTime=2',
    'qqtMapElems={77:Artificial}',
  ].join('\n');
  const result = staticParse('elements', source);
  assert.equal(result.ok, true, result.message);
  assert.equal(result.value.elements[0].properties.LifeTime, 2);
  assert.equal(result.value.elements[0].declared.offset, undefined);
  assert.deepEqual(result.value.elements[0].imageOffset, [-2, 10]);
  assert.deepEqual(result.value.elements[0].gridAttr, [15, 0]);
  assert.deepEqual([result.value.elements[0].widthCells, result.value.elements[0].heightCells], [2, 1]);
  assert.deepEqual(result.value.validationIssues, []);
});

test('calls, imports, methods, decorators, unresolved bases and executable registry expressions are rejected as data', {skip: !pythonAvailable && 'Python is required only for offline reference export'}, () => {
  const validClass = 'class Artificial:\n size=(1,1)\n offset=(0,0)\n GridAttr=(0,)\n imageID=1\n';
  for (const source of [
    'import os\n' + validClass + 'qqtMapElems={1:Artificial}',
    'class Artificial:\n def __init__(self):\n  raise RuntimeError("must never run")\nqqtMapElems={1:Artificial}',
    '@print("must never run")\n' + validClass + 'qqtMapElems={1:Artificial}',
    'class Artificial(Unknown):\n imageID=1\nqqtMapElems={1:Artificial}',
    validClass + 'qqtMapElems={1:Artificial()}',
    validClass.replace('imageID=1', 'imageID=print("must never run")') + 'qqtMapElems={1:Artificial}',
  ]) assert.equal(staticParse('elements', source).ok, false, source);
  assert.equal(staticParse('catalog', 'mapDesc=print("must never run")').ok, false);
  assert.equal(staticParse('catalog', "mapDesc=[(1,'x','x',1,1,1,'../escape.map','','',0,'',1,0)]").ok, false);
});

test('exported reference index identifies every JSON by hash and preserves catalog/header disagreement explicitly', async () => {
  const directory = new URL('../references/qqtang-map-data/', import.meta.url);
  let index;
  try { index = JSON.parse(await readFile(new URL('index.json', directory), 'utf8')); }
  catch (error) { if (error.code === 'ENOENT') return; throw error; }
  const files = (await readdir(new URL('maps/', directory))).filter(name => name.endsWith('.json'));
  assert.equal(index.mapCount, 377);
  assert.equal(files.length, index.mapCount);
  assert.equal(index.rejectedMapCount, 0);
  assert.equal(index.source.sourceType, 'community-patched-client-data');
  assert.equal(index.source.officialOriginalAuthenticity, 'unverified');
  assert.equal(index.map1601Md5Check.matches, true);
  let mismatches = 0;
  for (const entry of index.maps) {
    const bytes = await readFile(new URL(entry.jsonFile, directory));
    assert.equal(createHash('sha256').update(bytes).digest('hex'), entry.exportedJsonSha256, entry.fileName);
    const map = JSON.parse(bytes);
    assert.equal(map.source.sha256, entry.sha256);
    assert.equal(map.source.md5, entry.md5);
    assert.equal(map.source.archiveSha256, index.source.archiveSha256);
    assert.equal(map.validation.extractionHashMatched, true);
    assert.equal(map.parsedByteLength, map.source.byteLength);
    assert.equal(map.trailingByteLength, 0);
    assert.equal(map.layers.length, 3);
    for (const layer of map.layers) assert.equal(layer.values.length, map.header.width * map.header.height);
    // Independent reconstruction proves that JSON retains every inspected byte,
    // including unknown header data, signed markers and exact float32 bit patterns.
    // The reconstructed bytes are hashed in memory and never installed as assets.
    const reconstructed = Buffer.alloc(map.source.byteLength);
    reconstructed.writeUInt32LE(map.header.version, 0);
    reconstructed.writeUInt32LE(map.header.nativeRule, 4);
    Buffer.from(map.header.unknownWordAt8.rawHex, 'hex').copy(reconstructed, 8);
    if (map.header.version === 4) {
      reconstructed.writeUInt32LE(map.header.width, 12);
      reconstructed.writeUInt32LE(map.header.height, 16);
    }
    for (const layer of map.layers) layer.values.forEach((value, cell) => reconstructed.writeInt32LE(value, layer.offset + cell * 4));
    const wall = map.tables.wallItems;
    reconstructed.writeUInt32LE(wall.count, wall.offset);
    for (const item of wall.entries) {
      reconstructed.writeUInt32LE(item.sceneID, item.offset);
      reconstructed.writeUInt32LE(item.minimum, item.offset + 4);
      reconstructed.writeUInt32LE(item.maximum, item.offset + 8);
      reconstructed.writeUInt32LE(item.probabilityBits, item.offset + 12);
    }
    for (const name of ['hiddenItems', 'spawnGroupA', 'spawnGroupB', 'objectives']) {
      const table = map.tables[name];
      reconstructed.writeUInt32LE(table.count, table.offset);
      for (const cell of table.entries) {
        reconstructed.writeUInt16LE(cell.row, cell.offset);
        reconstructed.writeUInt16LE(cell.col, cell.offset + 2);
      }
    }
    assert.equal(createHash('sha256').update(reconstructed).digest('hex'), entry.sha256, `${entry.fileName} exact-byte reconstruction`);
    assert.equal(createHash('md5').update(reconstructed).digest('hex'), entry.md5, `${entry.fileName} MD5 reconstruction`);
    if (map.catalogEntries.some(catalog => !catalog.dimensionsMatchHeader)) mismatches++;
  }
  assert.equal(mismatches, 50);
  assert.equal(mismatches, index.catalogDimensionMismatchCount);
});
