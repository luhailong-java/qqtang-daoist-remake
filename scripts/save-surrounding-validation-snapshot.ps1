$ErrorActionPreference='Stop'
$projectRoot=(Resolve-Path -LiteralPath (Join-Path $PSScriptRoot '..')).Path
Set-Location -LiteralPath $projectRoot
$baseCommit='16ab7b07fe36532b30c8ebb8a0ea9842ce01454a'
$branchName='codex/surroundings-20261029'
$branchRef="refs/heads/$branchName"
$previous=Get-Content -LiteralPath '.artifacts/remote-ci/brand-20261028-b2a3f0e5/source-snapshot.json' -Raw | ConvertFrom-Json
$selected=[System.Collections.Generic.HashSet[string]]::new([System.StringComparer]::Ordinal)
foreach($entry in $previous.inputs){[void]$selected.Add([string]$entry.path)}
foreach($folder in @('src','server','tests','assets/items/surroundings')){
  foreach($file in Get-ChildItem -LiteralPath $folder -File -Recurse){
    if($file.FullName -match '[\\/]__pycache__[\\/]' -or $file.Extension -eq '.pyc'){continue}
    [void]$selected.Add([IO.Path]::GetRelativePath($projectRoot,$file.FullName).Replace('\','/'))
  }
}
$catalog=Get-Content -LiteralPath 'references/qqtang-item-data/catalog.json' -Raw | ConvertFrom-Json
foreach($item in @($catalog.items | Where-Object category -eq 'ear')){
  [void]$selected.Add("references/qqtang-item-data/icons/item-$($item.item_id)-inventory-icon.png")
  [void]$selected.Add("references/qqtang-item-data/icons/item-$($item.item_id)-inventory-icon.png.source.json")
}
foreach($pattern in @('surroundings-*-inventory.png','surroundings-*-inventory.png.source.json')){
  foreach($file in Get-ChildItem -LiteralPath 'references/qqtang-item-data/visual-reference' -Filter $pattern -File){[void]$selected.Add([IO.Path]::GetRelativePath($projectRoot,$file.FullName).Replace('\','/'))}
}
foreach($pattern in @('surroundings-*-contact-256.png','surroundings-*-contact-256.png.provenance.json')){
  foreach($file in Get-ChildItem -LiteralPath 'qa' -Filter $pattern -File){[void]$selected.Add([IO.Path]::GetRelativePath($projectRoot,$file.FullName).Replace('\','/'))}
}
foreach($pattern in @('surroundings-*-export.json','surroundings-*-v*.prompt.txt')){
  foreach($file in Get-ChildItem -LiteralPath 'docs' -Filter $pattern -File){[void]$selected.Add([IO.Path]::GetRelativePath($projectRoot,$file.FullName).Replace('\','/'))}
}
foreach($file in @('README.md','package.json','art.html','.github/workflows/source-validation.yml','.github/surroundings-scope.md',
  'references/qqtang-item-data/catalog.json','docs/SURROUNDING_INVENTORY_DELIVERY_20261029.md','docs/SURROUNDING_MOTION_CONTRACT_20261028.md',
  'scripts/extract-item-art-reference.py','scripts/make-item-structure-board.py','scripts/export-item-art.py','scripts/preview-item-batch.py',
  'scripts/inspect-surrounding-metadata.py','scripts/extract-surrounding-frame-reference.py','scripts/snapshot-surrounding-production.py',
  'scripts/verify-inventory-candidates.py','scripts/save-surrounding-validation-snapshot.ps1','scripts/register-generated-image.mjs')){[void]$selected.Add($file)}
$paths=@($selected | Sort-Object)
$inputs=@($paths | ForEach-Object{[ordered]@{path=$_;sha256=(Get-FileHash -LiteralPath $_ -Algorithm SHA256).Hash.ToLowerInvariant()}})
$headBefore=(& git rev-parse HEAD).Trim()
if($LASTEXITCODE -ne 0){throw 'Cannot read normal HEAD'}
$normalIndex=Join-Path $projectRoot '.git/index'
$indexBefore=if(Test-Path -LiteralPath $normalIndex){(Get-FileHash -LiteralPath $normalIndex -Algorithm SHA256).Hash}else{$null}
& git show-ref --verify --quiet $branchRef
if($LASTEXITCODE -eq 0){throw 'Snapshot branch exists; do not replace it'}
if($LASTEXITCODE -ne 1){throw 'Cannot establish branch absence'}
$capture=Join-Path $projectRoot ('.artifacts/remote-ci/surroundings-20261029-'+[guid]::NewGuid().ToString('N').Substring(0,8))
[void](New-Item -ItemType Directory -Path $capture)
$pathspec=Join-Path $capture 'paths.nul'
[IO.File]::WriteAllBytes($pathspec,[Text.Encoding]::UTF8.GetBytes(($paths -join [char]0)+[char]0))
$oldIndex=$env:GIT_INDEX_FILE
try{
  $env:GIT_INDEX_FILE=Join-Path $capture 'private-index'
  & git read-tree $baseCommit
  if($LASTEXITCODE -ne 0){throw 'Private baseline read failed'}
  & git --literal-pathspecs add "--pathspec-from-file=$pathspec" --pathspec-file-nul
  if($LASTEXITCODE -ne 0){throw 'Private path capture failed'}
  foreach($inputFile in $inputs){if((Get-FileHash -LiteralPath $inputFile.path -Algorithm SHA256).Hash.ToLowerInvariant() -ne $inputFile.sha256){throw "Input changed during capture: $($inputFile.path)"}}
  $treeId=(& git write-tree).Trim()
  if($LASTEXITCODE -ne 0){throw 'Cannot save tree'}
  $commitId=(& git commit-tree $treeId -p $baseCommit -m 'Add62 Daoist cosmetic inventory candidates and bounded PNG verification').Trim()
  if($LASTEXITCODE -ne 0){throw 'Cannot save commit'}
  & git update-ref $branchRef $commitId ('0'*40)
  if($LASTEXITCODE -ne 0){throw 'Cannot create new branch ref'}
}finally{$env:GIT_INDEX_FILE=$oldIndex}
$headAfter=(& git rev-parse HEAD).Trim()
$indexAfter=if(Test-Path -LiteralPath $normalIndex){(Get-FileHash -LiteralPath $normalIndex -Algorithm SHA256).Hash}else{$null}
if($headBefore -ne $headAfter -or $indexBefore -ne $indexAfter){throw 'Normal HEAD/index unexpectedly changed'}
$changed=@(& git diff-tree --no-commit-id --name-only -r $commitId)
$snapshot=[ordered]@{capturedAt=[datetimeoffset]::Now.ToString('o');branch=$branchName;baseCommit=$baseCommit;commit=$commitId;tree=$treeId;
  scope='62 source ear inventory candidates and required references/metadata/current source; other new art excluded';changedPathCount=$changed.Count;
  inputs=$inputs;localTestsRun=$false;localBuildRun=$false;localPixelValidationRun=$false;normalHeadAndIndexUnchanged=$true;remotePushComplete=$false}
$snapshotPath=Join-Path $capture 'source-snapshot.json'
$snapshot | ConvertTo-Json -Depth 9 | Set-Content -LiteralPath $snapshotPath -Encoding utf8NoBOM
[ordered]@{snapshot=$snapshotPath;branch=$branchName;commit=$commitId;tree=$treeId;changedPaths=$changed.Count;inputFiles=$paths.Count;localTestsRun=$false;normalHeadAndIndexUnchanged=$true}|ConvertTo-Json
