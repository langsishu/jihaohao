#!/usr/bin/env python
"""最终验证：检查emoji渲染位置"""
import fitz
doc = fitz.open(r'D:\AI project\app\账号密码记录\记号号工具软件V1.0_源程序鉴别材料.pdf')
page = doc[0]
blocks = page.get_text('dict')['blocks']

print("=== Emoji渲染检查 ===")
emoji_count = 0
for b in blocks:
    if 'lines' not in b: continue
    for l in b['lines']:
        for s in l['spans']:
            if 'Emoji' in s['font'] or 'E0' in s['font']:
                emoji_count += 1
                if emoji_count <= 3:
                    print(f"  Emoji[{emoji_count}]: text={repr(s['text'])}")
                    print(f"    bbox={s['bbox']}")
                    # 找同一y位置附近的MSYH span
                    for b2 in blocks:
                        if 'lines' not in b2: continue
                        for l2 in b2['lines']:
                            for s2 in l2['spans']:
                                if 'YaHei' in s2['font'] and abs(s2['bbox'][1]-s['bbox'][1]) < 5:
                                    if '\x00' in s2['text']:
                                        print(f"    对应MSYH: bbox={s2['bbox']}")
                                        print(f"      text={repr(s2['text'][:40])}")
                                        break
                    print()

print(f"总emoji span数: {emoji_count}")

# 统计所有页的null字符
null_total = 0
for i in range(len(doc)):
    tx = doc[i].get_text()
    null_total += tx.count('\x00')
print(f"所有页空字符总计: {null_total}")

doc.close()
