"""Check inventory evidence without treating an explicit stand frame as an icon."""


def validate_source_reference(entry, original, record, actual_sha, exception=None):
    ident = original['item_id']
    if record.get('itemId') != ident or record.get('category') != original['category']:
        raise ValueError('Reference identity disagrees with catalog')
    if record.get('file') != entry['sourceReference'] or record.get('sha256') != actual_sha:
        raise ValueError('Reference file/hash disagrees with evidence')
    member = record.get('sourceMember', '')
    installed = original['installed_files']
    if not any(member.endswith('/' + path) for path in installed):
        raise ValueError('Reference member is not catalog-declared')
    if record.get('sourceSha256') != record.get('dimg', {}).get('sha256'):
        raise ValueError('Source container evidence disagrees')
    inventory = [path for path in installed if path.startswith('res/uiRes/icon/')]
    if exception is None:
        if len(inventory) != 1 or not member.endswith('/' + inventory[0]):
            raise ValueError('Actual inventory reference required; no implicit stand fallback')
        if record.get('resourceKind') != 'explicit inventory icon':
            raise ValueError('Reference is not explicitly an inventory icon')
        return 'inventory'
    if inventory:
        raise ValueError('Stand exception cannot replace an available inventory icon')
    expected = {'itemId': ident, 'sourceReference': entry['sourceReference'],
                'referenceSha256': actual_sha, 'sourceMember': member,
                'sourceSha256': record.get('sourceSha256'),
                'sourceFrameIndex': record.get('sourceFrameIndex')}
    if any(exception.get(key) != value for key, value in expected.items()):
        raise ValueError('Stand exception differs from its fixed evidence')
    if record.get('resourceKind') != 'explicit installed stand' or not exception.get('reason'):
        raise ValueError('Stand exception kind/reason missing')
    if entry.get('inventoryMappingVerified') is not False:
        raise ValueError('Unresolved inventory mapping must remain false')
    if any(entry.get(flag) is not False for flag in ('visualAccepted', 'worldAccepted', 'stateAccepted', 'runtimeAdopted')):
        raise ValueError('Stand evidence does not authorize adoption')
    return 'stand-exception'
