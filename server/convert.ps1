$base = "C:\Users\王晓东\xwechat_files\wxid_rxic3kxnrvkt12_67bf\msg\file\2026-05"
$files = @(
    "2023年广州市高中阶段学校招生第三批次录取工分数线(1).docx",
    "2024年广州市高中阶段学校招生第三批次录取分数线(1).docx",
    "2025年广州市高中阶段学校招生第三批次录取分数线(1).docx"
)

try {
    $word = New-Object -ComObject Word.Application
    $word.Visible = $false
    $word.DisplayAlerts = 0
    Write-Host "Word started successfully"
} catch {
    Write-Host "Failed to start Word: $_"
    exit 1
}

foreach ($fname in $files) {
    $src = Join-Path $base $fname
    $pdf = $src -replace '\.docx$', '_A4打印版.pdf'

    if (-not (Test-Path $src)) {
        Write-Host "NOT FOUND: $fname"
        continue
    }

    try {
        Write-Host "Opening: $fname"
        $doc = $word.Documents.Open($src)

        $ps = $doc.PageSetup
        $ps.PageWidth = 29.7 * 28.35
        $ps.PageHeight = 21.0 * 28.35
        $ps.LeftMargin = 1.2 * 28.35
        $ps.RightMargin = 1.2 * 28.35
        $ps.TopMargin = 1.5 * 28.35
        $ps.BottomMargin = 1.5 * 28.35

        $count = $doc.Tables.Count
        Write-Host "  Tables: $count"

        for ($i = 1; $i -le $count; $i++) {
            $tbl = $doc.Tables.Item($i)
            $tbl.Range.Select()
            $word.Selection.Tables.AutoFitBehavior(1)
            $word.Selection.Tables.AutoFitBehavior(2)
            $tbl.PreferredWidthType = 2  # wdPreferredWidthPercent
            $tbl.PreferredWidth = 100
            $tbl.Range.Font.Size = 7
            $tbl.Range.Font.Name = "微软雅黑"
        }

        $ps.FitToPagesWide = 1
        $ps.FitToPagesTall = 0

        # wdFormatPDF = 17
        $doc.SaveAs([ref] $pdf, [ref] 17)
        $doc.Close()
        $sz = (Get-Item $pdf).Length
        Write-Host "  OK: $((Get-Item $pdf).Name) ($([math]::Round($sz/1024))KB)"
    } catch {
        Write-Host "  FAIL: $_"
        try { $doc.Close() } catch {}
    }
}

$word.Quit()
[System.Runtime.Interopservices.Marshal]::ReleaseComObject($word) | Out-Null
Remove-Variable word
Write-Host "`nAll done!"
