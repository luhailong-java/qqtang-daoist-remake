"""Deterministic source registration/QA; never generates or mirrors poses."""
from pathlib import Path
from PIL import Image
import numpy as np
import json, hashlib, datetime

BASE = Path(__file__).resolve().parent
REPO = BASE.parents[2]
IMAGE_REPO = Path(r'D:\work\image')

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def write(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

config = json.loads((IMAGE_REPO / 'config/image-generation.json').read_text(encoding='utf-8-sig'))
selected = json.loads((BASE / 'south-v2.contract.json').read_text())
selected.update(schemaVersion=1, artSource='builtin_image_gen', canvas=[256, 256],
                status='partial_internal_client_candidates', runtimeEnabled=False,
                clientApproved=False, userAccepted=False)
for cid, character in selected['characters'].items():
    character.update(name={'daoist-child': '道童', 'moon-shadow': '月影'}[cid],
                     adoptionStatus='client_candidate',
                     sourceStatus='builtin_generated_internal_review_candidate',
                     warnings=['four_frame_coarse_loop_client_review_pending'])

for cid in ['daoist-child', 'moon-shadow']:
    for sheet in sorted((BASE / cid).glob('walk-*.png')):
        stem = sheet.stem
        if stem in ['walk-sheet-v1', 'walk-south-v2']:
            continue
        direction = {'north': 'N', 'east': 'E', 'west': 'W'}[stem.split('-')[1]]
        parent = sheet.parent
        image = Image.open(sheet)
        assert image.size == (2048, 768) and image.mode == 'RGBA'
        submission = json.loads((parent / f'{stem}.submission.json').read_text())
        receipt = json.loads((parent / f'{stem}.receipt.json').read_text())
        mask = np.asarray(image.getchannel('A'))
        passed = cid == 'daoist-child' and stem in ['walk-north-v3', 'walk-east-v4', 'walk-west-v3']
        failures = [] if passed else ['opposite_leg_phase_not_established: frames1/3 or2/4 retain the same leading/support limb']
        if cid == 'daoist-child' and stem == 'walk-east-v3':
            failures = ['visible_brown_blocky_alpha_halo_outside_silhouettes; actual ivory composite not clean']
        if cid == 'moon-shadow' and direction == 'N':
            failures.append('back_head_with_front_waist_clasp_and_front_boot_motifs; rear garment design not established')
        if cid == 'moon-shadow' and direction == 'E':
            failures.append('left_hair_ornament_visibility_changes_in_frame4; side_camera_or_identity_orientation_inconsistent')
        if cid == 'daoist-child' and direction == 'W' and not passed:
            failures.append('body_view_and_gourd_arm_position_vary_between_open_and_passing_poses; held_prop_side_review_required')
        references = []
        for i, path in enumerate(submission['referenced_image_paths']):
            role = 'identity master' if i == 0 else 'primary Taoist chibi style' if i < 3 else 'edit target' if stem.endswith(('-v3', '-v4')) else 'adopted south action body/finish reference'
            references.append(dict(inputIndex=i + 1, path=path, sha256=sha(Path(path)), role=role))
        record = dict(schemaVersion=1, file=sheet.relative_to(REPO).as_posix(), sha256=sha(sheet),
                      generatedAt=None, generationTimeEvidence=receipt['times'], width=image.width,
                      height=image.height, format='PNG', mode='RGBA', alphaExtrema=list(image.getchannel('A').getextrema()),
                      tool='image_gen__imagegen', route='builtin', configSnapshot=config,
                      submittedParameters={**submission, 'model': None, 'quality': None}, actualModel=None,
                      actualQuality=None, unverifiedReason='宿主管理；工具仅返回image_url/output_hint，没有可核实版本、质量或精确生成时刻。',
                      evidence=dict(receipt=(parent / f'{stem}.receipt.json').relative_to(REPO).as_posix(),
                                    submission=(parent / f'{stem}.submission.json').relative_to(REPO).as_posix(),
                                    returnedKeys=receipt['returnedKeys'], pngMetadataKeys=list(image.info)),
                      prompt=dict(path=(parent / f'{stem}.prompt.txt').relative_to(REPO).as_posix(),
                                  sha256=sha(parent / f'{stem}.prompt.txt')), references=references,
                      status='internal_visual_candidate' if passed else 'not_passed', clientApproved=False,
                      userAccepted=False, review=dict(direction=direction, identity='original character recognizable; phase/side issues separately listed',
                          transparency='actual alpha; ivory/dark composition reviewed; hidden RGB excluded',
                          gait='opposing four phases internally confirmed' if passed else 'not_passed',
                          failureReasons=failures, note='Different PNG hashes do not establish different gait phases.'))
        if stem.endswith(('-v3', '-v4')):
            previous_stem = stem[:-1] + str(int(stem[-1]) - 1)
            record['editTarget'] = dict(file=references[-1]['path'], sha256=references[-1]['sha256'],
                generationRecord=f'assets/characters/motion-generated/daoist-child/{previous_stem}.png.generation.json')
        write(Path(str(sheet) + '.generation.json'), record)
        cuts, separators = [0], []
        for nominal in [512, 1024, 1536]:
            choices = [x for x in range(nominal - 64, nominal + 65) if int(mask[:, x].max()) <= 8]
            cut = min(choices, key=lambda x: (abs(x - nominal), int(mask[:, x].max()))) if choices else nominal
            cuts.append(cut)
            separators.append(dict(nominal=nominal, ownershipCut=cut, maxAlpha=int(mask[:, cut].max()),
                                   visiblePixelsAlphaGt8=int(np.sum(mask[:, cut] > 8))))
        cuts.append(2048)
        if any(item['visiblePixelsAlphaGt8'] for item in separators):
            failures.append('no_clear_ownership_separator; source pixels or haze cross cell cuts')
            passed = False
            record.update(status='not_passed')
            record['review'].update(failureReasons=failures)
            write(Path(str(sheet) + '.generation.json'), record)
        common, scale = 984, 256 / 984
        ground = 722 if cid == 'daoist-child' else 729
        anchor = [128, (ground + 108) * scale]
        frames, checks = [], []
        contact = Image.new('RGB', (1024, 256), '#f6f0df')
        for i in range(4):
            rect = [cuts[i], 0, cuts[i + 1], 768]
            crop = image.crop(rect)
            root_x = 256 + 512 * i - cuts[i]
            placement = [492 - root_x, 108]
            canvas = Image.new('RGBA', (common, common))
            canvas.paste(crop, tuple(placement))
            frame = canvas.convert('RGBa').resize((256, 256), Image.Resampling.LANCZOS).convert('RGBA')
            target = parent / f'frames-{stem.removeprefix("walk-")}' / direction / f'{i + 1:02d}.png'
            target.parent.mkdir(parents=True, exist_ok=True)
            frame.save(target)
            alpha = np.asarray(frame.getchannel('A'))
            ys, xs = np.where(alpha > 8)
            bbox = [int(xs.min()), int(ys.min()), int(xs.max() + 1), int(ys.max() + 1)]
            edges = int(np.sum(alpha[0, :] > 8) + np.sum(alpha[-1, :] > 8) + np.sum(alpha[:, 0] > 8) + np.sum(alpha[:, -1] > 8))
            assert edges == 0
            derived = dict(schemaVersion=1, file=target.relative_to(REPO).as_posix(), sha256=sha(target),
                derivedAt=datetime.datetime.now(datetime.timezone.utc).isoformat(), actualModel=None, actualQuality=None,
                derivedFrom=dict(file=sheet.relative_to(REPO).as_posix(), sha256=sha(sheet),
                                 generationRecord=Path(str(sheet) + '.generation.json').relative_to(REPO).as_posix()),
                operation=dict(type='ownership_crop_fixed_nominal_root_common_transparent_canvas_uniform_downscale',
                    sourceSize=[2048, 768], cropLTRB=rect, nominalCellRootX=root_x, placementOnCommonCanvas=placement,
                    commonCanvas=[984, 984], scale=scale, resampler='LANCZOS premultiplied RGBa', output=[256, 256],
                    perFrameSubjectFit=False, mirror=False, interpolatedPoses=False, newGeneration=False),
                anchor=anchor, anchorStatus='shared_character_root_candidate_not_client_approved',
                alphaExtrema=list(frame.getchannel('A').getextrema()), alphaGt8BBox=bbox,
                boundaryPixelsAlphaGt8=edges, status='internal_visual_candidate' if passed else 'not_passed',
                runtimeEnabled=False, clientApproved=False, failureReasons=failures)
            write(Path(str(target) + '.source.json'), derived)
            frames.append(dict(file='./' + target.relative_to(REPO).as_posix(), sha256=sha(target),
                provenance='./' + Path(str(target) + '.source.json').relative_to(REPO).as_posix(),
                warnings=['four_frame_loop_client_review_pending']))
            checks.append(dict(frame=i + 1, bbox=bbox, boundaryPixelsAlphaGt8=edges,
                sourceFootBBoxBottom=int(np.where(np.asarray(crop.getchannel('A')) > 8)[0].max() + 1),
                visualPhase='internally confirmed opposing phase' if passed else 'not_passed_limb_ambiguity'))
            background = Image.new('RGBA', (256, 256), '#f6f0df')
            background.alpha_composite(frame)
            contact.paste(background.convert('RGB'), (256 * i, 0))
        assert len({item['sha256'] for item in frames}) == 4
        (parent / 'qa').mkdir(exist_ok=True)
        contact.save(parent / 'qa' / f'{stem}-runtime-contact.png')
        for name, color in [('ivory', '#f6f0df'), ('dark', '#192f31')]:
            background = Image.new('RGBA', image.size, color)
            background.alpha_composite(image)
            background.convert('RGB').save(parent / 'qa' / f'{stem}-{name}.png')
        for qa in (parent / 'qa').glob(f'{stem}-*.png'):
            write(Path(str(qa) + '.source.json'), dict(file=qa.relative_to(REPO).as_posix(), sha256=sha(qa),
                derivedFrom=dict(file=sheet.relative_to(REPO).as_posix(), sha256=sha(sheet),
                    generationRecord=Path(str(sheet) + '.generation.json').relative_to(REPO).as_posix()),
                operation='diagnostic alpha composition/contact montage, no poses drawn, not runtime art'))
        write(parent / f'{stem}.review.json', dict(status='internal_visual_candidate' if passed else 'not_passed',
            runtimeEnabled=False, clientApproved=False, userAccepted=False, failureReasons=failures,
            sourceSeparators=separators, frameChecks=checks, anchor=anchor,
            sameScaleAcrossSelectedDirections=True, wholeCanvasScale=scale))
        if passed:
            source_order = [1, 4, 3, 2] if direction in ['E', 'W'] else [1, 2, 3, 4]
            runtime_frames = [frames[index - 1] for index in source_order]
            selected['characters'][cid]['clips']['run'][direction] = dict(frameMs=120, durationMs=480,
                loop=True, frameCount=4, anchor=anchor, anchorStatus='shared_character_client_candidate',
                timingStatus='trial_not_approved', frames=runtime_frames, sourceFrameOrder=source_order,
                sourceFrameOrderReason='Side contact -> opposite passing -> opposite contact -> near passing; only frame ordering changes, no pose pixels interpolated or mirrored.' if direction in ['E', 'W'] else 'native order',
                warnings=['four_frame_coarse_loop_client_review_pending'],
                generationRecord='./' + Path(str(sheet) + '.generation.json').relative_to(REPO).as_posix())
        print(cid, stem, 'candidate' if passed else 'NOT_PASSED', 'cuts', cuts)

for cid, character in selected['characters'].items():
    character['missingDirections'] = [direction for direction in 'NESW' if direction not in character['clips']['run']]
    character.update(status='client_candidate_partial_actions', runtimeEnabled=False)
write(BASE / 'runtime-candidates.manifest.json', selected)
sources = list(BASE.glob('*/*.png'))
index = dict(generatedSourceCount=len(sources), generatedSources=[],
             candidateFrameCount=sum(len(clip['frames']) for character in selected['characters'].values() for clip in character['clips']['run'].values()),
             allActualModelQualityUnconfirmed=True, old16CellSheetsRuntimeEnabled=False)
for source in sources:
    record_path = Path(str(source) + '.generation.json')
    record = json.loads(record_path.read_text(encoding='utf-8'))
    assert record['sha256'] == sha(source) and record['actualModel'] is None and record['actualQuality'] is None
    index['generatedSources'].append(dict(file=source.relative_to(REPO).as_posix(), sha256=sha(source),
        record=record_path.relative_to(REPO).as_posix(), status=record['status'], actualModel=None, actualQuality=None))
write(BASE / 'generation-index.json', index)
print('TOTAL source images', len(sources), 'selected candidate frames', index['candidateFrameCount'])
