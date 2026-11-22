param([string]$TrinhDuyet = '')
$ErrorActionPreference = 'Stop'
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$tsRoot = (Resolve-Path -LiteralPath (Join-Path $PSScriptRoot '../../..')).Path
Set-Location -LiteralPath $tsRoot
if (-not $TrinhDuyet) {
    $TrinhDuyet = Join-Path $env:ProgramFiles 'Google/Chrome/Application/chrome.exe'
    if (-not (Test-Path -LiteralPath $TrinhDuyet)) {
        $TrinhDuyet = Join-Path ${env:ProgramFiles(x86)} 'Microsoft/Edge/Application/msedge.exe'
    }
}
if (-not (Test-Path -LiteralPath $TrinhDuyet)) { throw 'Can Chromium de chup anh DEMO.' }
node e_phan_luong/tests/ui/dung_anh.mjs .venv/ui-ts-pl-DEMO.html
if ($LASTEXITCODE) { throw 'Khong dung duoc trang DEMO.' }
New-Item -ItemType Directory -Force -Path 'e_phan_luong/tests/ui/anh' | Out-Null
$tsBase = 'file:///' + ($tsRoot -replace '\\','/') + '/.venv/ui-ts-pl-DEMO.html'
$tsScenes = @(
    @{Ten='danh-muc'; The='danh_muc_loai_json'; W=1200; H=1000; Mode=''},
    @{Ten='phan-loai'; The='bo_phan_loai_json'; W=1200; H=2250; Mode=''},
    @{Ten='khuon-cot'; The='khuon_cot_json'; W=1200; H=3600; Mode=''},
    @{Ten='di-dong-loi'; The='nguong_json'; W=500; H=1700; Mode='loi'},
    @{Ten='cas'; The='nguong_json'; W=1200; H=1150; Mode='cas'},
    @{Ten='nguong-chinh-sach'; The='nguong_json,chinh_sach_json'; W=1200; H=1770; Mode=''}
)
foreach ($tsScene in $tsScenes) {
    $tsUrl = $tsBase + '?the=' + $tsScene.The + '&che_do=' + $tsScene.Mode
    $tsStem = 'ts-pl-' + $tsScene.Ten
    $tsProfile = Join-Path $tsRoot ('.venv/chrome-DEMO-' + $tsStem)
    $tsAnh = Join-Path $tsRoot ('e_phan_luong/tests/ui/anh/' + $tsStem + '.png')
    $tsArgs = @('--headless','--no-sandbox','--disable-gpu','--in-process-gpu',
        '--no-first-run','--no-default-browser-check','--disable-background-networking',
        '--disable-component-update','--hide-scrollbars','--force-device-scale-factor=1',
        ('--user-data-dir="' + $tsProfile + '"'),
        ('--window-size=' + $tsScene.W + ',' + $tsScene.H), '--virtual-time-budget=3000',
        ('--screenshot="' + $tsAnh + '"'), '--dump-dom', $tsUrl)
    $tsDomPath = '.venv/' + $tsStem + '-dom.txt'
    $tsProc = Start-Process -FilePath $TrinhDuyet -ArgumentList $tsArgs -WindowStyle Hidden `
        -Wait -PassThru -RedirectStandardOutput $tsDomPath `
        -RedirectStandardError ('.venv/' + $tsStem + '-browser.txt')
    $tsDom = Get-Content -Raw -Encoding UTF8 -LiteralPath $tsDomPath
    if ($tsProc.ExitCode -ne 0 -or -not $tsDom.Contains('data-demo-da-dung="true"')) {
        throw ('Khong dung duoc anh DEMO: ' + $tsStem)
    }
    if ($tsDom.Contains('data-tran-ngang="true"')) { throw ('Man tran ngang: ' + $tsStem) }
    Get-Item -LiteralPath $tsAnh | Select-Object Name, Length
}
