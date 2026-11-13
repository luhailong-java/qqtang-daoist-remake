"""Seal exact builtin submission JSON, then register the unchanged returned PNG."""
from datetime import datetime, timezone
from pathlib import Path
import argparse
import hashlib
import json
import shutil

from PIL import Image

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]


def read(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))


def save(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def relative(path):
    return path.relative_to(ROOT).as_posix()


parser = argparse.ArgumentParser()
parser.add_argument('mode', choices=['seal', 'register'])
parser.add_argument('version')
args = parser.parse_args()
if any(c not in 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_' for c in args.version):
    raise ValueError('Unsafe take name')
spec_path = HERE / f'specs/{args.version}.json'
submission_path = HERE / f'submissions/{args.version}.json'
spec = read(spec_path)
submission = read(submission_path)
prompt = submission['prompt']  # JSON escapes preserve exact CRLF; never read_text(prompt_file).
prompt_file = ROOT / spec['promptFile']
if args.mode == 'seal':
    config_path = ROOT / 'config/image-generation.json'
    submission.update({
        'promptSha256': hashlib.sha256(prompt.encode('utf-8')).hexdigest(),
        'promptCharacterLength': len(prompt), 'crCount': prompt.count('\r'), 'lfCount': prompt.count('\n'),
        'promptFile': spec['promptFile'], 'promptFileSha256': sha(prompt_file),
        'configSnapshot': read(config_path), 'configSource': {'path': relative(config_path), 'sha256': sha(config_path)},
        'sealedBeforeCallAtUTC': datetime.now(timezone.utc).isoformat(),
        'referenceEvidence': [{'path': path, 'sha256': sha(Path(path)), 'purpose': role}
                              for path, role in zip(submission['submittedParameters']['referenced_image_paths'], spec['referenceRoles'])],
        'evidenceMeaning': 'Actual functions.store value, written as JSON before builtin call. No newline normalization applied.'})
    if len(submission['referenceEvidence']) != len(spec['referencePaths']):
        raise ValueError('Actual reference role count differs from planned submission')
    save(submission_path, submission)
    print(json.dumps({'sealed': args.version, 'promptSha256': submission['promptSha256'], 'crCount': submission['crCount']}))
else:
    if hashlib.sha256(prompt.encode('utf-8')).hexdigest() != submission['promptSha256']:
        raise ValueError('Sealed actual submitted prompt changed')
    if sha(prompt_file) != submission['promptFileSha256']:
        raise ValueError('Prompt file changed after actual call')
    host = Path(submission['result']['hostSource'])
    target = ROOT / spec['source']
    if target.exists() or not target.resolve().is_relative_to(HERE):
        raise ValueError('Never overwrite an existing take or leave the selected family')
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(host, target)
    with Image.open(target) as picture:
        if picture.format != 'PNG' or picture.mode != 'RGBA':
            raise ValueError('Builtin output is not a real RGBA PNG')
        width, height = picture.size
        alpha = picture.getchannel('A').getextrema()
    record = {
        'file': relative(target), 'sha256': sha(target), 'generatedAt': datetime.now(timezone.utc).isoformat(),
        'timeEvidence': 'Registration after return; provider creation time not disclosed',
        'width': width, 'height': height, 'format': 'PNG', 'nativeDimensions': True,
        'tool': 'image_gen.imagegen', 'route': 'builtin', 'configSnapshot': submission['configSnapshot'],
        'configSource': submission['configSource'], 'prompt': prompt, 'exactPrompt': prompt,
        'submittedPromptSha256': submission['promptSha256'], 'promptFile': submission['promptFile'],
        'promptFileSha256': submission['promptFileSha256'],
        'promptSubmission': 'Exact CRLF-preserving string from pre-call JSON and functions.store; not universal-newline text read',
        'submittedParameters': {'model': None, 'quality': None, **submission['submittedParameters']},
        'actualModel': None, 'actualQuality': None,
        'unverifiedReason': 'Builtin exposes no model/quality selector or verifiable return metadata',
        'references': submission['referenceEvidence'],
        'evidence': {'hostSource': str(host), 'returnedFields': submission['result']['returnedFields'],
                     'outputHint': submission['result']['outputHint'], 'selectorsExposed': False,
                     'actualSubmissionRecord': relative(submission_path), 'actualSubmissionRecordSha256': sha(submission_path)},
        'operation': 'builtin original generated source; no image resampling or program pixel editing',
        'alphaExtrema': list(alpha)}
    if spec.get('editTarget'):
        target_before = ROOT / spec['editTarget']
        record['operation'] = 'builtin AI edit of actual referenced target; no program pixel editing'
        record['editOf'] = {'file': spec['editTarget'], 'sha256': sha(target_before)}
        parent_generation = Path(str(target_before) + '.generation.json')
        if parent_generation.exists():
            record['editOf'].update({'generationRecord': relative(parent_generation), 'generationRecordSha256': sha(parent_generation)})
        crop_record = Path(str(target_before) + '.source.json')
        if crop_record.exists():
            record['editOf'].update({'sourceRecord': relative(crop_record), 'sourceRecordSha256': sha(crop_record)})
    save(Path(str(target) + '.generation.json'), record)
    print(json.dumps({'registered': args.version, 'native': [width, height], 'alpha': alpha,
                      'submittedPromptSha256': submission['promptSha256']}))
