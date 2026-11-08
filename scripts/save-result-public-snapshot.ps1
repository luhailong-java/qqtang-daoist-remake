$ErrorActionPreference='Stop'
$projectRoot=(Resolve-Path -LiteralPath (Join-Path $PSScriptRoot '..')).Path
Set-Location -LiteralPath $projectRoot
$stage=Join-Path $projectRoot '.artifacts/git-upload-footprints-20261030'
$base='c39dd47f0a340bec1ad26e16cf2c039d9bb6874d'
$branch='codex/result-ui-20261102';$ref="refs/heads/$branch"
if((& git --git-dir=$stage rev-parse FETCH_HEAD).Trim() -ne $base){throw 'Unexpected verified baseline'}
& git --git-dir=$stage show-ref --verify --quiet $ref
if($LASTEXITCODE -ne 1){throw 'Snapshot ref already exists'}
$paths=@('README.md','art.html','src/app.js','src/ui-skin.css','src/art-review.js','src/result-art.js','tests/result-art.test.mjs',
  'docs/result-crests-v1.prompt.txt','docs/RESULT_UI_DELIVERY_20261102.md','docs/EYE_PUBLICATION_20261102.md',
  'docs/eye-adornments-public-snapshot.json','docs/eye-adornments-public-validation.json','docs/VALIDATION.md',
  'docs/GITHUB_PUBLICATION.md','docs/ART_COMPLETION_CHECKLIST.md','docs/REFERENCE_AUDIT.md',
  'qa/result-crests-native-ivory.png','qa/result-crests-display-contact.png','scripts/export-result-crests.py','scripts/save-result-public-snapshot.ps1')
$paths+=@(Get-ChildItem -LiteralPath 'assets/ui/results' -File|ForEach-Object{[IO.Path]::GetRelativePath($projectRoot,$_.FullName).Replace('\','/')})
$paths=@($paths|Sort-Object -Unique)
$inputs=@($paths|ForEach-Object{[ordered]@{path=$_;sha256=(Get-FileHash -LiteralPath $_ -Algorithm SHA256).Hash.ToLowerInvariant()}})
$normalHead=(& git rev-parse HEAD).Trim();$normalIndex=Join-Path $projectRoot '.git/index';$indexHash=(Get-FileHash -LiteralPath $normalIndex -Algorithm SHA256).Hash
$capture=Join-Path $projectRoot ('.artifacts/remote-ci/result-ui-20261102-'+[guid]::NewGuid().ToString('N').Substring(0,8));[void](New-Item -ItemType Directory -Path $capture)
$pathspec=Join-Path $capture 'paths.nul';[IO.File]::WriteAllBytes($pathspec,[Text.Encoding]::UTF8.GetBytes(($paths -join [char]0)+[char]0))
$previousIndex=$env:GIT_INDEX_FILE
try{
  $env:GIT_INDEX_FILE=Join-Path $capture 'private-index'
  & git --git-dir=$stage --work-tree=$projectRoot read-tree $base
  if($LASTEXITCODE -ne 0){throw 'Read baseline failed'}
  & git --git-dir=$stage --work-tree=$projectRoot --literal-pathspecs add "--pathspec-from-file=$pathspec" --pathspec-file-nul
  if($LASTEXITCODE -ne 0){throw 'Capture failed'}
  foreach($i in $inputs){if((Get-FileHash -LiteralPath $i.path -Algorithm SHA256).Hash.ToLowerInvariant() -ne $i.sha256){throw "Input changed: $($i.path)"}}
  $tree=(& git --git-dir=$stage write-tree --missing-ok).Trim();if($LASTEXITCODE -ne 0){throw 'Tree failed'}
  $commit=(& git --git-dir=$stage commit-tree $tree -p $base -m 'Add Daoist result crests and authoritative three-state UI').Trim();if($LASTEXITCODE -ne 0){throw 'Commit failed'}
  & git --git-dir=$stage update-ref $ref $commit ('0'*40);if($LASTEXITCODE -ne 0){throw 'Private ref failed'}
}finally{$env:GIT_INDEX_FILE=$previousIndex}
if((& git rev-parse HEAD).Trim() -ne $normalHead -or (Get-FileHash -LiteralPath $normalIndex -Algorithm SHA256).Hash -ne $indexHash){throw 'Normal HEAD/index changed'}
$record=[ordered]@{capturedAtUTC=[datetimeoffset]::UtcNow.ToString('o');branch=$branch;baseCommit=$base;commit=$commit;tree=$tree;inputs=$inputs;normalHeadAndIndexUnchanged=$true;remotePushComplete=$false;completeGameArt=$false;scope='Three result crests and authoritative outcome UI, readable text, exact provenance, and prior72 ornament publication receipt; no map geometry changes'}
$record|ConvertTo-Json -Depth 8|Set-Content -LiteralPath (Join-Path $capture 'source-snapshot.json') -Encoding utf8NoBOM
[ordered]@{capture=$capture;branch=$branch;commit=$commit;tree=$tree;inputs=$paths.Count;normalHeadAndIndexUnchanged=$true}|ConvertTo-Json
