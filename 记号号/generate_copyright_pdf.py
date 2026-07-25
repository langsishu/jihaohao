#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
软著登记源程序鉴别材料PDF生成脚本（v5 - 保留完整代码结构）
- 保留所有源码行（含注释、空行），仅折叠连续空行
- 仅统计有效行数用于3000行限制判断
- ASCII代码：Consolas等宽字体（保证缩进对齐）
- 中文字符：NotoSansSC（CJK字体，保证可读）
- emoji：移除（字体不支持）
- 缩进：tab展开4空格，Consolas等宽保证对齐
- 页眉：每页左上角「记号号工具软件 V1.0 程序鉴别材料」
- 长代码：自动折行展示
"""
import os
import re

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

# ========== 配置 ==========
PROJECT_DIR = r"D:\AI project\app\账号密码记录"
HEADER_TEXT = "记号号工具软件 V1.0 程序鉴别材料"
OUTPUT_FILENAME = "记号号工具软件 V1.0_源程序鉴别材料.pdf"
OUTPUT_TEMP = "记号号工具软件 V1.0_源程序鉴别材料_tmp.pdf"

FILE_PRIORITY = [
    "pages/index/index.uvue",
    "pages/detail/detail.uvue",
    "App.uvue",
    "main.uts",
    "pages.json",
    "uni.scss",
]

# ========== Emoji移除 ==========
EMOJI_MAP = {
    '\U0001F50D': '', '\U0001F4CB': '', '\u2699': '',
    '\U0001F4F1': '', '\U0001F310': '', '\U0001F4C4': '',
    '\u270F': '', '\U0001F5D1': '', '\U0001F5BC': '',
    '\u2B06': '', '\u2B07': '', '\U0001F4CC': '',
    '\U0001F680': '', '\u2605': '', '\u2715': '',
    '\u2705': '', '\U0001F4E4': '', '\U0001F4E5': '',
    '\u27A1': '', '\u25B6': '', '\u25BC': '',
    '\u25B8': '', '\uFE0F': '', '\u00D7': '',
    '\u25CF': '', '\U0001F44D': '', '\U0001F4DD': '',
    '\u270F\uFE0F': '', '\u2728': '', '\U0001F441': '',
}

def remove_emoji(text):
    """移除所有不可渲染的高码位emoji字符"""
    out = []
    for ch in text:
        out.append(EMOJI_MAP.get(ch, ch))
    # 再用正则清除残留的高码位字符
    return re.sub(r'[\U00010000-\U0010FFFF]', '', ''.join(out))


# ========== 字体注册 ==========
def register_fonts():
    """注册Consolas（ASCII等宽）+ NotoSansSC（CJK回退）"""
    consola_path = None
    for p in [r"C:\Windows\Fonts\consola.ttf", r"C:\Windows\Fonts\CONSOLA.TTF"]:
        if os.path.exists(p):
            consola_path = p
            break
    if consola_path:
        pdfmetrics.registerFont(TTFont('Consolas', consola_path))
        print(f"  [OK] Consolas: {consola_path}")
    else:
        print("  [WARN] Consolas not found, using Courier")
        pdfmetrics.registerFont(TTFont('Consolas', r"C:\Windows\Fonts\cour.ttf"))

    cjk_path = None
    for p in [r"C:\Windows\Fonts\NotoSansSC-VF.ttf",
              r"C:\Windows\Fonts\simsun.ttc",
              r"C:\Windows\Fonts\msyh.ttc"]:
        if os.path.exists(p):
            cjk_path = p
            break
    if cjk_path:
        pdfmetrics.registerFont(TTFont('CJKFont', cjk_path))
        print(f"  [OK] CJK font: {os.path.basename(cjk_path)}")
    else:
        print("  [WARN] No CJK font found")


# ========== 混合字体绘制 ==========
def is_ascii(ch):
    code = ord(ch)
    return code < 0x200 or (0x200 <= code < 0x300) or ch in '→►'

def is_cjk(ch):
    code = ord(ch)
    return (0x4E00 <= code <= 0x9FFF) or (0x3400 <= code <= 0x4DBF) or \
           (0xF900 <= code <= 0xFAFF) or (0x2000 <= code <= 0x206F) or \
           (0x3000 <= code <= 0x303F) or (0xFF00 <= code <= 0xFFEF)

def draw_mixed_line(c, x, y, text, font_size):
    """用混合字体绘制一行代码：ASCII用Consolas，CJK用CJKFont"""
    FS = font_size
    segments = []
    current = ''
    current_type = None

    for ch in text:
        if is_ascii(ch):
            t = 'ascii'
        elif is_cjk(ch):
            t = 'cjk'
        else:
            continue

        if t != current_type and current:
            segments.append((current, current_type))
            current = ''
        current += ch
        current_type = t

    if current:
        segments.append((current, current_type))

    cx = x
    for seg_text, seg_type in segments:
        fn = 'CJKFont' if seg_type == 'cjk' else 'Consolas'
        c.setFont(fn, FS)
        c.drawString(cx, y, seg_text)
        cx += c.stringWidth(seg_text, fn, FS)

    return cx - x

def string_width_mixed(text, font_size):
    """计算混合字体的字符串总宽度"""
    FS = font_size
    total = 0
    current = ''
    current_type = None

    for ch in text:
        if is_ascii(ch):
            t = 'ascii'
        elif is_cjk(ch):
            t = 'cjk'
        else:
            continue
        if t != current_type and current:
            fn = 'CJKFont' if current_type == 'cjk' else 'Consolas'
            total += pdfmetrics.stringWidth(current, fn, FS)
            current = ''
        current += ch
        current_type = t

    if current:
        fn = 'CJKFont' if current_type == 'cjk' else 'Consolas'
        total += pdfmetrics.stringWidth(current, fn, FS)

    return total


# ========== 文件读取 ==========
def read_source_file(rel_path):
    abs_path = os.path.join(PROJECT_DIR, rel_path)
    if not os.path.exists(abs_path):
        return []
    with open(abs_path, "r", encoding="utf-8") as f:
        content = f.read()
    content = content.replace("\r\n", "\n").replace("\r", "\n")
    return content.split("\n")


def count_effective_lines(lines):
    """统计有效代码行数（空行、纯注释不计入）"""
    count = 0
    in_block = False
    for line in lines:
        s = line.strip()
        if in_block:
            if "*/" in s:
                in_block = False
                after = s.split("*/", 1)[1].strip()
                if after:
                    count += 1
            continue
        if "/*" in s:
            if "*/" in s:
                cleaned = re.sub(r'/\*.*?\*/', '', s, count=1).strip()
                if cleaned:
                    count += 1
                continue
            else:
                before = s.split("/*")[0].strip()
                if before:
                    count += 1
                in_block = True
                continue
        if s.startswith("//") or s.startswith("#") or not s:
            continue
        if (s.startswith("<!--") and s.endswith("-->")) or \
           s.startswith("<!--") or s.endswith("-->"):
            continue
        count += 1
    return count


def collapse_blank_lines(lines):
    """折叠连续空行为最多1行，保留所有代码和注释行"""
    result = []
    prev_blank = False
    for line in lines:
        if line.strip() == '':
            if not prev_blank:
                result.append(line)
            prev_blank = True
        else:
            result.append(line)
            prev_blank = False
    # 去除文件开头和结尾的空行
    while result and result[0].strip() == '':
        result.pop(0)
    while result and result[-1].strip() == '':
        result.pop()
    return result


# ========== 主流程 ==========
def build_pdf():
    register_fonts()
    print()

    # === Step 1: 读取文件并统计 ===
    file_info = []
    total_eff = 0
    print("=" * 60)
    print("Step 1: File statistics")
    print("=" * 60)
    for rp in FILE_PRIORITY:
        lines = read_source_file(rp)
        if not lines:
            file_info.append((rp, [], 0))
            continue
        eff = count_effective_lines(lines)
        file_info.append((rp, lines, eff))
        total_eff += eff
        print(f"  {rp}: {len(lines)} lines, {eff} effective")
    print(f"\n  Total effective lines: {total_eff}")

    # === Step 2: 3000行控制 ===
    print("\n" + "=" * 60)
    print("Step 2: Line count control")
    print("=" * 60)
    if total_eff <= 3000:
        print(f"  {total_eff} <= 3000, keep all files")
        sel = file_info
    else:
        sel = [list(fi) for fi in file_info]
        while total_eff > 3000 and len(sel) > 1:
            removed = sel.pop()
            total_eff -= removed[2]
            print(f"  Removed: {removed[0]} ({removed[2]} lines), remaining {total_eff}")

    # === Step 3: 拼接代码（保留所有行，仅移除emoji和折叠空行） ===
    print("\n" + "=" * 60)
    print("Step 3: Code assembly (preserve all lines)")
    print("=" * 60)
    code_lines = []
    for rp, raw_lines, cnt in sel:
        if not raw_lines:
            continue
        code_lines.append(f"// ====== {rp} ======")
        collapsed = collapse_blank_lines(raw_lines)
        for line in collapsed:
            code_lines.append(remove_emoji(line))
    total = len(code_lines)
    print(f"  Total display lines: {total}")
    print(f"  Effective lines: {total_eff}")

    # === Step 4: 生成PDF ===
    print("\n" + "=" * 60)
    print("Step 4: Generate PDF")
    print("=" * 60)
    out_path = os.path.join(PROJECT_DIR, OUTPUT_TEMP)

    PW, PH = A4
    LM = 22 * mm
    RM = 18 * mm
    TM = 22 * mm
    BM = 20 * mm
    CW = PW - LM - RM
    CH = PH - TM - BM

    FS = 10
    LEAD = FS * 1.2
    LPP = int(CH / LEAD)

    print(f"  Consolas(ASCII) + CJKFont(CJK), {FS}pt, lead={LEAD}pt, {LPP} lines/page")

    c = canvas.Canvas(out_path, pagesize=A4)
    c.setTitle(HEADER_TEXT)

    li = 0
    pn = 1

    while li < total:
        # --- 页眉 ---
        c.saveState()
        c.setFont('Consolas', 9)
        c.setFillColorRGB(0, 0, 0)
        c.drawString(LM, PH - 13 * mm, HEADER_TEXT)
        c.drawRightString(PW - RM, PH - 13 * mm, str(pn))
        c.setStrokeColorRGB(0.55, 0.55, 0.55)
        c.line(LM, PH - 15.5 * mm, PW - RM, PH - 15.5 * mm)
        c.restoreState()

        # --- 代码 ---
        y = PH - TM - 2 * mm
        drawn = 0

        while li < total and drawn < LPP:
            raw = code_lines[li]
            display = raw.expandtabs(4).rstrip('\n').rstrip('\r')

            if not display:
                li += 1
                y -= LEAD
                drawn += 1
                continue

            w = string_width_mixed(display, FS)

            if w <= CW:
                draw_mixed_line(c, LM, y, display, FS)
                drawn += 1
                y -= LEAD
                li += 1
            else:
                # 自动折行
                remain = display
                first = True
                while remain and drawn < LPP:
                    lo, hi = 1, len(remain)
                    while lo < hi:
                        mid = (lo + hi + 1) // 2
                        if string_width_mixed(remain[:mid], FS) <= CW - 3:
                            lo = mid
                        else:
                            hi = mid - 1
                    x = LM if first else LM + 8
                    draw_mixed_line(c, x, y, remain[:lo], FS)
                    remain = remain[lo:]
                    drawn += 1
                    y -= LEAD
                    first = False

                if remain:
                    code_lines[li] = remain
                else:
                    li += 1

        pn += 1
        c.showPage()

    c.save()

    # 尝试重命名为最终文件名
    import shutil
    final_path = os.path.join(PROJECT_DIR, OUTPUT_FILENAME)
    renamed = False
    try:
        if os.path.exists(final_path):
            os.remove(final_path)
        shutil.move(out_path, final_path)
        out_path = final_path
        renamed = True
        print(f"  Renamed to final filename")
    except Exception as e:
        print(f"  Warning: could not rename to final name ({e})")
        print(f"  Output kept as: {out_path}")
        # 尝试copy
        try:
            shutil.copy2(out_path, final_path)
            out_path = final_path
            renamed = True
            print(f"  Copied to final filename instead")
        except Exception as e2:
            print(f"  Copy also failed: {e2}")
            print(f"  Using temp file: {out_path}")

    # === 结果 ===
    rp_count = pn - 1
    sz = os.path.getsize(out_path)
    print(f"\n  [DONE] PDF generated")
    print(f"  File: {out_path}")
    print(f"  Pages: {rp_count}")
    print(f"  Size: {sz/1024:.1f} KB")
    print(f"  Font: Consolas(ASCII) + CJKFont(CJK)")
    print(f"  Header: {HEADER_TEXT}")
    print(f"  Page numbers: 1-{rp_count}")
    print(f"  Effective lines: {total_eff}")
    print(f"  Display lines: {total}")
    print(f"  Indentation: tab->4 spaces, Consolas monospace")
    print(f"  Line wrap: auto")
    print(f"  Single file: yes")
    print(f"  Emoji: removed")

    return out_path


if __name__ == "__main__":
    r = build_pdf()
    print(f"\nPath: {r}")
