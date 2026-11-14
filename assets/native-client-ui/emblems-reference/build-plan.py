"""Bind original UI slots to original project art without inventing game item bindings."""
import hashlib
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[3]
HERE=Path(__file__).resolve().parent


def record(path):
    path=ROOT/path
    return {'file':path.relative_to(ROOT).as_posix(),'sha256':hashlib.sha256(path.read_bytes()).hexdigest()}


def main():
    source=json.loads((HERE/'manifest.json').read_bytes())
    metals=('bronze-v2','silver-v1','gold-v1')
    rank=lambda metal,shape:f'assets/native-client-ui/emblems-reference/cutouts/rank-{metal}-{shape:02}.png'
    kin=[rank(m,s) for m in metals for s in range(9)]
    for name in ('forge','food'):
        d=json.loads((ROOT/f'assets/items/{name}/art.json').read_bytes())
        kin.extend(i['file'] for i in d['items'][:7 if name=='forge' else 4])
    platform=json.loads((ROOT/'assets/items/platform/art.json').read_bytes())
    wanted=(204,294,435,436,437,450,9011,9012,9013,9020)
    kin.extend(next(i['file'] for i in platform['items'] if i['itemId']==n) for n in wanted)
    if len(kin)!=48 or len(set(kin))!=48:raise ValueError('All 48 clan emblem choices need distinct own art inputs')
    def piece(family,n):
        data=json.loads((ROOT/f'assets/maps/{family}/art.json').read_bytes())
        return next(i['file'] for i in data['pieces'] if i['elementId']==n)
    special=lambda n:f'assets/native-client-ui/emblems-reference/cutouts/mode-specials-v1-{n:02}.png'
    modes={'bomb':special(1),'rand':special(2),'tank':special(0),'sculpture':special(3),'pig':special(4),'box':special(5),
           'bun':piece('bun',8005),'desert':piece('desert',1004),'field':piece('field',6003),
           'match':piece('match',11002),'mine':piece('mine',4005),'snow':piece('snow',2002),
           'town':piece('town',3006),'treasure':piece('treasure',10005),'water':piece('water',5002)}
    # These are slot silhouettes/material families read from the source contact sheet, not level thresholds.
    medal=[('bronze-v2',0),('gold-v1',0),('silver-v1',0),('bronze-v2',1),('silver-v1',1),('gold-v1',1),
           ('bronze-v2',2),('silver-v1',2),('gold-v1',2),('bronze-v2',2),
           ('bronze-v2',3),('silver-v1',3),('gold-v1',3),('bronze-v2',4),('silver-v1',4),('gold-v1',4),
           ('bronze-v2',5),('silver-v1',5),('gold-v1',5),('bronze-v2',5),
           ('bronze-v2',6),('silver-v1',6),('gold-v1',6),('bronze-v2',7),('silver-v1',7),('gold-v1',7),
           ('bronze-v2',6),('silver-v1',6),('gold-v1',6),('gold-v1',8)]
    result=[]
    for entry in source['resources']:
        path=entry['nativePath'];stem=Path(path).stem;art=[]
        if '/kintotem/' in path:
            kind='kin';art=[] if stem=='000' else [kin[int(stem)-1]]
        elif '/level/medal/' in path:
            kind='medal';art=[rank(*medal[int(stem)-1])]
        elif '/level/tie/' in path:kind='tie'
        elif '/map/' in path:
            kind='map';art=[modes['field'],modes['mine'],modes['treasure']] if stem=='all' else [rank('gold-v1',0)] if stem=='normal' else [modes[stem]]
        elif '/cursor/' in path:
            kind='cursor';art=['assets/native-client-ui/emblems-reference/masters/cursor-arrow-v1.png'] if stem in ('arror','fight') else [
                'assets/native-client-ui/emblems-reference/masters/cursor-click-v1.png',
                'assets/native-client-ui/emblems-reference/masters/cursor-click-pressed-v1.png']
        else:raise ValueError(path)
        result.append({'nativePath':path,'kind':kind,'ownArt':[record(p) for p in art],
                       'sourceSha256':entry['sourceSha256'],'nativeGeometry':entry['metadata'],
                       'mappingScope':'UI display slot only; no claim that own thematic motif is the source item ID or world entity',
                       'visualAccepted':False,'nativeRuntimeVerified':False})
    data={'schemaVersion':1,'sourceReference':record('assets/native-client-ui/emblems-reference/manifest.json'),
          'planner':record(Path(__file__).relative_to(ROOT)), 'items':result,'resourceCount':len(result),
          'knownSourceAliases':[{'paths':['object/ui/cursor/arror.img','object/ui/cursor/fight.gsa'],
             'evidence':'Exact source native bytes equal across packed and loose data; both receive identical own arrow states'}]+[{'paths':[f'object/ui/level/tie/c{i:02}.img',f'object/ui/level/tie/d{i:02}.img'],
             'evidence':'Exact source native bytes and decoded pixels equal; own strip is shared for this pair'} for i in range(1,7)],
          'sourceTimingVerified':False,'cursorHotspotsVerified':False,'levelThresholdsVerified':False,
          'interpretation':'Native rank/cursor state counts and frame windows retained. Own diagonal gleam and squash states are candidates; original elapsed timings are not established.'}
    (HERE/'own-mapping.json').write_bytes((json.dumps(data,ensure_ascii=False,indent=2)+'\n').encode())
    print(json.dumps({'mapped':len(result),'kinMotifs':len(kin),'modeIcons':len(modes)}))


if __name__=='__main__':main()
