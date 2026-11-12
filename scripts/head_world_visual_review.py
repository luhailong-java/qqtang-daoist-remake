"""Validate explicit user approval of one unchanged static world-raster only."""
import hashlib
import json
from pathlib import Path


STATIC_SCOPE = 'static-export-raster'
EXCLUDED_SCOPES = {'native-timing', 'head-attachment', 'in-game-composition',
                   'direction-semantics', 'complete-animation', 'complete-game'}


def _local(root, relative):
    if not isinstance(relative, str) or not relative or Path(relative).is_absolute():
        raise ValueError('Review paths must be nonempty project-relative paths')
    path = (root / relative).resolve()
    if not path.is_relative_to(root.resolve()):
        raise ValueError('Review path leaves the project')
    return path


def _sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def validate_static_visual_review(frame, item_id, root):
    """Return whether a static approval is valid; reject broader acceptance."""
    root = Path(root)
    for key in ('accepted', 'geometryAccepted', 'runtimeAdopted'):
        if frame.get(key) is not False:
            raise ValueError(f'Static review cannot approve {key}')
    if frame.get('completeAnimationAccepted', False) is not False:
        raise ValueError('Static review cannot approve completeAnimationAccepted')
    if frame.get('visualAccepted') is False:
        return False
    if frame.get('visualAccepted') is not True:
        raise ValueError('visualAccepted must be an explicit boolean')
    if frame.get('visualAcceptanceScope') != STATIC_SCOPE or frame.get('userReviewStatus') != 'approved-static-visual':
        raise ValueError('Visual approval lacks the explicit static-raster scope/status')
    receipt = json.loads(_local(root, frame.get('userVisualReviewRecord')).read_text(encoding='utf-8-sig'))
    if (receipt.get('schemaVersion') != 1 or receipt.get('reviewType') != 'user-static-visual'
            or receipt.get('status') != 'approved' or receipt.get('scope') != STATIC_SCOPE):
        raise ValueError('User review receipt is not an approved static-raster review')
    if not EXCLUDED_SCOPES.issubset(set(receipt.get('exclusions', []))):
        raise ValueError('Static review receipt does not exclude the remaining unverified scopes')
    preview = receipt.get('preview', {})
    if _sha(_local(root, preview.get('file'))) != preview.get('sha256'):
        raise ValueError('Reviewed preview SHA differs from the receipt')
    source = receipt.get('source', {})
    if not all(isinstance(source.get(key), str) and source[key].strip() for key in ('question', 'answer')):
        raise ValueError('User review receipt lacks its explicit question/answer record')
    index = frame['sourceFrameIndex']
    representative = frame.get('imagePhaseRepresentativeIndex')
    matches = []
    for asset in receipt.get('assets', []):
        if asset.get('itemId') != item_id or asset.get('sourceFrameIndex') != representative:
            continue
        positions = asset.get('sourcePositions')
        if (not isinstance(positions, list) or not positions
                or any(type(position) is not int or position < 0 for position in positions)
                or len(set(positions)) != len(positions) or representative not in positions):
            raise ValueError('Receipt sourcePositions are not explicit valid source positions')
        if index in positions and asset.get('file') == frame['file'] and asset.get('sha256') == frame['sha256']:
            matches.append(asset)
    if len(matches) != 1:
        raise ValueError('User receipt does not uniquely approve this item/representative/position/file/SHA')
    if _sha(_local(root, frame['file'])) != matches[0]['sha256']:
        raise ValueError('Approved raster bytes changed after user review')
    return True
