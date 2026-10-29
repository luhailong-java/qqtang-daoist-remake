"""Write all97 entity contracts from existing small JSON; no image/resource scan."""
from pathlib import Path
from datetime import datetime,timezone
import json,hashlib
ROOT=Path(__file__).resolve().parents[3]
OUT=Path(__file__).resolve().parent/'creatures'
CONTRACT=OUT/'motion-contract'
mapping=json.loads((OUT/'identity-mapping.json').read_text(encoding='utf-8'))
masters={x['entityId']:x for x in json.loads((OUT/'art.json').read_text(encoding='utf-8'))['masters']}
headers=json.loads((CONTRACT/'six-header-evidence.json').read_text(encoding='utf-8'))
survey=json.loads((OUT.parent/'adventure-source-survey/static-survey.json').read_text(encoding='utf-8'))
rows=[]
for identity in sorted(mapping['mappedIdentities'],key=lambda x:x['entityId']):
    ident=identity['entityId']; groups=identity['sourceMapGroups']; master=masters[ident]
    rows.append({'entityId':ident,'projectOriginalChineseIdentityName':identity['projectOriginalChineseIdentityName'],
        'entityClass':identity.get('entityClass','ordinary'),'sourceMapIds':[x['mapId']for x in groups],
        'sourceProfileFlags':sorted({p['is_boss']for g in groups for p in g['sourceGroupUnmodified']['combat_profiles']}),
        'sourceProfileKeys':['count','health','damage','defense','speed','is_boss'],
        'sourceGameplayMapping':'../identity-mapping.json#entityId='+str(ident),'preserveSourceProfilesUnmodified':True,
        'currentStaticMaster':master['file'],'staticAccepted':False,'staticIsMotion':False,
        'sourceNativePlayerNumber':None,'sourceNativeModelNumber':None,'sourceLayerBindings':None,
        'sourceActionNames':None,'sourceActionResourcePaths':None,'sourceDirections':None,'sourceDirectionOrder':None,
        'sourceFramesPerDirection':None,'sourceFrameDurationMs':None,'sourceLoopPolicy':None,'sourceFrameOffsets':None,
        'nativeMotionContractConfirmed':False,'motionFramesProduced':0,'motionAccepted':False,
        'targetNamingTemplate':f'assets/maps/exploration/creatures/motion/{ident}/<confirmed-action>/<confirmed-direction>/NN.png',
        'pendingDeliverables':[
            {'category':'directional-rest-and-locomotion','status':'contract-unconfirmed','note':'Need source-linked state/action names, direction count/order, frame count and timing before final frame budget.'},
            {'category':'combat-anticipation-and-reaction','status':'conditional-unconfirmed','note':'Produce only source gameplay states confirmed for this ID; held prop adds no skills.'},
            {'category':'defeat-and-exit','status':'conditional-unconfirmed','note':'Need ID-linked resource/call evidence; generic player die file is not an NPC mapping.'},
            {'category':'Boss-phase-or-special-state','status':'conditional-unconfirmed','note':'is_boss does not by itself prove visual phases, phase counts, summoned forms or special actions.'}],
        'evidenceNeeded':['source boss_id -> native model/player/layer association','model -> action DIMG paths','direction index meanings and mirroring policy','native state event -> action playback call','native frame timing/loop/transition and visual root'],
        'doNotSubstitute':['static image translation/rotation is not source animation','do not apply unrelated player67/73 samples','do not infer model number by subtracting30000','do not guess npcIcon index or known avatar/transformation name'],
        'artAddsNoRules':True})
