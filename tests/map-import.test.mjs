import test from 'node:test';
import assert from 'node:assert/strict';
import {mkdtemp, writeFile, mkdir, readFile, rm} from 'node:fs/promises';
import {tmpdir} from 'node:os';
import {join} from 'node:path';
import {spawnSync} from 'node:child_process';
import {fileURLToPath} from 'node:url';
import {parseOriginalMap, summarizeOriginalMap, inspectMapDirectory, MapParseError, MAX_SUPPORTED_MAP_BYTES} from '../scripts/inspect-original-map.mjs';

// All fixtures below are intentionally artificial byte streams. They are not
// Tencent maps, original-layout references or proof of original client behavior.
function fixture({version = 4, width = 4, height = 2, nativeRule = 1, walls = [], hidden = [], a = [], b = [], objectives = []} = {}) {
  if (version === 3) { width = 15; height = 13; }
  const chunks = [];
  const offsets = {};
  let length = 0;
  const append = (name, data) => { offsets[name] = length; chunks.push(data); length += data.length; };
  const header = Buffer.alloc(version === 4 ? 20 : 12);
  header.writeUInt32LE(version, 0);
  header.writeUInt32LE(nativeRule, 4);
  header.writeUInt32LE(0xa1b2c3d4, 8);
  if (version === 4) { header.writeUInt32LE(width, 12); header.writeUInt32LE(height, 16); }
  append('header', header);
  for (let layer = 0; layer < 3; layer++) {
    const bytes = Buffer.alloc(width * height * 4);
    for (let cell = 0; cell < width * height; cell++) bytes.writeInt32LE(layer * 1000 + cell, cell * 4);
    append(`layer${layer}`, bytes);
  }
  const wallData = Buffer.alloc(4 + walls.length * 16);
  wallData.writeUInt32LE(walls.length);
  walls.forEach((wall, index) => {
    const cursor = 4 + index * 16;
    wallData.writeUInt32LE(wall.sceneID, cursor);
    wallData.writeUInt32LE(wall.minimum, cursor + 4);
    wallData.writeUInt32LE(wall.maximum, cursor + 8);
    wallData.writeFloatLE(wall.probability, cursor + 12);
  });
  append('walls', wallData);
  for (const [name, cells] of Object.entries({hidden, a, b, objectives})) {
    const data = Buffer.alloc(4 + cells.length * 4);
    data.writeUInt32LE(cells.length);
    cells.forEach(([row, col], index) => { data.writeUInt16LE(row, 4 + index * 4); data.writeUInt16LE(col, 6 + index * 4); });
    append(name, data);
  }
  return {bytes: Buffer.concat(chunks), offsets};
}

function rejects(bytes, code, section) {
  assert.throws(() => parseOriginalMap(bytes), error => {
    assert.ok(error instanceof MapParseError);
    assert.equal(error.code, code);
    if (section) assert.equal(error.section, section);
    assert.ok(Number.isInteger(error.offset) && error.offset >= 0 && error.offset <= bytes.length);
    return true;
  });
}

test('artificial v3 preserves all layers, negative markers, unknown header bytes and ordered coordinate tables', () => {
  const {bytes, offsets} = fixture({version: 3,
    walls: [{sceneID: 42, minimum: 0, maximum: 7, probability: 0.5}],
    hidden: [[12, 14], [0, 0]], a: [[1, 2]], b: [[12, 14]], objectives: [[6, 7]],
  });
  bytes.writeInt32LE(-2147483648, offsets.layer0);
  bytes.writeInt32LE(-42, offsets.layer1 + 4);
  bytes.writeInt32LE(2147483647, offsets.layer2 + 194 * 4);
  const map = parseOriginalMap(bytes, {sourceName: 'artificial-v3.map'});
  assert.equal(map.header.version, 3);
  assert.deepEqual([map.header.width, map.header.height, map.header.byteLength], [15, 13, 12]);
  assert.equal(map.header.dimensionSource, 'community-v3-format-default');
  assert.deepEqual(map.header.unknownWordAt8, {offset: 8, rawHex: 'd4c3b2a1', uint32LE: 0xa1b2c3d4});
  assert.deepEqual(map.layers.map(layer => layer.values.length), [195, 195, 195]);
  assert.equal(map.layers[0].values[0], -2147483648);
  assert.equal(map.layers[1].values[1], -42);
  assert.equal(map.layers[2].values[194], 2147483647);
  assert.equal(map.tables.wallItems.entries[0].probabilityBits, 0x3f000000);
  assert.equal(map.tables.wallItems.entries[0].maximum, 7);
  assert.deepEqual(map.tables.hiddenItems.entries.map(({row, col}) => [row, col]), [[12, 14], [0, 0]]);
  assert.equal(map.tables.spawnGroupB.entries[0].row, 12);
  assert.equal(map.tables.objectives.entries[0].col, 7);
  assert.equal(map.parsedByteLength, bytes.length);
  assert.equal(map.source.name, 'artificial-v3.map');
  assert.equal(map.source.authenticity, 'not-established-by-parser');
  assert.equal(map.header.cellSizePixels, undefined);
  assert.equal(map.layers[0].collision, undefined);
});

