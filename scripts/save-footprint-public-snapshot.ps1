$ErrorActionPreference='Stop'
$projectRoot=(Resolve-Path -LiteralPath (Join-Path $PSScriptRoot '..')).Path
Set-Location -LiteralPath $projectRoot
$stage=Join-Path $projectRoot '.artifacts/git-upload-footprints-20261030'
$base='de82b6054891bcedb1c14562e08bdfe6a1a6eca5'
$branch='codex/footprints-20261030'
$ref="refs/heads/$branch"
if((& git --git-dir=$stage rev-parse HEAD).Trim() -ne $base){throw 'Unexpected verified remote baseline'}
& git --git-dir=$stage show-ref --verify --quiet $ref
if($LASTEXITCODE -ne 1){throw 'Snapshot ref already exists or cannot be checked'}
$selected=[System.Collections.Generic.HashSet[string]]::new([StringComparer]::Ordinal)
foreach($folder in @('assets/items/footprints','assets/items/surroundings','references/image')){
  foreach($f in Get-ChildItem -LiteralPath $folder -File -Recurse){if($f.Extension -ne '.pyc' -and $f.FullName -notmatch '[\\/]__pycache__[\\/]'){[void]$selected.Add([IO.Path]::GetRelativePath($projectRoot,$f.FullName).Replace('\','/'))}}
}
$catalog=Get-Content -LiteralPath 'references/qqtang-item-data/catalog.json' -Raw | ConvertFrom-Json
foreach($i in @($catalog.items | Where-Object {$_.category -in @('ear','footprint')})){
  foreach($suffix in @('.png','.png.source.json')){[void]$selected.Add("references/qqtang-item-data/icons/item-$($i.item_id)-inventory-icon$suffix")}
}
foreach($pattern in @('surroundings-*-inventory.png*')){foreach($f in Get-ChildItem -LiteralPath 'references/qqtang-item-data/visual-reference' -Filter $pattern -File){[void]$selected.Add([IO.Path]::GetRelativePath($projectRoot,$f.FullName).Replace('\','/'))}}
foreach($pattern in @('footprints-*-contact-256.png*','surroundings-*-contact-256.png*')){foreach($f in Get-ChildItem -LiteralPath 'qa' -Filter $pattern -File){[void]$selected.Add([IO.Path]::GetRelativePath($projectRoot,$f.FullName).Replace('\','/'))}}
foreach($pattern in @('footprints-*.json','footprints-*.prompt.txt','surroundings-*.json','surroundings-*.prompt.txt','FOOTPRINT*.md','SURROUNDING*.md')){foreach($f in Get-ChildItem -LiteralPath 'docs' -Filter $pattern -File){[void]$selected.Add([IO.Path]::GetRelativePath($projectRoot,$f.FullName).Replace('\','/'))}}
foreach($f in @('art.html','src/art-review.js','.github/workflows/source-validation.yml','.github/footprints-scope.md',
  'references/qqtang-item-data/catalog.json','docs/GITHUB_PUBLICATION.md','docs/VALIDATION.md','docs/LOCAL_RESOURCE_WINDOW_20261028.md',
  'scripts/register-generated-image.mjs','scripts/mark-generation-edit.mjs','scripts/extract-item-art-reference.py',
  'scripts/make-item-structure-board.py','scripts/export-item-art.py','scripts/preview-item-batch.py','scripts/inspect-footprint-reference.py',
  'scripts/verify-inventory-candidates.py','scripts/save-footprint-public-snapshot.ps1')){[void]$selected.Add($f)}
$paths=@($selected | Sort-Object)
$inputs=@($paths | ForEach-Object{[ordered]@{path=$_;sha256=(Get-FileHash -LiteralPath $_ -Algorithm SHA256).Hash.ToLowerInvariant()}})
$normalHead=(& git rev-parse HEAD).Trim();$normalIndex=Join-Path $projectRoot '.git/index';$indexHash=(Get-FileHash -LiteralPath $normalIndex -Algorithm SHA256).Hash
$capture=Join-Path $projectRoot ('.artifacts/remote-ci/footprints-20261030-'+[guid]::NewGuid().ToString('N').Substring(0,8));[void](New-Item -ItemType Directory -Path $capture)
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
  $commit=(& git --git-dir=$stage commit-tree $tree -p $base -m 'Add74 original Daoist footprint inventory candidates and delivery evidence').Trim();if($LASTEXITCODE -ne 0){throw 'Commit failed'}
  & git --git-dir=$stage update-ref $ref $commit ('0'*40);if($LASTEXITCODE -ne 0){throw 'New snapshot ref failed'}
}finally{$env:GIT_INDEX_FILE=$previousIndex}
if((& git rev-parse HEAD).Trim() -ne $normalHead -or (Get-FileHash -LiteralPath $normalIndex -Algorithm SHA256).Hash -ne $indexHash){throw 'Normal HEAD/index changed'}
$record=[ordered]@{capturedAtUTC=[datetimeoffset]::UtcNow.ToString('o');branch=$branch;baseCommit=$base;commit=$commit;tree=$tree;inputs=$inputs;normalHeadAndIndexUnchanged=$true;remotePushComplete=$false;completeGameArt=$false;scope='74 footprint inventory candidates plus complete62 surrounding inventory and required source/review/validation files; other art inherited baseline only'}
$record | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath (Join-Path $capture 'source-snapshot.json') -Encoding utf8NoBOM
[ordered]@{capture=$capture;branch=$branch;commit=$commit;tree=$tree;inputs=$paths.Count;normalHeadAndIndexUnchanged=$true}|ConvertTo-Json
