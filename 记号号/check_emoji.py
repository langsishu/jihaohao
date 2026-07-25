#!/usr/bin/env python
"""检查PDF中emoji渲染情况"""
import fitz
doc = fitz.open(r'D:\AI project\app\账号密码记录\记号号工具软件V1.0_源程序鉴别材料.pdf')
page = doc[0]
blocks = page.get_text('dict')['blocks']

print("包含空字符的spans:")
for b in blocks:
    if 'lines' in b:
        for l in b['lines']:
            for s in l['spans']:
                if '\x00' in s['text']:
                    print(f"  font={s['font']} size={s['size']} bbox={s['bbox']}")
                    print(f"  text={repr(s['text'][:60])}")

print()
print("Segoe UI Emoji渲染的spans:")
for b in blocks:
    if 'lines' in b:
        for l in b['lines']:
            for s in l['spans']:
                if 'Emoji' in s['font']:
                    print(f"  font={s['font']} text={repr(s['text'][:40])} bbox={s['bbox']}")
                elif 'E0' in s['font']:
                    print(f"  font={s['font']} text={repr(s['text'][:40])} bbox={s['bbox']}")

# 检查所有字体引用
print()
fonts_used = set()
for b in blocks:
    if 'lines' in b:
        for l in b['lines']:
            for s in l['spans']:
                fonts_used.add(s['font'])
print("所有使用到的字体:", fonts_used)

# 检查第1页行6（已知包含emoji的行）附近
print()
print("line 6附近文本块:")
for b in blocks:
    if 'lines' in b:
        for l in b['lines']:
            for s in l['spans']:
                if 100 < s['bbox'][1] < 200:  # y范围在行6附近
                    print(f"  y={s['bbox'][1]:.0f} font={s['font']} text={repr(s['text'][:60])}")

doc.close()
