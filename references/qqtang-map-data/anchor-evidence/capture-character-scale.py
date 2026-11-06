"""Read current renderer and existing small JSONs; no image decode or tests.

Native layer rectangle unions are frame extents, not newly measured alpha.
Projected motion bounds use retained source alpha metadata only.
"""
import hashlib
import json
from pathlib import Path
import struct

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
def read(relative):return json.loads((ROOT/relative).read_text(encoding='utf-8'))
def sha(data):return hashlib.sha256(data).hexdigest()
inputs=['src/game.js','src/app.js','src/art.js','src/character-motion.js','assets/art.json','assets/characters/motion/manifest.json',
        'assets/characters/motion-generated/daoist-child/native-role9-evidence/group0-six-phase-board.json']
art=read('assets/art.json')['characters']['assets']
motion=read('assets/characters/motion/manifest.json')
unit=40/64
static=[]
for index,ident in enumerate(['daoist-child','moon-shadow','mountain-guardian','lotus-healer']):
    p=f'assets/characters/runtime/{ident}.png.provenance.json'
    inputs.append(p)
    provenance=read(p)
    asset=art[index]
    sx,sy,sw,sh=asset['rect']
    minx,miny,maxx,maxy=provenance['visibleBounds']
    assert asset['rect']==[minx,miny,maxx-minx,maxy-miny]
    scale=min(82/sw,90/sh)
    c=motion['characters'][ident]
    static.append(dict(identity=ident,spriteIndex=index,file=asset['file'],sourceCanvas=[asset['width'],asset['height']],
        storedVisibleBounds=provenance['visibleBounds'],sourceAlphaHeightFraction=sh/asset['height'],sourceAlphaWidthFraction=sw/asset['width'],
        sourceCrop=[sx,sy,sw,sh],requestBoxBeforeMapScale=[82,90],drawnCropBeforeMapScale=[sw*scale,sh*scale],
        drawnCropMapLogicalSize=[sw*scale*unit,sh*scale*unit],drawnCropHeightIn40pxCells=sh*scale*unit/40,
        fullCanvasDrawn=False,sourcePixelToMapLogical=scale*unit,equivalentUncroppedCanvasSize=[asset['width']*scale*unit,asset['height']*scale*unit],
        motionAdoptionStatus=c['adoptionStatus'],runtimeRunDirections=list(c.get('clips',{}).get('run',{})),
        daoistGeneratedCandidatesAdopted=bool(c.get('clips')) if ident=='daoist-child' else None))
motion_samples=[]
for ident in ['mountain-guardian','lotus-healer']:
    clip=motion['characters'][ident]['clips']['run']['E']
    frame=clip['frames'][0]
    p=frame['provenance'].removeprefix('./')
    inputs.append(p)
    provenance=read(p)
    bounds=provenance['source']['alphaGt8BBox']
    source_width=provenance['source']['width'];source_height=provenance['source']['height']
    alpha_fraction=(bounds[3]-bounds[1])/source_height
    motion_samples.append(dict(identity=ident,action='run',direction='E',sampleFrame=frame['file'],frameCanvas=motion['canvas'],
        fullCanvasBeforeMapScale=[110,110],fullCanvasMapLogicalSize=[110*unit,110*unit],fullCanvasHeightInCells=110*unit/40,
        clipAnchor=clip['anchor'],clipAnchorStatus=clip.get('anchorStatus'),
        sourceCanvas=[source_width,source_height],sourceAlphaGt8BBox=bounds,sourceAlphaHeightFraction=alpha_fraction,
        projectedVisibleHeightMapLogical=alpha_fraction*110*unit,projectedVisibleHeightIn40pxCells=alpha_fraction*110*unit/40,
        actual256pxOutputAlphaMeasuredThisRun=False,sourceAlphaGt8ProjectionOnly=True))
