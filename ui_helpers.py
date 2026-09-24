"""工具函数：时间格式化、FDA 警告格式化"""
import re
from datetime import datetime, timezone, timedelta


# ============================================================
# FDA 警告标题翻译表（保留备用，当前不启用）
# ============================================================
WARNING_HEADER_MAP = {
    "zh-Hans": {
        "Warnings": "警告",
        "Warning": "警告",
        "Liver warning": "肝脏警告",
        "Allergy alert": "过敏警告",
        "Stomach bleeding warning": "胃出血警告",
        "Alcohol warning": "酒精警告",
        "Overdose warning": "过量警告",
        "Reye's syndrome": "瑞氏综合征警告",
        "Ask a doctor before use if": "使用前请咨询医生，如果您",
        "Ask a doctor or pharmacist before use if": "使用前请咨询医生或药师，如果您",
        "Do not use": "禁止使用，如果您",
        "Stop use and ask a doctor if": "出现以下情况请停药并就医",
        "When using this product": "使用本品时",
        "If pregnant or breast-feeding": "孕期或哺乳期",
        "Keep out of reach of children": "儿童请勿接触",
        "Purpose": "用途",
    },
    "zh-Hant": {
        "Warnings": "警告",
        "Warning": "警告",
        "Liver warning": "肝臟警告",
        "Allergy alert": "過敏警告",
        "Stomach bleeding warning": "胃出血警告",
        "Alcohol warning": "酒精警告",
        "Overdose warning": "過量警告",
        "Reye's syndrome": "瑞氏症候群警告",
        "Ask a doctor before use if": "使用前請諮詢醫生，如果您",
        "Ask a doctor or pharmacist before use if": "使用前請諮詢醫生或藥師，如果您",
        "Do not use": "禁止使用，如果您",
        "Stop use and ask a doctor if": "出現以下情況請停藥並就醫",
        "When using this product": "使用本品時",
        "If pregnant or breast-feeding": "孕期或哺乳期",
        "Keep out of reach of children": "兒童請勿接觸",
        "Purpose": "用途",
    },
    "en": {},
}


def _translate_headers(text: str, lang: str) -> str:
    """把 FDA 警告里的英文标题替换成本地语言（当前不启用）。"""
    mapping = WARNING_HEADER_MAP.get(lang, {})
    if not mapping:
        return text
    for en in sorted(mapping.keys(), key=len, reverse=True):
        text = text.replace(en, mapping[en])
    return text


# ============================================================
# 时间格式化
# ============================================================
def format_local_time(iso_str: str, lang: str) -> str:
    """把 ISO 时间转成本地化显示（默认 UTC+8）。"""
    if not iso_str:
        return "-"
    try:
        dt = datetime.fromisoformat(iso_str.replace("Z", "+00:00"))
        local = dt.astimezone(timezone(timedelta(hours=8)))

        if lang == "en":
            return local.strftime("%b %d, %Y · %I:%M %p") + " (UTC+8)"
        elif lang == "zh-Hant":
            weekday = ["一", "二", "三", "四", "五", "六", "日"][local.weekday()]
            return local.strftime(f"%Y年%m月%d日 週{weekday} %H:%M（台北時間）")
        else:
            weekday = ["一", "二", "三", "四", "五", "六", "日"][local.weekday()]
            return local.strftime(f"%Y年%m月%d日 星期{weekday} %H:%M（北京时间）")
    except Exception:
        return iso_str


# ============================================================
# FDA 警告格式化（保留英文原文，不翻译，只做结构美化）
# ============================================================
def format_fda_warnings(warnings: str, lang: str) -> str:
    """把 openFDA 的原始 warnings 转成可读 HTML（保留英文，不做翻译）。"""
    if not warnings:
        return ""

    # 清理前缀
    warnings = re.sub(r"^(Warnings|WARNINGS)\s+", "", warnings.strip())

    # 英文标题加粗（第一个标题 margin-top=0，其余 0.6rem）
    _heading_count = {"n": 0}

    def bold_heading(m):
        _heading_count["n"] += 1
        top = "0" if _heading_count["n"] == 1 else "0.6rem"
        return (
            f"<div style='margin-top:{top};margin-bottom:0.3rem;'>"
            f"<strong class='fda-heading' "
            f"style='font-size:0.88rem;font-weight:700;'>"
            f"{m.group(1)}:</strong></div>"
        )

    warnings = re.sub(
        r"(?<!\w)([A-Z][a-zA-Z\s']{2,35}?)\s*(?:warning|alert|Warning|Alert)\s*:",
        bold_heading,
        warnings,
    )

    # bullet 转列表
    if "•" in warnings:
        parts = warnings.split("•")
        warnings = (
            parts[0]
            + "<ul style='margin:0.4rem 0 0.6rem 1.1rem;padding:0;"
              "list-style-type:disc;'>"
            + "".join(
                f"<li style='margin-bottom:0.25rem;color:#57534e;"
                f"line-height:1.55;'>{p.strip()}</li>"
                for p in parts[1:] if p.strip()
            )
            + "</ul>"
        )

    # 段落化
    warnings = re.sub(r"\n{2,}", "<br>", warnings).replace("\n", "<br>")

    # 去掉开头多余的空行 / <br> / 空白
    warnings = re.sub(r"^(<br\s*/?>\s*)+", "", warnings)
    warnings = re.sub(r"^[\s\n]+", "", warnings)
    warnings = warnings.strip()

    return warnings