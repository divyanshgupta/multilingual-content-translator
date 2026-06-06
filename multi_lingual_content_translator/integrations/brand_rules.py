"""Travel site brand and locale rules for translation agents."""

TRAVEL_GLOSSARY: dict[str, dict[str, str]] = {
    "free cancellation": {
        "th": "ยกเลิกฟรี",
        "ja": "無料キャンセル",
        "ko": "무료 취소",
        "zh-CN": "免费取消",
        "vi": "Hủy miễn phí",
        "id": "Pembatalan gratis",
        "ms": "Pembatalan percuma",
    },
    "breakfast included": {
        "th": "รวมอาหารเช้า",
        "ja": "朝食付き",
        "ko": "조식 포함",
        "zh-CN": "含早餐",
        "vi": "Bao gồm bữa sáng",
        "id": "Termasuk sarapan",
        "ms": "Termasuk sarapan",
    },
    "non-refundable": {
        "th": "ไม่สามารถคืนเงินได้",
        "ja": "返金不可",
        "ko": "환불 불가",
        "zh-CN": "不可退款",
        "vi": "Không hoàn tiền",
        "id": "Tidak dapat dikembalikan",
        "ms": "Tidak boleh dikembalikan",
    },
    "pay at hotel": {
        "th": "ชำระที่โรงแรม",
        "ja": "現地払い",
        "ko": "호텔에서 결제",
        "zh-CN": "到店付款",
        "vi": "Thanh toán tại khách sạn",
        "id": "Bayar di hotel",
        "ms": "Bayar di hotel",
    },
    "instant confirmation": {
        "th": "ยืนยันทันที",
        "ja": "即時確認",
        "ko": "즉시 확정",
        "zh-CN": "即时确认",
        "vi": "Xác nhận ngay",
        "id": "Konfirmasi instan",
        "ms": "Pengesahan segera",
    },
    "per night": {
        "th": "ต่อคืน",
        "ja": "1泊あたり",
        "ko": "1박당",
        "zh-CN": "每晚",
        "vi": "Mỗi đêm",
        "id": "Per malam",
        "ms": "Setiap malam",
    },
}

# Backward-compatible alias
TRAVEL_GLOSSARY = TRAVEL_GLOSSARY

LOCALE_GUIDELINES: dict[str, str] = {
    "th": "Use polite formal Thai suitable for hospitality. Preserve hotel names in Latin script.",
    "ja": "Use polite desu/masu form. Keep foreign hotel brand names in katakana or original script.",
    "ko": "Use polite 합니다 form. Preserve proper nouns and brand names.",
    "zh-CN": "Use Simplified Chinese. Keep international brand names recognizable.",
    "zh-TW": "Use Traditional Chinese (Taiwan). Keep international brand names recognizable.",
    "vi": "Use formal Vietnamese suitable for travel booking. Preserve hotel names.",
    "id": "Use formal Bahasa Indonesia. Keep brand names in original form.",
    "ms": "Use formal Bahasa Melayu. Keep brand names in original form.",
    "ar": "Use Modern Standard Arabic, RTL-aware. Keep Latin brand names as-is.",
    "hi": "Use formal Hindi. Preserve international brand names.",
}

BRAND_RULES = {
    "tone": "Professional, trustworthy, and welcoming — suitable for a global travel booking platform.",
    "preserve": [
        "Hotel brand names",
        "Room type codes (e.g., DLX, STD)",
        "Currency codes (USD, THB, JPY)",
        "HTML tags and placeholders ({price}, {date}, %s)",
        "URLs and email addresses",
    ],
    "prohibited": [
        "Overly casual slang",
        "Machine-translated literal idioms",
        "Altering legal/policy meaning",
        "Translating protected brand names",
    ],
    "travel_context": (
        "Content is for a travel site. "
        "Users search, compare, and book hotels across Asia-Pacific and worldwide."
    ),
}


def get_brand_rules() -> dict:
    return BRAND_RULES


def get_locale_guidelines(locale: str) -> str:
    return LOCALE_GUIDELINES.get(
        locale,
        "Use natural, formal language appropriate for a travel booking website.",
    )


def get_glossary_for_locale(locale: str) -> dict[str, str]:
    return {
        term: translations[locale]
        for term, translations in TRAVEL_GLOSSARY.items()
        if locale in translations
    }
