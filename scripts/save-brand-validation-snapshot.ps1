$ErrorActionPreference = 'Stop'
$projectRoot = (Resolve-Path -LiteralPath (Join-Path $PSScriptRoot '..')).Path
Set-Location -LiteralPath $projectRoot
$baseCommit = '53ddb843f4e275b378ea4623d3d79d4ebacc453e'
$branchName = 'codex/linghu-brand-20261028'
$branchRef = "refs/heads/$branchName"
$priorSnapshot = Get-Content -LiteralPath '.artifacts/remote-ci/source-20261028-d842d461/source-snapshot.json' -Raw | ConvertFrom-Json
$selectedPaths = [System.Collections.Generic.HashSet[string]]::new([System.StringComparer]::Ordinal)
foreach ($entry in $priorSnapshot.inputs) { [void]$selectedPaths.Add([string]$entry.path) }
foreach ($directory in @('src','server','tests','assets/branding')) {
    foreach ($entry in Get-ChildItem -LiteralPath $directory -File -Recurse) {
        if ($entry.FullName -match '[\\/]__pycache__[\\/]' -or $entry.Extension -eq '.pyc') { continue }
        [void]$selectedPaths.Add([System.IO.Path]::GetRelativePath($projectRoot,$entry.FullName).Replace('\','/'))
    }
}
foreach ($entry in Get-ChildItem -LiteralPath $projectRoot -Filter '*.html' -File) { [void]$selectedPaths.Add($entry.Name) }
foreach ($relativePath in @('README.md','package.json','.github/workflows/source-validation.yml','.github/validation-scope.md',
    'scripts/index-map-animation-candidates.py','scripts/inspect-linghu-wordmark.py','scripts/export-linghu-wordmark.py',
    'scripts/save-brand-validation-snapshot.ps1','docs/GAME_IDENTITY_20261028.md','docs/REMOTE_CI_20261028.md',
    'docs/linghu-wordmark-v1.prompt.txt')) { [void]$selectedPaths.Add($relativePath) }
$pathsToSave = @($selectedPaths | Sort-Object)
$inputRecords = @($pathsToSave | ForEach-Object { [ordered]@{path=$_;sha256=(Get-FileHash -LiteralPath $_ -Algorithm SHA256).Hash.ToLowerInvariant()} })
$headBefore = (& git rev-parse HEAD).Trim()
if ($LASTEXITCODE -ne 0) { throw 'Cannot read HEAD' }
$normalIndexPath = Join-Path $projectRoot '.git/index'
$indexBefore = if (Test-Path -LiteralPath $normalIndexPath) { (Get-FileHash -LiteralPath $normalIndexPath -Algorithm SHA256).Hash } else { $null }
& git show-ref --verify --quiet $branchRef
if ($LASTEXITCODE -eq 0) { throw 'Snapshot branch already exists; do not replace it.' }
if ($LASTEXITCODE -ne 1) { throw 'Could not verify branch absence.' }
$captureDirectory = Join-Path $projectRoot ('.artifacts/remote-ci/brand-20261028-' + [guid]::NewGuid().ToString('N').Substring(0,8))
[void](New-Item -ItemType Directory -Path $captureDirectory)
$oldPrivateIndex = $env:GIT_INDEX_FILE
try {
    $env:GIT_INDEX_FILE = Join-Path $captureDirectory 'private-index'
    & git read-tree $baseCommit
    if ($LASTEXITCODE -ne 0) { throw 'Private-index baseline failed' }
    & git add -- @pathsToSave
    if ($LASTEXITCODE -ne 0) { throw 'Snapshot paths could not be added' }
    foreach ($record in $inputRecords) {
        if ((Get-FileHash -LiteralPath $record.path -Algorithm SHA256).Hash.ToLowerInvariant() -ne $record.sha256) { throw "Input changed during capture: $($record.path)" }
    }
    $treeId = (& git write-tree).Trim()
    if ($LASTEXITCODE -ne 0) { throw 'Cannot save private tree' }
    $commitId = (& git commit-tree $treeId -p $baseCommit -m 'Adopt Linghu game name, title art and expanded candidate review').Trim()
    if ($LASTEXITCODE -ne 0) { throw 'Cannot create fixed snapshot commit' }
    & git update-ref $branchRef $commitId ('0' * 40)
    if ($LASTEXITCODE -ne 0) { throw 'Cannot register new snapshot branch' }
} finally {
    $env:GIT_INDEX_FILE = $oldPrivateIndex
}
$headAfter = (& git rev-parse HEAD).Trim()
$indexAfter = if (Test-Path -LiteralPath $normalIndexPath) { (Get-FileHash -LiteralPath $normalIndexPath -Algorithm SHA256).Hash } else { $null }
if ($headBefore -ne $headAfter -or $indexBefore -ne $indexAfter) { throw 'Normal working HEAD or index changed unexpectedly' }
$changed = @(& git diff-tree --no-commit-id --name-only -r $commitId)
$snapshot = [ordered]@{capturedAt=[datetimeoffset]::Now.ToString('o');branch=$branchName;baseCommit=$baseCommit;commit=$commitId;tree=$treeId;
    scope='current source and selected new title branding; all other new art excluded';changedPathCount=$changed.Count;
    inputs=$inputRecords;localTestsRun=$false;localBuildRun=$false;normalHeadAndIndexUnchanged=$true;remotePushComplete=$false}
$snapshotPath = Join-Path $captureDirectory 'source-snapshot.json'
$snapshot | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath $snapshotPath -Encoding utf8NoBOM
[ordered]@{snapshot=$snapshotPath;branch=$branchName;commit=$commitId;tree=$treeId;changedPaths=$changed.Count;localTestsRun=$false;normalHeadAndIndexUnchanged=$true} | ConvertTo-Json
