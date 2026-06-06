"""Theme tokens and CSS for the travel translator demo UI."""

THEME_COLORS = {
    "red": "#FF2938",
    "yellow": "#FDB812",
    "green": "#0DB14B",
    "purple": "#B01E8D",
    "blue": "#00A9DC",
    "gray": "#585856",
    "light_gray": "#F5F5F5",
    "border": "#E5E5E5",
    "text": "#333333",
    "text_muted": "#6B6B6B",
    "white": "#FFFFFF",
}

THEME_CSS = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Nunito:wght@400;600;700;800&display=swap');

    html, body, [class*="css"] {
        font-family: 'Nunito', -apple-system, BlinkMacSystemFont, sans-serif;
    }

    .stApp {
        background: linear-gradient(180deg, #fafafa 0%, #f0f4f8 100%);
    }

    header[data-testid="stHeader"] {
        background: transparent;
    }

    footer[data-testid="stFooter"] {
        display: none;
    }

    /* ── Top bar ── */
    .tt-topbar {
        background: #FFFFFF;
        border-bottom: 1px solid #E5E5E5;
        padding: 0.6rem 0 0.6rem 0;
        margin: -1rem -1rem 1.5rem -1rem;
        padding-left: 1rem;
        padding-right: 1rem;
        display: flex;
        align-items: center;
        justify-content: space-between;
        box-shadow: 0 1px 4px rgba(0,0,0,0.06);
    }
    .tt-logo-wrap {
        display: flex;
        align-items: center;
        gap: 0.55rem;
    }
    .tt-dots {
        display: flex;
        gap: 3px;
        align-items: center;
    }
    .tt-dot {
        width: 11px;
        height: 11px;
        border-radius: 50%;
        display: inline-block;
    }
    .tt-wordmark {
        font-size: 1.65rem;
        font-weight: 800;
        color: #333;
        letter-spacing: -0.5px;
        line-height: 1;
    }
    .tt-badge {
        background: #FF2938;
        color: white;
        font-size: 0.7rem;
        font-weight: 700;
        padding: 0.2rem 0.6rem;
        border-radius: 4px;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    .tt-nav-links {
        display: flex;
        gap: 1.5rem;
        font-size: 0.85rem;
        color: #585856;
        font-weight: 600;
    }
    .tt-nav-links span { cursor: default; }
    .tt-nav-links .active { color: #00A9DC; border-bottom: 2px solid #00A9DC; padding-bottom: 2px; }

    /* ── Hero banner ── */
    .tt-hero {
        background: linear-gradient(135deg, #FF2938 0%, #B01E8D 50%, #00A9DC 100%);
        border-radius: 12px;
        padding: 1.75rem 2rem;
        color: white;
        margin-bottom: 1.5rem;
        position: relative;
        overflow: hidden;
    }
    .tt-hero::after {
        content: '';
        position: absolute;
        right: -30px;
        top: -30px;
        width: 180px;
        height: 180px;
        border-radius: 50%;
        background: rgba(255,255,255,0.08);
    }
    .tt-hero h1 {
        font-size: 1.6rem;
        font-weight: 800;
        margin: 0 0 0.4rem 0;
        color: white;
    }
    .tt-hero p {
        font-size: 0.95rem;
        margin: 0;
        opacity: 0.92;
        font-weight: 600;
    }
    .tt-tagline {
        font-size: 0.8rem;
        opacity: 0.8;
        margin-top: 0.5rem;
        font-style: italic;
    }

    /* ── Stat cards ── */
    .tt-stats {
        display: flex;
        gap: 1rem;
        margin-bottom: 1.25rem;
        flex-wrap: wrap;
    }
    .tt-stat-card {
        flex: 1;
        min-width: 140px;
        background: white;
        border: 1px solid #E5E5E5;
        border-radius: 10px;
        padding: 0.9rem 1.1rem;
        box-shadow: 0 2px 6px rgba(0,0,0,0.04);
    }
    .tt-stat-card .num {
        font-size: 1.5rem;
        font-weight: 800;
        color: #FF2938;
    }
    .tt-stat-card .lbl {
        font-size: 0.78rem;
        color: #585856;
        font-weight: 600;
        margin-top: 0.1rem;
    }

    /* ── Pipeline pills ── */
    .agent-pill {
        display: inline-block;
        background: white;
        color: #585856;
        border: 1px solid #E5E5E5;
        padding: 0.2rem 0.7rem;
        border-radius: 20px;
        font-size: 0.75rem;
        font-weight: 600;
        margin: 0.12rem;
    }
    .agent-pill:nth-child(1) { border-color: #FF2938; color: #FF2938; }
    .agent-pill:nth-child(2) { border-color: #FDB812; color: #C88A00; }
    .agent-pill:nth-child(3) { border-color: #0DB14B; color: #0DB14B; }
    .agent-pill:nth-child(4) { border-color: #00A9DC; color: #00A9DC; }
    .agent-pill:nth-child(5) { border-color: #B01E8D; color: #B01E8D; }

    .pipeline-label {
        font-size: 0.82rem;
        color: #585856;
        font-weight: 700;
        margin-bottom: 0.4rem;
    }

    /* ── QA badges ── */
    .qa-pass {
        color: #0DB14B;
        font-weight: 700;
        background: #E8F8EE;
        padding: 0.2rem 0.6rem;
        border-radius: 6px;
        font-size: 0.82rem;
    }
    .qa-fail {
        color: #FF2938;
        font-weight: 700;
        background: #FFF0F1;
        padding: 0.2rem 0.6rem;
        border-radius: 6px;
        font-size: 0.82rem;
    }

    /* ── Content cards ── */
    .tt-card {
        background: white;
        border: 1px solid #E5E5E5;
        border-radius: 10px;
        padding: 1.25rem;
        margin-bottom: 1rem;
        box-shadow: 0 2px 8px rgba(0,0,0,0.04);
    }
    .tt-card-title {
        font-size: 1rem;
        font-weight: 700;
        color: #333;
        margin-bottom: 0.5rem;
        display: flex;
        align-items: center;
        gap: 0.4rem;
    }

    /* ── Footer ── */
    .tt-footer {
        margin-top: 2.5rem;
        padding: 1.25rem 0;
        border-top: 1px solid #E5E5E5;
        text-align: center;
        color: #585856;
        font-size: 0.78rem;
    }
    .tt-footer strong { color: #FF2938; }

    /* ── Sidebar ── */
    div[data-testid="stSidebar"] {
        background: #FFFFFF;
        border-right: 1px solid #E5E5E5;
    }
    div[data-testid="stSidebar"] .stMarkdown h1,
    div[data-testid="stSidebar"] h2 {
        color: #FF2938 !important;
        font-weight: 800 !important;
        font-size: 1.1rem !important;
    }

    /* ── Primary buttons ── */
    .stButton > button[kind="primary"] {
        background-color: #FF2938 !important;
        border-color: #FF2938 !important;
        color: white !important;
        font-weight: 700 !important;
        border-radius: 8px !important;
        transition: background 0.2s;
    }
    .stButton > button[kind="primary"]:hover {
        background-color: #E0202E !important;
        border-color: #E0202E !important;
    }
    .stButton > button[kind="secondary"] {
        border-color: #00A9DC !important;
        color: #00A9DC !important;
        font-weight: 600 !important;
        border-radius: 8px !important;
    }

    /* ── Tabs ── */
    .stTabs [data-baseweb="tab-list"] {
        gap: 0.5rem;
        background: white;
        border-radius: 10px;
        padding: 0.35rem;
        border: 1px solid #E5E5E5;
    }
    .stTabs [data-baseweb="tab"] {
        font-weight: 700;
        color: #585856;
        border-radius: 8px;
    }
    .stTabs [aria-selected="true"] {
        background: #FFF0F1 !important;
        color: #FF2938 !important;
    }

    /* ── Locale result cards in UI strings tab ── */
    .locale-result {
        background: #F5F5F5;
        border-left: 3px solid #00A9DC;
        padding: 0.6rem 0.8rem;
        border-radius: 0 6px 6px 0;
        font-size: 0.88rem;
        margin-top: 0.3rem;
    }

    /* ── Side-by-side comparison ── */
    .compare-panel {
        background: #FAFAFA;
        border: 1px solid #E5E5E5;
        border-radius: 8px;
        padding: 1rem;
        min-height: 200px;
        font-size: 0.9rem;
        line-height: 1.6;
        white-space: pre-wrap;
    }
    .compare-panel.target {
        border-left: 4px solid #FF2938;
        background: #FFFBFB;
    }
    .compare-panel.source {
        border-left: 4px solid #00A9DC;
    }
    .compare-label {
        font-size: 0.75rem;
        font-weight: 700;
        color: #585856;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        margin-bottom: 0.5rem;
    }
    .glossary-highlight {
        background: #FFF8E1;
        border-bottom: 2px solid #FDB812;
        padding: 0 2px;
    }
    .token-highlight {
        background: #E3F8FD;
        color: #007A9E;
        padding: 0 3px;
        border-radius: 3px;
        font-family: monospace;
        font-size: 0.85em;
    }

    /* ── Mock booking page ── */
    .booking-preview {
        background: white;
        border: 1px solid #E5E5E5;
        border-radius: 12px;
        overflow: hidden;
        box-shadow: 0 4px 16px rgba(0,0,0,0.08);
        max-width: 720px;
        margin: 0 auto;
    }
    .booking-search-bar {
        background: #FF2938;
        padding: 1.25rem 1.5rem;
    }
    .booking-search-input {
        background: white;
        border-radius: 8px;
        padding: 0.75rem 1rem;
        color: #999;
        font-size: 0.95rem;
    }
    .booking-hotel-card {
        padding: 1.25rem 1.5rem;
        border-bottom: 1px solid #F0F0F0;
    }
    .booking-hotel-name {
        font-size: 1.15rem;
        font-weight: 800;
        color: #333;
        margin-bottom: 0.3rem;
    }
    .booking-hotel-desc {
        font-size: 0.85rem;
        color: #585856;
        line-height: 1.5;
        margin-bottom: 0.75rem;
    }
    .booking-badges {
        display: flex;
        gap: 0.5rem;
        flex-wrap: wrap;
        margin-bottom: 0.75rem;
    }
    .booking-badge {
        font-size: 0.72rem;
        font-weight: 700;
        padding: 0.2rem 0.55rem;
        border-radius: 4px;
    }
    .badge-green { background: #E8F8EE; color: #0DB14B; }
    .badge-blue { background: #E3F8FD; color: #007A9E; }
    .booking-price-row {
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    .booking-price {
        font-size: 1.3rem;
        font-weight: 800;
        color: #FF2938;
    }
    .booking-cta {
        background: #FF2938;
        color: white;
        font-weight: 700;
        padding: 0.55rem 1.4rem;
        border-radius: 8px;
        font-size: 0.9rem;
        border: none;
    }
    .booking-urgency {
        font-size: 0.78rem;
        color: #FF2938;
        font-weight: 600;
        margin-top: 0.4rem;
    }
</style>
"""


def render_topbar() -> str:
    return """
    <div class="tt-topbar">
        <div class="tt-logo-wrap">
            <span class="tt-wordmark">🌐 Travel Translator</span>
            <span class="tt-badge">Demo</span>
        </div>
        <div class="tt-nav-links">
            <span>Hotels</span>
            <span>Flights</span>
            <span class="active">Content CMS</span>
            <span>Partners</span>
        </div>
    </div>
    """


def render_hero() -> str:
    return """
    <div class="tt-hero">
        <h1>🌐 Multilingual Content Translator</h1>
        <p>Localize your travel booking site for guests across Asia-Pacific and beyond.</p>
        <div class="tt-tagline">Localize travel content — in every language.</div>
    </div>
    """


def highlight_terms(text: str, glossary_terms: list[str], tokens: list[str]) -> str:
    import html
    import re

    safe = html.escape(text)
    for term in sorted(glossary_terms, key=len, reverse=True):
        pattern = re.compile(re.escape(term), re.IGNORECASE)
        safe = pattern.sub(
            lambda m: f'<span class="glossary-highlight">{m.group()}</span>',
            safe,
        )
    for token in tokens:
        safe = safe.replace(html.escape(token), f'<span class="token-highlight">{html.escape(token)}</span>')
    return safe


def render_booking_preview(
    locale: str,
    strings: dict[str, str],
    hotel_name: str,
    hotel_desc: str,
    price: str = "2,450",
) -> str:
    search = strings.get("search_placeholder", "Where are you going?")
    book_now = strings.get("book_now", "Book Now")
    free_cancel = strings.get("free_cancellation", "Free Cancellation")
    pay_hotel = strings.get("pay_at_hotel", "Pay at Hotel")
    price_label = strings.get("price_per_night", "From {price} per night").replace("{price}", price)
    rooms_left = strings.get("rooms_left", "Only {count} rooms left!").replace("{count}", "3")

    return f"""
    <div class="booking-preview">
        <div class="booking-search-bar">
            <div class="booking-search-input">🔍 {search}</div>
        </div>
        <div class="booking-hotel-card">
            <div class="booking-hotel-name">{hotel_name}</div>
            <div class="booking-hotel-desc">{hotel_desc[:180]}…</div>
            <div class="booking-badges">
                <span class="booking-badge badge-green">✓ {free_cancel}</span>
                <span class="booking-badge badge-blue">🏨 {pay_hotel}</span>
            </div>
            <div class="booking-price-row">
                <div>
                    <div class="booking-price">{price_label}</div>
                    <div class="booking-urgency">⚡ {rooms_left}</div>
                </div>
                <span class="booking-cta">{book_now}</span>
            </div>
        </div>
    </div>
    <p style="text-align:center;color:#585856;font-size:0.8rem;margin-top:0.5rem;">
        Live preview · Locale: <strong>{locale}</strong>
    </p>
    """


def render_stats(locale_count: int, agent_count: int = 6) -> str:
    return f"""
    <div class="tt-stats">
        <div class="tt-stat-card">
            <div class="num">{locale_count}</div>
            <div class="lbl">Supported locales</div>
        </div>
        <div class="tt-stat-card">
            <div class="num">{agent_count}</div>
            <div class="lbl">AI agents in pipeline</div>
        </div>
        <div class="tt-stat-card">
            <div class="num">13+</div>
            <div class="lbl">Content types</div>
        </div>
        <div class="tt-stat-card">
            <div class="num">APAC</div>
            <div class="lbl">Primary market focus</div>
        </div>
    </div>
    """


def render_footer() -> str:
    return """
    <div class="tt-footer">
        Travel Translator Demo &nbsp;·&nbsp;
        Multi-agent content localization platform &nbsp;·&nbsp;
        For internal demonstration purposes only
    </div>
    """
