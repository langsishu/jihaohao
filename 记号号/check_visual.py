#!/usr/bin/env python
"""视觉验证PDF - 检查emoji是否可见"""
import fitz
doc = fitz.open(r'D:\AI project\app\账号密码记录\记号号工具软件V1.0_源程序鉴别材料.pdf')

# 第1页转图片查看
page = doc[0]
pix = page.get_pixmap(dpi=200)
pix.save(r'D:\AI project\app\账号密码记录\page1_check.png')

# 分析文本块详情查看嵌套标签
blocks = page.get_text('dict')['blocks']
print("=== 第1页文本块详情（关注emoji行）=== ")
for b in blocks:
    if 'lines' in b:
        for l in b['lines']:
            for s in l['spans']:
                txt = s['text']
                y = s['bbox'][1]
                if 85 < y < 115:  # 第5-7行附近
                    print(f"  y={y:.1f} font={s['font']}")
                    print(f"    bbox={s['bbox']}")
                    print(f"    text={repr(txt[:60])}")
                    print()

# 统计空字符在每页的分布
print("=== 空字符分布 ===")
for i in range(len(doc)):
    tx = doc[i].get_text()
    nc = tx.count(chr(0))
    if nc > 0:
        # 找到包含空字符的具体行
        for ln, l in enumerate(tx.split('\n')):
            if chr(0) in l:
                # 检查同一位置是否有emoji字体渲染
                print(f"第{i+1}页行{ln}: null在: '{l[:80]}'")

doc.close()
print("\n图片已保存: page1_check.png")