test('artificial v4 uses nonsquare header geometry instead of assuming 15 × 13', () => {
  const {bytes} = fixture({width: 4, height: 2, hidden: [[1, 3]], a: [[1, 3]], objectives: [[0, 2]]});
  const map = parseOriginalMap(bytes);
  assert.deepEqual([map.header.width, map.header.height, map.header.byteLength], [4, 2, 20]);
  assert.equal(map.header.dimensionSource, 'v4-file-header');
  assert.deepEqual(map.layers[1].values, [1000, 1001, 1002, 1003, 1004, 1005, 1006, 1007]);
  assert.equal(map.layers[1].values[1 * map.header.width + 3], 1007);
  assert.deepEqual([map.tables.hiddenItems.entries[0].row, map.tables.hiddenItems.entries[0].col], [1, 3]);
  assert.equal(map.tables.hiddenItems.count, 1);
  assert.equal(map.tables.spawnGroupA.count, 1); // Same cell across tables is allowed.
  const summary = summarizeOriginalMap(map);
  assert.equal(summary.layers[0].entryCount, 8);
  assert.equal(summary.layers[0].values, undefined);
  assert.equal(summary.tables.objectives.count, 1);
});

test('fingerprints cover every input byte and a Uint8Array view respects its byte offset and length', () => {
  const {bytes} = fixture();
  const direct = parseOriginalMap(bytes);
  const padded = Buffer.concat([Buffer.from([0xff, 0xff]), bytes, Buffer.from([0xee])]);
  const view = new Uint8Array(padded.buffer, padded.byteOffset + 2, bytes.length);
  assert.deepEqual(parseOriginalMap(view).source, direct.source);
  const changed = Buffer.from(bytes);
  changed[8] ^= 1;
  assert.notEqual(parseOriginalMap(changed).source.sha256, direct.source.sha256);
  assert.notEqual(parseOriginalMap(changed).source.md5, direct.source.md5);
  assert.deepEqual(parseOriginalMap(changed).layers, direct.layers);
  assert.match(direct.source.sha256, /^[0-9a-f]{64}$/);
  assert.match(direct.source.md5, /^[0-9a-f]{32}$/);
  assert.throws(() => parseOriginalMap('not bytes'), TypeError);
});

test('every truncated prefix is rejected without returning a partial map or leaking native bounds errors', () => {
  const {bytes} = fixture({walls: [{sceneID: 9, minimum: 1, maximum: 2, probability: 1}], hidden: [[1, 2]], a: [[0, 0]], b: [[1, 3]], objectives: [[0, 3]]});
  for (let length = 0; length < bytes.length; length++) rejects(bytes.subarray(0, length), 'TRUNCATED');
});

test('unknown versions, zero rules, excessive geometry and oversized inputs cannot fall back to a guessed layout', () => {
  const unknown = fixture().bytes; unknown.writeUInt32LE(5, 0); rejects(unknown, 'UNSUPPORTED_VERSION', 'header');
  rejects(fixture({nativeRule: 0}).bytes, 'INVALID_RULE', 'header');
  for (const [width, height] of [[0, 2], [4, 0], [257, 2], [4, 257], [0xffffffff, 2]]) {
    const bytes = fixture().bytes; bytes.writeUInt32LE(width, 12); bytes.writeUInt32LE(height, 16);
    rejects(bytes, 'INVALID_DIMENSIONS', 'header');
  }
  rejects(Buffer.alloc(MAX_SUPPORTED_MAP_BYTES + 1), 'SIZE_LIMIT', 'file');
});

test('large untrusted counts fail before allocation and coordinate limits are table specific', () => {
  for (const [table, count, section] of [['walls', 101, 'wallItems'], ['hidden', 9, 'hiddenItems'], ['a', 9, 'spawnGroupA'], ['b', 9, 'spawnGroupB'], ['objectives', 9, 'objectives']]) {
    const {bytes, offsets} = fixture(); bytes.writeUInt32LE(count, offsets[table]); rejects(bytes, 'COUNT_LIMIT', section);
  }
  const {bytes, offsets} = fixture(); bytes.writeUInt32LE(0xffffffff, offsets.walls); rejects(bytes, 'COUNT_LIMIT', 'wallItems');
});

test('wall records reject invalid ranges, nonfinite probabilities, zero or duplicate IDs', () => {
  const valid = {sceneID: 7, minimum: 0, maximum: 2, probability: 0.5};
  for (const changes of [{sceneID: 0}, {minimum: 3}, {maximum: 32768}, {probability: NaN}, {probability: Infinity}, {probability: -Infinity}, {probability: -0.01}, {probability: 1.01}]) {
    rejects(fixture({walls: [{...valid, ...changes}]}).bytes, 'INVALID_WALL_ITEM', 'wallItems');
  }
  rejects(fixture({walls: [valid, {...valid}]}).bytes, 'DUPLICATE_SCENE_ID', 'wallItems');
});

