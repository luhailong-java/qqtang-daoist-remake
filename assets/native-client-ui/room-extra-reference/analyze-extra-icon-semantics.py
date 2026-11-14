"""Separate native PVE image IDs from role IDs using inert source evidence."""
from pathlib import Path
import hashlib
import importlib.util
import json
import zipfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
spec = importlib.util.spec_from_file_location('extra_icon_inert', HERE / 'build-roster-mapping.py')
helper = importlib.util.module_from_spec(spec)
spec.loader.exec_module(helper)


def record(path):
    return {'file': path.relative_to(ROOT).as_posix(), 'sha256': hashlib.sha256(path.read_bytes()).hexdigest()}


def main():
    modules, uses, orphan_occurrences = [], [], []
    with zipfile.ZipFile(helper.ARCHIVE) as archive:
        files = [p for p in archive.namelist() if '/res/uiRes/' in p and p.lower().endswith('.pyc')]
        for member in files:
            raw = archive.read(member)
            tree, count = helper.PARSER.decode(raw)
            modules.append({'archiveMember':member, 'sourceSha256':helper.sha(raw), 'parsedObjects':count})
            for scope in helper.PARSER.collect(tree):
                direct = [c.get('text') for c in scope['constants'] if c['type']=='bytes']
                targets = [s for s in direct if s and ('object/ui/room/char/icon_' in s or s in ('xxm','zjl'))]
                if targets:
                    uses.append({'archiveMember':member, 'scope':scope['scope'], 'sourceFirstLine':scope['firstLine'],
                                 'bytecodeSha256':scope['bytecodeSha256'], 'directConstants':targets,
                                 'referencedNames':scope['names'], 'bytecodeExecuted':False})
                if any(s in ('xxm','zjl','object/ui/room/char/icon_xxm.img','object/ui/room/char/icon_zjl.img') for s in direct):
                    orphan_occurrences.append({'archiveMember':member,'scope':scope['scope'],'constants':targets})
    source_path=HERE/'manifest.json'
    source=json.loads(source_path.read_bytes())
    all_resources={r['nativePath']:r for r in source['resources']}
    mapping_path=HERE/'roster-mapping-audit.json'
    mapping=json.loads(mapping_path.read_bytes())
    pve_info=next(u for u in uses if u['scope']=='?.ui_InitPVEBoss')
    if pve_info['directConstants']!=['object/ui/room/char/icon_%d.img'] or 'm_iImageID' not in pve_info['referencedNames']:
        raise ValueError('Native PVE image-ID formatting source changed')
    player_evidence_path=ROOT/'assets/characters/motion-generated/roster-player-static-evidence.json'
    inis={p['id']:p for p in json.loads(player_evidence_path.read_bytes())['playerIni']}
    numeric=[67,69,72,73,75,77,78,79,81,85,117,118,119,124,125]
    coincidence=[]
    for key in numeric:
        ini=inis.get(key)
        coincidence.append({'numericUiImageId':key,'sameNumberPlayerIni':ini,
                            'namespaceBridgeVerified':False,
                            'interpretation':'Matching numeric suffix alone does not establish imageID-to-roleID or NPC/model identity'})
    identities=[]
    requests=json.loads((HERE/'extra-icon-generation-requests.json').read_bytes())['requests']
    for request in requests:
        original=all_resources[request['sourceNativePath']]
        identities.append({'nativePath':request['sourceNativePath'],'sourceSha256':original['sourceSha256'],
                           'nativeSlotKey':request['slotKey'],'projectUiIdentityName':request['projectUiIdentityName'],
                           'sourceNamespace':'PVEBossInfo.m_iImageID' if request['slotKey'].isdigit() else 'Unbound legacy filename alias',
                           'originalActorOrNpcId':None,'worldModelBindingVerified':False,
                           'independentUiAppearanceAllocated':True,'existingSourceRolePortraitReused':False})
    result={'schemaVersion':1,'scope':'PVE boss image-ID source proof, exact extra PVE role aliases, and remaining independent UI identity slots',
            'script':record(Path(__file__).resolve()),'sourceReferences':record(source_path),'rosterMapping':record(mapping_path),
            'sourceArchiveSha256':mapping['sourceArchiveSha256'],'sourceUiModuleCount':len(modules),'sourceModules':modules,
            'imagePathUses':uses,'numericBossImagePathUse':pve_info,
            'sourcePveAliasTuple':mapping['sourcePveAliasTuple'],'existingOwnPveRoleBindings':mapping['pveAdditionalEntries'],
            'unboundAliasOccurrencesIn13UiConstantTrees':orphan_occurrences,
            'numericPlayerIniCoincidences':coincidence,'playerIniEvidence':record(player_evidence_path),
            'independentUiIdentityAllocations':identities,
            'existingTransformationNamespace':[41,42,43,44,45,46,54,55],
            'existingTransformationMastersReusedForUnboundImageIds':False,
            'aliasDecision':'Original icon pixel equality alone is not an entity identity alias; all17 unbound image paths receive independent original portraits',
            'nativeRuntimeVerified':False,'worldCreatureOrCharacterActionsCompleted':False}
    path=HERE/'extra-icon-source-semantics.json'
    path.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'sourceUiModules':len(modules),'numericImageSlots':len(numeric),'existingOwnPveAliases':2,
                      'independentNewUiIdentities':len(identities),'unboundAliasOccurrences':len(orphan_occurrences)}))


if __name__=='__main__':
    main()
