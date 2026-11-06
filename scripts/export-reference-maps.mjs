import {createHash} from 'node:crypto';
import {mkdir, readFile, writeFile} from 'node:fs/promises';
import {join, relative, resolve} from 'node:path';
import {pathToFileURL} from 'node:url';
import {inspectMapDirectory} from './inspect-original-map.mjs';

export async function exportReferenceMaps({clientRoot, manifestPath, outputPath}) {
  const inputRoot = resolve(clientRoot);
  const outputRoot = resolve(outputPath);
  const outputRelativeToInput = relative(inputRoot, outputRoot);
  if (outputRelativeToInput === '' || (!outputRelativeToInput.startsWith('..') && !outputRelativeToInput.includes(':'))) {
    throw new Error('Output must be outside the inspected client directory.');
  }
  const manifestBytes = await readFile(resolve(manifestPath));
  const manifest = JSON.parse(manifestBytes);
  const catalog = JSON.parse(await readFile(join(outputRoot, 'catalog.json'), 'utf8'));
  const elements = JSON.parse(await readFile(join(outputRoot, 'elements.json'), 'utf8'));
  if (catalog.source.archiveSha256 !== manifest.archiveSha256 || elements.source.archiveSha256 !== manifest.archiveSha256) {
    throw new Error('Catalog, elements and extraction manifest must refer to the same archive.');
  }
  const batch = await inspectMapDirectory(join(inputRoot, 'map'));
  if (batch.scan.rejectedCount > 0) throw new Error(`Refusing a partial export: ${batch.scan.rejectedCount} map files were rejected. Inspect directory mode for details.`);
  const elementIDs = new Set(elements.elements.map(element => element.id));
  const catalogByFile = new Map();
  for (const entry of catalog.entries) {
    const key = entry.mapFileName.toLowerCase();
    if (!catalogByFile.has(key)) catalogByFile.set(key, []);
    catalogByFile.get(key).push(entry);
  }
  const sourceMetadata = {
    archiveUrl: manifest.url,
    archiveSha256: manifest.archiveSha256,
    sourceType: manifest.sourceType,
    officialOriginalAuthenticity: manifest.officialOriginalAuthenticity,
    extractionManifestSha256: createHash('sha256').update(manifestBytes).digest('hex'),
    externalCodeExecuted: false,
  };
  const records = [];
  const documents = [];
  const dimensionCounts = {};
  const versionCounts = {};
  for (const result of batch.results) {
    const map = result.map;
    const suffix = `/runtime/client-patched/map/${result.fileName}`;
    const sourceRecords = manifest.files.filter(record => record.archiveEntry.endsWith(suffix));
    if (sourceRecords.length !== 1 || sourceRecords[0].bytes !== map.source.byteLength || sourceRecords[0].sha256.toLowerCase() !== map.source.sha256) {
      throw new Error(`Map bytes do not match extraction manifest: ${result.fileName}`);
    }
    map.source = {
      ...map.source, ...sourceMetadata,
      archiveEntry: sourceRecords[0].archiveEntry,
      localInput: sourceRecords[0].localPath,
    };
    map.catalogEntries = (catalogByFile.get(result.fileName.toLowerCase()) ?? []).map(entry => ({
      id: entry.id, family: entry.family, name: entry.name, playerLimit: entry.playerLimit,
      catalogWidth: entry.catalogWidth, catalogHeight: entry.catalogHeight,
      dimensionsMatchHeader: entry.catalogWidth === map.header.width && entry.catalogHeight === map.header.height,
    }));
    map.validation = {
      extractionHashMatched: true,
      parsedWholeFile: map.parsedByteLength === map.source.byteLength && map.trailingByteLength === 0,
      catalogDimensionsOverrideHeader: false,
      unknownPositiveElementIdsByLayer: map.layers.map(layer => [...new Set(layer.values.filter(value => value > 0 && !elementIDs.has(value)))].sort((left, right) => left - right)),
      collisionAndRenderingReconstruction: 'not-performed-by-data-export',
    };
    const jsonFile = `${result.fileName.replace(/\.map$/i, '')}.json`;
    const encoded = `${JSON.stringify(map, null, 2)}\n`;
    documents.push({jsonFile, encoded});
    const dimensions = `${map.header.width}x${map.header.height}`;
    dimensionCounts[dimensions] = (dimensionCounts[dimensions] ?? 0) + 1;
    versionCounts[map.header.version] = (versionCounts[map.header.version] ?? 0) + 1;
    records.push({
      fileName: result.fileName, jsonFile: `maps/${jsonFile}`,
      byteLength: map.source.byteLength, sha256: map.source.sha256, md5: map.source.md5,
      exportedJsonSha256: createHash('sha256').update(encoded).digest('hex'),
      version: map.header.version, nativeRule: map.header.nativeRule,
      width: map.header.width, height: map.header.height, dimensionSource: map.header.dimensionSource,
      catalogEntries: map.catalogEntries,
      unknownPositiveElementIdsByLayer: map.validation.unknownPositiveElementIdsByLayer,
    });
  }
  const importedFiles = new Set(records.map(record => record.fileName.toLowerCase()));
  const map1601 = records.find(record => record.catalogEntries.some(entry => entry.id === 1601));
  const expected1601Md5 = 'ad8c5668c199c5521616a7d2d1829ddc';
  const index = {
    schemaVersion: 1, importedOn: '2026-10-26', source: sourceMetadata,
    notes: [
      'Data from the community v1.3.4 client-patched release; not authenticated as untouched Tencent original client data.',
      'No inspected Python, native binaries, scripts or asset paths were executed; only static data was read.',
      'Binary map header dimensions take precedence over mapDesc catalog dimensions; pixel cell size is not inferred.',
      'All three layers and raw coordinate tables are retained. Collision behavior and rendering anchors need separate implementation and validation.',
    ],
    mapCount: records.length, rejectedMapCount: batch.scan.rejectedCount,
    catalogEntryCount: catalog.entryCount, elementCount: elements.elementCount,
    dimensionCounts, versionCounts,
    missingCatalogFiles: catalog.entries.filter(entry => !importedFiles.has(entry.mapFileName.toLowerCase())).map(({id, family, name, mapFileName}) => ({id, family, name, mapFileName})),
    unlistedMapFiles: records.filter(record => record.catalogEntries.length === 0).map(record => record.fileName),
    catalogDimensionMismatchCount: records.filter(record => record.catalogEntries.some(entry => !entry.dimensionsMatchHeader)).length,
    map1601Md5Check: {
      expected: expected1601Md5, actual: map1601?.md5 ?? null, matches: map1601?.md5 === expected1601Md5,
      fileName: map1601?.fileName ?? null,
      expectationSource: 'https://github.com/kuuhaku1314/qqtang/blob/4b3a245fd985cabd4abd68ade6c282cc163d9edb/internal/game/mapdata/catalog_test.go#L784-L800',
      meaning: 'Match to one community runtime test expectation; not a Tencent authenticity or signature certificate.',
    },
    maps: records,
  };
  // Validate every input before writing any map outputs, avoiding a falsely
  // complete-looking export when a late file fails manifest verification.
  await mkdir(join(outputRoot, 'maps'), {recursive: true});
  for (const {jsonFile, encoded} of documents) await writeFile(join(outputRoot, 'maps', jsonFile), encoded);
  await writeFile(join(outputRoot, 'index.json'), `${JSON.stringify(index, null, 2)}\n`);
  return index;
}

async function cli(args) {
  if (args.length !== 6 || args[0] !== '--client-root' || args[2] !== '--manifest' || args[4] !== '--output') {
    throw new Error('Usage: node scripts/export-reference-maps.mjs --client-root <client-root> --manifest <extraction-manifest.json> --output <reference-output-directory>');
  }
  const index = await exportReferenceMaps({clientRoot: args[1], manifestPath: args[3], outputPath: args[5]});
  console.log(JSON.stringify({mapCount: index.mapCount, rejectedMapCount: index.rejectedMapCount, dimensionCounts: index.dimensionCounts, versionCounts: index.versionCounts, missingCatalogFiles: index.missingCatalogFiles, unlistedMapFiles: index.unlistedMapFiles, catalogDimensionMismatchCount: index.catalogDimensionMismatchCount, map1601Md5Check: index.map1601Md5Check}, null, 2));
}

if (process.argv[1] && pathToFileURL(resolve(process.argv[1])).href === import.meta.url) {
  cli(process.argv.slice(2)).catch(error => { console.error(error.message); process.exitCode = 1; });
}
