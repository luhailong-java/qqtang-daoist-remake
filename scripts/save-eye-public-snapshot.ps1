$ErrorActionPreference='Stop'
$projectRoot=(Resolve-Path -LiteralPath (Join-Path $PSScriptRoot '..')).Path
Set-Location -LiteralPath $projectRoot
$stage=Join-Path $projectRoot '.artifacts/git-upload-footprints-20261030'
$base='9be287bfb65d110c0664970265b2d898a22c75c2'
$branch='codex/eye-inventory-20261102'
$ref="refs/heads/$branch"
if((& git --git-dir=$stage rev-parse FETCH_HEAD).Trim() -ne $base){throw 'Unexpected verified remote baseline'}
& git --git-dir=$stage show-ref --verify --quiet $ref
if($LASTEXITCODE -ne 1){throw 'Snapshot ref already exists or cannot be checked'}
$selected=[System.Collections.Generic.HashSet[string]]::new([StringComparer]::Ordinal)
foreach($f in Get-ChildItem -LiteralPath 'assets/items/eye-adornments' -File -Recurse){[void]$selected.Add([IO.Path]::GetRelativePath($projectRoot,$f.FullName).Replace('\','/'))}
$art=Get-Content -LiteralPath 'assets/items/eye-adornments/art.json' -Raw | ConvertFrom-Json
if($art.items.Count -ne 72){throw 'Expected72 candidates'}
foreach($item in $art.items){[void]$selected.Add($item.sourceReference);[void]$selected.Add($item.sourceReference+'.source.json')}
foreach($pattern in @('eye-adornments-*.json','eye-adornments-*.prompt.txt','EYE_*.md')){foreach($f in Get-ChildItem -LiteralPath 'docs' -Filter $pattern -File){[void]$selected.Add([IO.Path]::GetRelativePath($projectRoot,$f.FullName).Replace('\','/'))}}
foreach($f in Get-ChildItem -LiteralPath 'scripts' -Filter 'eye-adornments-*' -File){[void]$selected.Add([IO.Path]::GetRelativePath($projectRoot,$f.FullName).Replace('\','/'))}
foreach($f in @('README.md','art.html','src/art-review.js','.github/workflows/source-validation.yml',
  'docs/IMAGE_CONFIG_VERIFICATION_20261101.md','docs/ART_PRODUCTION_STATUS_20261028.json','docs/ART_COMPLETION_CHECKLIST.md',
  'docs/VALIDATION.md','docs/GITHUB_PUBLICATION.md','docs/LOCAL_RESOURCE_WINDOW_20261028.md',
  'qa/eye-adornments-small-size.png','qa/eye-adornments-small-size.png.source.json',
  'scripts/verify-inventory-candidates.py','scripts/inventory_reference_contract.py','scripts/preview-eye-inventory.py',
  'scripts/save-eye-public-snapshot.ps1','tests/inventory-reference-contract.test.py')){[void]$selected.Add($f)}
$paths=@($selected | Sort-Object)
$inputs=@($paths | ForEach-Object{[ordered]@{path=$_;sha256=(Get-FileHash -LiteralPath $_ -Algorithm SHA256).Hash.ToLowerInvariant()}})
$normalHead=(& git rev-parse HEAD).Trim();$normalIndex=Join-Path $projectRoot '.git/index';$indexHash=(Get-FileHash -LiteralPath $normalIndex -Algorithm SHA256).Hash
$capture=Join-Path $projectRoot ('.artifacts/remote-ci/eye-inventory-20261102-'+[guid]::NewGuid().ToString('N').Substring(0,8));[void](New-Item -ItemType Directory -Path $capture)
$pathspec=Join-Path $capture 'paths.nul';[IO.File]::WriteAllBytes($pathspec,[Text.Encoding]::UTF8.GetBytes(($paths -join [char]0)+[char]0))
$previousIndex=$env:GIT_INDEX_FILE
try{
  $env:GIT_INDEX_FILE=Join-Path $capture 'private-index'
  & git --git-dir=$stage --work-tree=$projectRoot read-tree $base
  if($LASTEXITCODE -ne 0){throw 'Baseline tree read failed'}
  & git --git-dir=$stage --work-tree=$projectRoot --literal-pathspecs add "--pathspec-from-file=$pathspec" --pathspec-file-nul
  if($LASTEXITCODE -ne 0){throw 'Fixed path capture failed'}
  foreach($i in $inputs){if((Get-FileHash -LiteralPath $i.path -Algorithm SHA256).Hash.ToLowerInvariant() -ne $i.sha256){throw "Input changed: $($i.path)"}}
  $treeOutput=& git --git-dir=$stage write-tree --missing-ok
  if($LASTEXITCODE -ne 0 -or -not $treeOutput){throw 'Tree failed'}
  $tree=$treeOutput.Trim()
  $commit=(& git --git-dir=$stage commit-tree $tree -p $base -m 'Add72 original Daoist ornament inventory candidates and strict source evidence checks').Trim()
  if($LASTEXITCODE -ne 0){throw 'Commit failed'}
  & git --git-dir=$stage update-ref $ref $commit ('0'*40)
  if($LASTEXITCODE -ne 0){throw 'New snapshot ref failed'}
}finally{$env:GIT_INDEX_FILE=$previousIndex}
if((& git rev-parse HEAD).Trim() -ne $normalHead -or (Get-FileHash -LiteralPath $normalIndex -Algorithm SHA256).Hash -ne $indexHash){throw 'Normal HEAD/index changed'}
$record=[ordered]@{capturedAtUTC=[datetimeoffset]::UtcNow.ToString('o');branch=$branch;baseCommit=$base;commit=$commit;tree=$tree;inputs=$inputs;normalHeadAndIndexUnchanged=$true;remotePushComplete=$false;completeGameArt=$false;scope='72 ornament inventory candidates, explicit71 inventory and1 stand source references, review boards and provenance checks; other art inherited from baseline only'}
$record | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath (Join-Path $capture 'source-snapshot.json') -Encoding utf8NoBOM
[ordered]@{capture=$capture;branch=$branch;commit=$commit;tree=$tree;inputs=$paths.Count;bytes=($inputs|ForEach-Object{(Get-Item -LiteralPath $_.path).Length}|Measure-Object -Sum).Sum;normalHeadAndIndexUnchanged=$true}|ConvertTo-Json