test('coordinates remain row/column, reject out-of-bounds and duplicates in each table, and retain valid edge cells', () => {
  for (const [table, section] of [['hidden', 'hiddenItems'], ['a', 'spawnGroupA'], ['b', 'spawnGroupB'], ['objectives', 'objectives']]) {
    rejects(fixture({[table]: [[2, 0]]}).bytes, 'CELL_OUT_OF_BOUNDS', section);
    rejects(fixture({[table]: [[0, 4]]}).bytes, 'CELL_OUT_OF_BOUNDS', section);
    rejects(fixture({[table]: [[1, 3], [1, 3]]}).bytes, 'DUPLICATE_CELL', section);
    assert.equal(parseOriginalMap(fixture({[table]: [[1, 3]]}).bytes).tables[section].count, 1);
  }
  const edge = parseOriginalMap(fixture({width: 256, height: 1, objectives: [[0, 255]]}).bytes);
  assert.equal(edge.tables.objectives.entries[0].col, 255);
});

test('even zero-filled trailing data is rejected at its exact start rather than silently ignored', () => {
  const {bytes} = fixture();
  for (const suffix of [Buffer.from([0]), Buffer.from([1, 2, 3, 4])]) {
    assert.throws(() => parseOriginalMap(Buffer.concat([bytes, suffix])), error => error.code === 'TRAILING_DATA' && error.offset === bytes.length && error.section === 'trailing');
  }
});

test('read-only CLI emits JSON for a synthetic file and structured errors for malformed files', async t => {
  const directory = await mkdtemp(join(tmpdir(), 'qqtang-map-parser-'));
  t.after(() => rm(directory, {recursive: true, force: true}));
  const path = join(directory, 'artificial.map');
  const script = fileURLToPath(new URL('../scripts/inspect-original-map.mjs', import.meta.url));
  const {bytes} = fixture({objectives: [[1, 3]]});
  await writeFile(path, bytes);
  const full = spawnSync(process.execPath, [script, path], {encoding: 'utf8'});
  assert.equal(full.status, 0, full.stderr);
  assert.equal(full.stderr, '');
  assert.equal(JSON.parse(full.stdout).layers[2].values.length, 8);
  const summary = spawnSync(process.execPath, [script, path, '--summary'], {encoding: 'utf8'});
  assert.equal(summary.status, 0, summary.stderr);
  assert.equal(JSON.parse(summary.stdout).tables.objectives.count, 1);
  assert.equal(JSON.parse(summary.stdout).layers[0].values, undefined);
  await writeFile(path, Buffer.concat([bytes, Buffer.from([0])]));
  const invalid = spawnSync(process.execPath, [script, path], {encoding: 'utf8'});
  assert.equal(invalid.status, 1);
  assert.equal(invalid.stdout, '');
  assert.equal(JSON.parse(invalid.stderr).error.code, 'TRAILING_DATA');
  assert.equal(JSON.parse(invalid.stderr).error.offset, bytes.length);
});

test('directory inspection is sorted, nonrecursive and retains malformed-file evidence without concealing later files', async t => {
  const directory = await mkdtemp(join(tmpdir(), 'qqtang-map-batch-'));
  t.after(() => rm(directory, {recursive: true, force: true}));
  const {bytes} = fixture();
  await writeFile(join(directory, 'z-good.MAP'), bytes);
  await writeFile(join(directory, 'a-bad.map'), Buffer.concat([bytes, Buffer.from([0])]));
  await writeFile(join(directory, 'mapDesc.py'), 'raise RuntimeError("MUST NEVER EXECUTE")');
  await mkdir(join(directory, 'nested'));
  await writeFile(join(directory, 'nested', 'not-scanned.map'), bytes);
  await mkdir(join(directory, 'not-a-file.map'));
  const report = await inspectMapDirectory(directory, {summary: true});
  assert.deepEqual(report.scan, {recursive: false, regularFilesOnly: true, mapEntryCount: 3, parsedCount: 1, rejectedCount: 2});
  assert.deepEqual(report.results.map(entry => entry.fileName), ['a-bad.map', 'not-a-file.map', 'z-good.MAP']);
  assert.equal(report.results[0].error.code, 'TRAILING_DATA');
  assert.match(report.results[0].source.sha256, /^[0-9a-f]{64}$/);
  assert.equal(report.results[0].source.byteLength, bytes.length + 1);
  assert.equal(report.results[1].error.code, 'NOT_A_FILE');
  assert.equal(report.results[2].map.layers[0].values, undefined);
  assert.equal(report.results[2].map.layers[0].entryCount, 8);
  assert.deepEqual(await readFile(join(directory, 'z-good.MAP')), bytes);
  const script = fileURLToPath(new URL('../scripts/inspect-original-map.mjs', import.meta.url));
  const cli = spawnSync(process.execPath, [script, '--directory', directory, '--summary'], {encoding: 'utf8'});
  assert.equal(cli.status, 1); // One rejected map must not look like full batch success.
  assert.equal(cli.stderr, '');
  assert.equal(JSON.parse(cli.stdout).scan.parsedCount, 1);
  assert.equal(JSON.parse(cli.stdout).scan.rejectedCount, 2);
});
