#!/usr/bin/env python
"""校准Pillow宽度测量 vs PyMuPDF实际渲染宽度"""
import fitz
from PIL import ImageFont

font_msyh = ImageFont.truetype(r"C:\Windows\Fonts\msyh.ttc", 9)

# 测试文本
test = '    <text class="search-icon">'
b = font_msyh.getbbox(test)
pillow_w_px = b[2] - b[0]
pillow_w_pt = pillow_w_px * 0.75
print(f"Pillow getbbox: {b}")
print(f"Pillow width: {pillow_w_px}px = {pillow_w_pt:.2f}pt")

# PyMuPDF渲染并检查实际宽度
doc = fitz.open()
page = doc.new_page()
page.insert_text((45, 100), test, fontname="M", fontfile=r"C:\Windows\Fonts\msyh.ttc", fontsize=9)
doc.save(r"D:\AI project\app\账号密码记录\test_width.pdf")
doc.close()

doc2 = fitz.open(r"D:\AI project\app\账号密码记录\test_width.pdf")
blocks = doc2[0].get_text('dict')['blocks']
for b in blocks:
    if 'lines' in b:
        for l in b['lines']:
            for s in l['spans']:
                pw = s['bbox'][2] - s['bbox'][0]
                print(f"PyMuPDF actual width: {pw:.2f}pt")
                print(f"  bbox={s['bbox']}")
                print(f"  text len={len(s['text'])}")
                print(f"  avg char width={pw/len(s['text']):.2f}pt")
                # 校准因子
                scale = pw / pillow_w_pt
                print(f"  Calibration factor: {scale:.4f} (should be 1.0)")
doc2.close()
