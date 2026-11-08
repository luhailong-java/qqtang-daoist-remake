import {createHash} from 'node:crypto';
import {open, readdir} from 'node:fs/promises';
import {extname, join, resolve} from 'node:path';
import {pathToFileURL} from 'node:url';

// Independent byte-format reader, not copied community code or a client loader.
// Evidence describes one reverse-engineered competitive schema, not an official
// Tencent contract and not proof that every .map (notably PVE) shares this tail.
export const MAP_FORMAT_EVIDENCE = Object.freeze({
  commit: '4b3a245fd985cabd4abd68ade6c282cc163d9edb',
  url: 'https://github.com/kuuhaku1314/qqtang/blob/4b3a245fd985cabd4abd68ade6c282cc163d9edb/internal/game/mapdata/catalog.go#L476-L664',
  authority: 'community-reverse-engineered-competitive-schema',
});

// Derived upper bound for the supported schema: largest header, three layers,
// 100 wall records, two area-sized coordinate tables and two eight-cell tables.
export const MAX_SUPPORTED_MAP_BYTES = 20 + 3 * 256 * 256 * 4
  + 4 + 100 * 16 + 2 * (4 + 256 * 256 * 4) + 2 * (4 + 8 * 4);

export class MapParseError extends Error {
  constructor(code, message, offset = 0, section = 'header') {
    super(message);
    this.name = 'MapParseError';
    this.code = code;
    this.offset = offset;
    this.section = section;
  }
}

/**
 * Parse bytes without executing Python, native code or map-specified paths.
 * Unknown header word and all signed tile values are preserved. No collision,
 * artwork dimensions, pixel cell size, authenticity or gameplay are inferred.
 * Unrecognized/truncated/trailing data fails closed rather than being discarded.
 */