native_path='assets/characters/motion-generated/daoist-child/native-role9-evidence/group0-six-phase-board.json'
native=read(native_path)
native_records=[]
for r in native['records']:
    layers=[dict(layer=l['layer'],frameOffset=l['frameOffset'],nativeSize=l['nativeSize'])for l in r['layers'] if not l.get('empty')]
    bounds=[min(l['frameOffset'][0]for l in layers),min(l['frameOffset'][1]for l in layers),
            max(l['frameOffset'][0]+l['nativeSize'][0]for l in layers),max(l['frameOffset'][1]+l['nativeSize'][1]for l in layers)]
    native_records.append(dict(frameIndex=r['frameIndex'],phaseIndex=r['phaseIndex'],nativeCanvas=r['nativeCanvas'],layers=layers,
        layerRectUnion=bounds,layerRectUnionSize=[bounds[2]-bounds[0],bounds[3]-bounds[1]],
        unionHeightFractionOf100=(bounds[3]-bounds[1])/100,actualAlphaUnionKnown=False,originalDisplayScaleKnown=False))
map_sample=next(r for r in read('references/qqtang-map-data/anchor-evidence/local-anchor-samples.json')['records']if r['elementId']==3019)
header=bytes.fromhex(map_sample['dimgFirst68BytesHex'])
map_3019=dict(footprintCells=map_sample['footprintCells'],nativeFrameSize=map_sample['firstFrame']['size'],
    declaredCanvas=map_sample['dimgHeader']['declaredCanvas'],retainedVisibleBBox=map_sample['retainedVisibleBoundingBox'],
    headerUnknownSignedPairAt24And28=list(struct.unpack_from('<ii',header,24)),frameSignedPairAt44And48=list(struct.unpack_from('<ii',header,44)),
    headerUnknownPairSemantics='unknown; numerically equals frameOffset here, not a second authorized translation',
    rawFrameContainsProven17pxTransparentTopPadding=False,paddingEvidence='Existing alpha bbox starts at y0 and reaches native frame bottom110; no new alpha read',
    sourceFrameDecodeAppliedFrameOffset=False,repeatAdditionAccepted=False)
snapshot=[]
for p in inputs:
    data=(ROOT/p).read_bytes();snapshot.append(dict(file=p,byteLength=len(data),sha256=sha(data)))
result=dict(schemaVersion=1,createdOn='2026-10-28',operation='Existing JSON/source arithmetic only; no image decode, tests, browser, compilation or runtime writes',
    sourceMap=dict(cellPixels=40,actorLegacyUnit=64,actorMapScale=unit,canvasBackingDensity=2),
    staticFallback=static,motionSamples=motion_samples,nativeRole9=dict(source=native_path,sourceRoleId=9,
    observedDirection=native.get('observedCardinalDirection'),compositeScope=native['compositeScope'],records=native_records),map3019=map_3019,inputSnapshot=snapshot,
    limitations=['Layer rectangle union is an upper bound on visible alpha, not a newly measured pixel bbox.',
      'Native100px canvas is not a proven100px screen draw size; original renderer transform remains unknown.',
      '68.75px full motion canvas cannot be compared directly to a native55px rectangle union without accounting for alpha fraction.',
      'Static daoist56.25px height is close to54-55px native layer extents under hypothetical1:1 native draw; this is a clue, not scale acceptance.',
      'The current motion manifest leaves daoist-child and moon-shadow clips missing; generated candidate directories are not runtime adoption.'])
(HERE/'character-scale-evidence.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(dict(static=[dict(identity=r['identity'],mapLogicalSize=r['drawnCropMapLogicalSize'],motionStatus=r['motionAdoptionStatus'])for r in static],
    motion=[dict(identity=r['identity'],fullCanvasMapLogical=r['fullCanvasMapLogicalSize'],sourceProjectedVisibleHeight=r['projectedVisibleHeightMapLogical'])for r in motion_samples],
    nativeRectHeights=[r['layerRectUnionSize'][1]for r in native_records],map3019HeaderPair=map_3019['headerUnknownSignedPairAt24And28']),ensure_ascii=False))
