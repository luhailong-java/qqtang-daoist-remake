"""Write exact builtin generation requests; this file never calls a paid API."""
from pathlib import Path
import datetime
import hashlib
import json

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
REFS = ['references/image/01-mail-event.png', 'references/image/team-ui-v2.png']
EXPRESSIONS = [
    'A worried sad face: upward inner eyebrows, two tiny downcast open eyes with a small tear glint, and a simple small downturned mouth.',
    'A tightly squeezed distressed face: two inward diagonal squeezed shut eyes, pinched eyebrows, and a small wavy trembling mouth.',
    'A calm friendly smiling face: two tall open dark jade oval eyes with small light glints, two tiny peach blush marks, and a gentle upward curved closed smile.',
    'A joyful laughing face: two closed upward arch eyes, peach pink blush cheeks, and a wide open happy smile with a small ivory tooth line.',
    'An affectionate face: two bright cinnabar red heart shaped eyes and a tiny puckered kiss mouth, with a little warm peach cheek tint.',
]


def main():
    requests = []
    for i, expression in enumerate(EXPRESSIONS):
        prompt = (
            'Create ONE original Daoist Q-style game UI emotion speech-bubble icon as a finished transparent PNG. '
            'Use the two attached images ONLY as visual style references for the existing jade, warm gold and ivory hand-painted Daoist game interface. '
            'Do not reproduce their text, people, scene, UI layout, or any QQTang art. '
            'The subject is a simple circular, slightly squashed round ivory silk-paper emotion face inside a soft pale jade outline, with one short speech tail pointing down-left. '
            'The bubble itself fills about 80 percent of the square, centered with a generous fully transparent margin. '
            'The tail is contained inside that same overall silhouette. Front-facing flat 2D game icon, rounded and cute, subtle hand-painted warm ivory body, restrained gold rim and pale jade edge. '
            'Strong readable dark jade facial marks, designed to remain legible at 34 by 33 pixels. '
            + expression + ' '
            'Keep the face marks very simple and centered; no character body, ears, hats, hair, arms, props, decoration around the face, letters, words, numerals, watermark, floor, backdrop, gradients outside the cutout, or cast shadow. '
            'Real RGBA transparency around the isolated speech bubble; do not render a white or checkered background. '
            'This is a new original drawing for one emotion, not a contact sheet or a layout of several expressions.'
        )
        requests.append({'sourceIndex': i, 'sourceInterpretation': expression, 'submitted': {
            'prompt': prompt, 'referenced_image_paths': [str(ROOT / p) for p in REFS],
            'transparent_background': True}, 'referenceImages': [
                {'file': p, 'sha256': hashlib.sha256((ROOT / p).read_bytes()).hexdigest(), 'role': 'user canonical style only'} for p in REFS],
            'configuredTarget': json.loads((ROOT / 'config/image-generation.json').read_bytes()),
            'actualSubmittedModel': None, 'actualSubmittedQuality': None,
            'actualReturnedModel': None, 'actualReturnedQuality': None,
            'route': 'host builtin image_gen', 'paidApiInvoked': False,
            'plannedOutput': f'assets/native-client-ui/pet-controls-reference/emotions/face{i}-master.png',
        })
    (HERE / 'generation-requests.json').write_text(json.dumps({
        'schemaVersion': 1, 'preparedAtUtc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
        'requests': requests, 'userVisualAccepted': False,
    }, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')


if __name__ == '__main__':
    main()