export function parseOriginalMap(input, {sourceName = null} = {}) {
  if (!(input instanceof Uint8Array)) throw new TypeError('Map input must be a Buffer or Uint8Array.');
  const bytes = Buffer.from(input.buffer, input.byteOffset, input.byteLength);
  if (bytes.length > MAX_SUPPORTED_MAP_BYTES) {
    throw new MapParseError('SIZE_LIMIT', `File exceeds the supported schema limit of ${MAX_SUPPORTED_MAP_BYTES} bytes.`, 0, 'file');
  }
  let cursor = 0;
  const fail = (code, message, section, offset = cursor) => {
    throw new MapParseError(code, message, offset, section);
  };
  const requireBytes = (count, section) => {
    if (!Number.isSafeInteger(count) || count < 0 || count > bytes.length - cursor) {
      fail('TRUNCATED', `${section} requires ${count} bytes; ${bytes.length - cursor} remain.`, section);
    }
  };
  const uint32 = section => {
    requireBytes(4, section);
    const value = bytes.readUInt32LE(cursor);
    cursor += 4;
    return value;
  };

  requireBytes(12, 'header');
  const version = uint32('header');
  if (version !== 3 && version !== 4) fail('UNSUPPORTED_VERSION', `Unsupported map version ${version}.`, 'header', 0);
  const nativeRule = uint32('header');
  if (nativeRule === 0) fail('INVALID_RULE', 'Rule 0 is not valid in the supported competitive schema.', 'header', 4);
  const unknownWordAt8 = {offset: 8, rawHex: bytes.subarray(8, 12).toString('hex'), uint32LE: uint32('header')};
  let width = 15;
  let height = 13;
  if (version === 4) {
    requireBytes(8, 'header');
    width = uint32('header');
    height = uint32('header');
  }
  if (width < 1 || width > 256 || height < 1 || height > 256) {
    fail('INVALID_DIMENSIONS', `Unsupported dimensions ${width} × ${height}; each must be within 1..256.`, 'header', version === 4 ? 12 : 0);
  }
  const headerByteLength = cursor;
  const cellCount = width * height;
  requireBytes(3 * cellCount * 4, 'layers');
  const layers = [];
  for (let index = 0; index < 3; index++) {
    const offset = cursor;
    const values = new Array(cellCount);
    for (let cell = 0; cell < cellCount; cell++, cursor += 4) values[cell] = bytes.readInt32LE(cursor);
    layers.push({index, offset, byteLength: cellCount * 4, encoding: 'int32-le-row-major', values});
  }

  const wallOffset = cursor;
  const wallCount = uint32('wallItems');
  if (wallCount > 100) fail('COUNT_LIMIT', `Wall-item count ${wallCount} exceeds 100.`, 'wallItems', wallOffset);
  requireBytes(wallCount * 16, 'wallItems');
  const wallEntries = [];
  const sceneIDs = new Set();
  for (let index = 0; index < wallCount; index++) {
    const offset = cursor;
    const sceneID = uint32('wallItems');
    const minimum = uint32('wallItems');
    const maximum = uint32('wallItems');
    const probabilityBits = bytes.readUInt32LE(cursor);
    const probability = bytes.readFloatLE(cursor);
    cursor += 4;
    if (sceneID === 0 || minimum > maximum || maximum > 32767
      || !Number.isFinite(probability) || probability < 0 || probability > 1) {
      fail('INVALID_WALL_ITEM', `Invalid wall-item record ${index}.`, 'wallItems', offset);
    }
    if (sceneIDs.has(sceneID)) fail('DUPLICATE_SCENE_ID', `Repeated wall-item scene ID ${sceneID}.`, 'wallItems', offset);
    sceneIDs.add(sceneID);
    wallEntries.push({offset, sceneID, minimum, maximum, probability, probabilityBits});
  }

  const readCells = (section, limit) => {
    const offset = cursor;
    const count = uint32(section);
    if (count > limit) fail('COUNT_LIMIT', `${section} count ${count} exceeds ${limit}.`, section, offset);
    requireBytes(count * 4, section);
    const entries = [];
    const seen = new Set();
    for (let index = 0; index < count; index++) {
      const cellOffset = cursor;
      const row = bytes.readUInt16LE(cursor);
      const col = bytes.readUInt16LE(cursor + 2);
      cursor += 4;
      if (row >= height || col >= width) fail('CELL_OUT_OF_BOUNDS', `${section} cell ${index} (${row}, ${col}) exceeds ${height} rows × ${width} columns.`, section, cellOffset);
      const key = row * width + col;
      if (seen.has(key)) fail('DUPLICATE_CELL', `${section} repeats cell (${row}, ${col}).`, section, cellOffset);
      seen.add(key);
      entries.push({offset: cellOffset, row, col});
    }
    return {offset, count, byteLength: cursor - offset, entries};
  };
  const tables = {
    wallItems: {offset: wallOffset, count: wallCount, byteLength: cursor - wallOffset, entries: wallEntries},
    hiddenItems: readCells('hiddenItems', cellCount),
    spawnGroupA: readCells('spawnGroupA', 8),
    spawnGroupB: readCells('spawnGroupB', 8),
    objectives: readCells('objectives', cellCount),
  };
  if (cursor !== bytes.length) fail('TRAILING_DATA', `${bytes.length - cursor} unrecognized trailing bytes; no data was silently discarded.`, 'trailing');

  return {
    schemaVersion: 1,
    evidence: MAP_FORMAT_EVIDENCE,
    source: {
      name: sourceName,
      byteLength: bytes.length,
      sha256: createHash('sha256').update(bytes).digest('hex'),
      md5: createHash('md5').update(bytes).digest('hex'),
      authenticity: 'not-established-by-parser',
    },
    header: {
      version, nativeRule, unknownWordAt8, byteLength: headerByteLength, width, height,
      dimensionSource: version === 3 ? 'community-v3-format-default' : 'v4-file-header',
    },
    layers,
    tables,
    parsedByteLength: cursor,
    trailingByteLength: 0,
  };
}

export function summarizeOriginalMap(map) {
  return {
    schemaVersion: map.schemaVersion,
    evidence: map.evidence,
    source: map.source,
    header: map.header,
    layers: map.layers.map(({index, offset, byteLength, encoding, values}) => ({index, offset, byteLength, encoding, entryCount: values.length})),
    tables: Object.fromEntries(Object.entries(map.tables).map(([name, {offset, count, byteLength}]) => [name, {offset, count, byteLength}])),
    parsedByteLength: map.parsedByteLength,
    trailingByteLength: map.trailingByteLength,
  };
}

function errorDetails(error) {
  return {
    name: error.name, code: error.code ?? 'READ_FAILED', message: error.message,
    ...(error instanceof MapParseError ? {offset: error.offset, section: error.section} : {}),
  };
}

