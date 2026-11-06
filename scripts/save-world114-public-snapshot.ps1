$ErrorActionPreference='Stop'
$projectRoot=(Resolve-Path -LiteralPath (Join-Path $PSScriptRoot '..')).Path
Set-Location -LiteralPath $projectRoot
$stage=Join-Path $projectRoot '.artifacts/git-upload-footprints-20261030'
$base='ed928050b39adaa5a745a12065203138e4de65be'
$branch='codex/world114-20261102';$ref="refs/heads/$branch"
if((& git --git-dir=$stage rev-parse FETCH_HEAD).Trim() -ne $base){throw 'Unexpected verified baseline'}
& git --git-dir=$stage show-ref --verify --quiet $ref
if($LASTEXITCODE -ne 1){throw 'Snapshot ref already exists'}
$selected=[System.Collections.Generic.HashSet[string]]::new([StringComparer]::Ordinal)
foreach($folder in @('assets/items/head-adornments/world/114','assets/items/head-adornments/references/world/114')){
 foreach($f in Get-ChildItem -LiteralPath $folder -Recurse -File){if($f.Extension -ne '.pyc'){[void]$selected.Add([IO.Path]::GetRelativePath($projectRoot,$f.FullName).Replace('\','/'))}}
}
foreach($pattern in @('world-114-*','114-*.json','114-*.png*')){foreach($f in Get-ChildItem -LiteralPath 'assets/items/head-adornments/exports' -File -Filter $pattern){[void]$selected.Add([IO.Path]::GetRelativePath($projectRoot,$f.FullName).Replace('\','/'))}}
foreach($folder in @('assets/items/head-adornments/world','assets/items/head-adornments/prompts')){foreach($f in Get-ChildItem -LiteralPath $folder -File -Filter '*114-*'){[void]$selected.Add([IO.Path]::GetRelativePath($projectRoot,$f.FullName).Replace('\','/'))}}
foreach($f in @('art.html','src/art-review.js','src/art-review-data.js','.github/workflows/source-validation.yml',
 'scripts/verify-head-world-114.py','scripts/save-world114-public-snapshot.ps1',
 'assets/items/head-adornments/world-114-art.json','assets/items/head-adornments/docs/WORLD_114_SOURCE_CONTRACT.md',
 'assets/items/head-adornments/icons/114-rose-silk-garland.png','assets/items/head-adornments/prepare_114_batches.py',
 'assets/items/head-adornments/register_world_batch.py','assets/items/head-adornments/export_world_batch.py',
 'assets/items/head-adornments/prepare_phase_references.py','assets/items/head-adornments/prepare_export_contract.py',
 'assets/items/head-adornments/make_phase_reference_board.py','assets/items/head-adornments/complete_raster_aliases.py',
 'references/qqtang-item-data/icons/item-114-inventory-icon.png','references/qqtang-item-data/icons/item-114-inventory-icon.png.source.json',
 'docs/RESULT_UI_PUBLICATION_20261102.md','docs/ART_PRODUCTION_STATUS_20261028.json','docs/ART_COMPLETION_CHECKLIST.md',
 'docs/VALIDATION.md','docs/GITHUB_PUBLICATION.md')){[void]$selected.Add($f)}
$paths=@($selected|Sort-Object)
$inputs=@($paths|ForEach-Object{[ordered]@{path=$_;sha256=(Get-FileHash -LiteralPath $_ -Algorithm SHA256).Hash.ToLowerInvariant()}})
$normalHead=(& git rev-parse HEAD).Trim();$normalIndex=Join-Path $projectRoot '.git/index';$indexHash=(Get-FileHash -LiteralPath $normalIndex -Algorithm SHA256).Hash
$capture=Join-Path $projectRoot ('.artifacts/remote-ci/world114-20261102-'+[guid]::NewGuid().ToString('N').Substring(0,8));[void](New-Item -ItemType Directory -Path $capture)
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
 $commit=(& git --git-dir=$stage commit-tree $tree -p $base -m 'Add20 Daoist rose garland rasters with24 exact source positions').Trim();if($LASTEXITCODE -ne 0){throw 'Commit failed'}
 & git --git-dir=$stage update-ref $ref $commit ('0'*40);if($LASTEXITCODE -ne 0){throw 'Private ref failed'}
}finally{$env:GIT_INDEX_FILE=$previousIndex}
if((& git rev-parse HEAD).Trim() -ne $normalHead -or (Get-FileHash -LiteralPath $normalIndex -Algorithm SHA256).Hash -ne $indexHash){throw 'Normal HEAD/index changed'}
$record=[ordered]@{capturedAtUTC=[datetimeoffset]::UtcNow.ToString('o');branch=$branch;baseCommit=$base;commit=$commit;tree=$tree;inputs=$inputs;normalHeadAndIndexUnchanged=$true;remotePushComplete=$false;completeGameArt=$false;scope='Item114 only:20 painted world rasters,24 source positions, exact dimensions/raw offsets and reference evidence, gallery diagnostic and prior result UI publication receipt; other head world art not included'}
$record|ConvertTo-Json -Depth 8|Set-Content -LiteralPath (Join-Path $capture 'source-snapshot.json') -Encoding utf8NoBOM
[ordered]@{capture=$capture;branch=$branch;commit=$commit;tree=$tree;inputs=$paths.Count;bytes=($paths|ForEach-Object{(Get-Item -LiteralPath $_).Length}|Measure-Object -Sum).Sum;normalHeadAndIndexUnchanged=$true}|ConvertTo-Json
