"""Convert docx to PDF - copies files out of Protected View zone first"""
import os, shutil, win32com.client

BASE = r'C:\Users\王晓东\xwechat_files\wxid_rxic3kxnrvkt12_67bf\msg\file\2026-05'
WORK = r'C:\Users\王晓东\Documents\高岸管理\盈隆\高岸智能管理系统\高岸ERP\server'

files = [
    ('2023', '2023年广州市高中阶段学校招生第三批次录取工分数线(1).docx'),
    ('2024', '2024年广州市高中阶段学校招生第三批次录取分数线(1).docx'),
    ('2025', '2025年广州市高中阶段学校招生第三批次录取分数线(1).docx'),
]

word = win32com.client.DispatchEx("Word.Application")
word.Visible = False
word.DisplayAlerts = 0

for year, fname in files:
    src = os.path.join(BASE, fname)
    pdf_out = os.path.join(BASE, fname.replace('.docx', '_A4打印版.pdf'))
    work_file = os.path.join(WORK, f'temp_{year}_admission.docx')

    # Copy to working dir (avoid preserving read-only from source)
    shutil.copy(src, work_file)

    try:
        doc = word.Documents.Open(work_file)
        print(f"Opened: {fname[:20]}...")

        ps = doc.PageSetup
        ps.PageWidth = 29.7 * 28.35
        ps.PageHeight = 21.0 * 28.35
        ps.LeftMargin = 1.2 * 28.35
        ps.RightMargin = 1.2 * 28.35
        ps.TopMargin = 1.5 * 28.35
        ps.BottomMargin = 1.5 * 28.35

        # Set minimum font size for table headers
        for i in range(doc.Tables.Count):
            tbl = doc.Tables(i + 1)
            tbl.AutoFitBehavior(1)  # wdAutoFitContent
            tbl.AutoFitBehavior(2)  # wdAutoFitWindow
            tbl.PreferredWidthType = 2  # wdPreferredWidthPercent
            tbl.PreferredWidth = 100
            tbl.Range.Font.Size = 7
            tbl.Range.Font.Name = "微软雅黑"

        doc.SaveAs(pdf_out, FileFormat=17)
        doc.Close()
        sz = os.path.getsize(pdf_out)
        print(f"  -> PDF: {os.path.basename(pdf_out)} ({sz/1024:.0f}KB)")
    except Exception as e:
        print(f"  FAIL {year}: {e}")
        import traceback
        traceback.print_exc()
        try: doc.Close()
        except: pass
    finally:
        if os.path.exists(work_file):
            os.remove(work_file)

word.Quit()
print("\nAll done!")