export async function readOriginalMapBytes(path) {
  const filePath = resolve(path);
  const file = await open(filePath, 'r');
  let bytes;
  try {
    const info = await file.stat();
    if (!info.isFile()) throw new MapParseError('NOT_A_FILE', 'Input is not a regular file.', 0, 'file');
    if (info.size > MAX_SUPPORTED_MAP_BYTES) throw new MapParseError('SIZE_LIMIT', 'Input exceeds the supported schema size limit.', 0, 'file');
    // A bounded read also avoids an unbounded allocation if the file grows after stat.
    bytes = Buffer.alloc(info.size + 1);
    let read = 0;
    while (read < bytes.length) {
      const result = await file.read(bytes, read, bytes.length - read, read);
      if (result.bytesRead === 0) break;
      read += result.bytesRead;
    }
    if (read !== info.size) throw new MapParseError('FILE_CHANGED', 'Input length changed while reading; retry a stable file.', 0, 'file');
    bytes = bytes.subarray(0, read);
  } finally {
    await file.close();
  }
  return bytes;
}

/** Inspect only regular .map files directly inside a trusted directory.
 * Python/config files, subdirectories and symbolic links are never executed or
 * followed. A failed map has a separate result and does not conceal later maps.
 */
export async function inspectMapDirectory(path, {summary = false} = {}) {
  const directory = resolve(path);
  const entries = (await readdir(directory, {withFileTypes: true}))
    .filter(entry => extname(entry.name).toLowerCase() === '.map')
    .sort((left, right) => left.name < right.name ? -1 : left.name > right.name ? 1 : 0);
  if (entries.length > 4096) throw new MapParseError('DIRECTORY_LIMIT', 'More than 4096 .map entries; use a smaller directory.', 0, 'directory');
  const results = [];
  for (const entry of entries) {
    const filePath = join(directory, entry.name);
    if (!entry.isFile()) {
      results.push({fileName: entry.name, status: 'rejected', error: errorDetails(new MapParseError('NOT_A_FILE', 'Entry is not a regular file; no symlink or directory was followed.', 0, 'file'))});
      continue;
    }
    let source;
    try {
      const bytes = await readOriginalMapBytes(filePath);
      source = {
        name: filePath, byteLength: bytes.length,
        sha256: createHash('sha256').update(bytes).digest('hex'),
        md5: createHash('md5').update(bytes).digest('hex'),
        authenticity: 'not-established-by-parser',
      };
      const map = parseOriginalMap(bytes, {sourceName: filePath});
      results.push({fileName: entry.name, status: 'parsed', map: summary ? summarizeOriginalMap(map) : map});
    } catch (error) {
      results.push({fileName: entry.name, status: 'rejected', ...(source ? {source} : {}), error: errorDetails(error)});
    }
  }
  const parsedCount = results.filter(result => result.status === 'parsed').length;
  return {
    schemaVersion: 1, evidence: MAP_FORMAT_EVIDENCE, directory,
    sourceAuthenticity: 'not-established-by-parser',
    scan: {recursive: false, regularFilesOnly: true, mapEntryCount: entries.length, parsedCount, rejectedCount: results.length - parsedCount},
    results,
  };
}

async function runCli(args) {
  if (args.length === 1 && (args[0] === '--help' || args[0] === '-h')) {
    process.stdout.write('Usage: node scripts/inspect-original-map.mjs <file.map> [--summary]\n       node scripts/inspect-original-map.mjs --directory <map-directory> [--summary]\nReads only the supported community competitive schema; writes JSON to stdout.\nDirectory mode continues after errors, includes all failures, and exits with status 1 if any file is rejected.\n');
    return;
  }
  const summary = args.includes('--summary');
  const positional = args.filter(arg => arg !== '--summary');
  if (positional[0] === '--directory' && positional.length === 2 && !positional[1].startsWith('--') && args.length <= 3) {
    const batch = await inspectMapDirectory(positional[1], {summary});
    process.stdout.write(`${JSON.stringify(batch, null, 2)}\n`);
    if (batch.scan.rejectedCount > 0) process.exitCode = 1;
    return;
  }
  if (positional.length !== 1 || positional[0].startsWith('--') || args.length > 2) {
    throw new MapParseError('CLI_USAGE', 'Expected one map path or --directory <map-directory>, with optional --summary.', 0, 'arguments');
  }
  const filePath = resolve(positional[0]);
  const bytes = await readOriginalMapBytes(filePath);
  const map = parseOriginalMap(bytes, {sourceName: filePath});
  process.stdout.write(`${JSON.stringify(summary ? summarizeOriginalMap(map) : map, null, 2)}\n`);
}

const invokedPath = process.argv[1] ? pathToFileURL(resolve(process.argv[1])).href : null;
if (invokedPath === import.meta.url) {
  runCli(process.argv.slice(2)).catch(error => {
    process.stderr.write(`${JSON.stringify({error: errorDetails(error)})}\n`);
    process.exitCode = 1;
  });
}