assert len(rows)==97
report={'schemaVersion':1,'createdAtUTC':datetime.now(timezone.utc).isoformat(),
        'scope':'Full97 source entity motion/direction contract gap list, with six unbound native DIMG header examples',
        'sourceEntityNamespace':'adventure-rules.maps.npc_drop_groups.boss_id, not item_id/avatar/player',
        'sourceGameplayFile':'QQTang-Local/configs/adventure-rules.json',
        'sourceGameplaySHA256':survey['rules']['sha256'],
        'entityCount':97,'staticCandidateCoverage':97,'nativeModelMappingsConfirmed':0,'nativeActionMappingsConfirmed':0,
        'sourceDirectionOrdersConfirmed':0,'sourceNativeTimingsConfirmed':0,'motionFramesProduced':0,'fullEntityArtComplete':False,
        'headerEvidence':'six-header-evidence.json','selectedHeaderResources':6,'pixelsDecodedThisMotionPass':0,
        'unboundHeaderCounts':[{'resourcePath':x['resourcePath'],'sha256':x['rawResourceSHA256'],'directions':x['declaredDirections'],'framesPerDirection':x['declaredFramesPerDirection']}for x in headers['resourceSamples']],
        'coordinatorSourceReview':{'fixedCommit':'4b3a245fd985cabd4abd68ade6c282cc163d9edb',
            'paths':['internal/protocol/game/pve_boss.go','internal/game/match/adventure.go','internal/clientdata/sceneelement/catalog.go'],
            'reportedFinding':'Parent independently read these fixed sources; BossID groups/drop identity does not establish boss_id to native player/model mapping.',
            'reviewer':'root coordinator; no duplicate child verification claimed','sourceContentHashForThisChild':None},
        'entities':rows}
(CONTRACT/'entity-motion-contract.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
lines=['# 97实体动作与方向资源合同','','2026-10-28。97个源实体均有独立原创静态首稿；**原生模型映射、动作映射、方向顺序和播放时序均未确认，动作帧0，完整实体美术未完成**。本合同为完整缺项清单，不把未知值补成通用四向六帧。','',
'源ID来自`npc_drop_groups.boss_id`，不同于道具`item_id`、玩家`player`和角色`avatar`。现有完整战斗组只提供count/health/damage/defense/speed/is_boss及掉落池，没有图像或动作字段。30087保留逐地图混合分类。','',
'仅读取两份小INI和六个明确选定DIMG的40字节头，使用缓存object.idx的固定包偏移有界解压；没有解码像素、遍历帧体、验证整个DIMG容器或重哈希大ZIP/包。每资源记录原始与压缩数据SHA、头SHA、路径、偏移、声明帧数/方向数。来源是社区修订客户端，腾讯原始官方真实性仍未确认。','',
'| 未绑定样本 | 头声明总帧 | 头声明方向 | 每方向声明帧 |','|---|---:|---:|---:|']
for x in headers['resourceSamples']:lines.append(f'| `{x["resourcePath"]}` | {x["declaredFrameCount"]} | {x["declaredDirections"]} | {x["declaredFramesPerDirection"]} |')
lines+=['','这些样本由player67/73的cloth层关联选出，**未绑定任何97实体**。player73的cry原值173701按原文保留，没有纠正为17301。INI列出的trigger/win/cry/lose/wait不能仅凭同一cloth编号认定对应动作文件存在，更不能作为NPC动作合同。DIMG头没有原生每帧时长，GM示例100ms也不作为客户端时序。方向索引的东南西北顺序、镜像策略和根点不猜。','',
'每个实体的JSON条目分别保留地图、分类、静态当前路径和动作缺项。交付目标命名模板为`motion/<ID>/<已证实动作>/<已证实方向>/NN.png`，目前未创建假帧。需先取得ID→模型/图层、模型→动作文件、状态→播放调用及原生方向/时序/偏移证据，再确定逐ID帧预算和制作。','',
'动作候选类别为站立/移动、已证实战斗前摇/反应、已证实离场，以及有实际规则依据的Boss特殊状态；它们是待确认交付项，不是新玩法或已验证源动作名。不得以静态图平移/旋转、无关玩家动作或自定三波怪代替全集。','',
'固定来源与哈希见`six-header-evidence.json`及六份`.header.json`；完整97行见`entity-motion-contract.json`。本轮未构建、未运行客户端、未做全族图像QA，重型作业暂停仍有效。','']
(CONTRACT/'README.md').write_text('\n'.join(lines),encoding='utf-8')
print(json.dumps({'contractEntities':97,'staticCandidates':97,'nativeModelBindings':0,'selectedHeaderResources':6,'pixelDecodes':0,'motionFrames':0,'fullEntityArtComplete':False}))
