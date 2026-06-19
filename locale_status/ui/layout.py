from __future__ import annotations

import streamlit as st


# 이 파일은 데이터 처리 없이 화면의 공통 스타일과 상단 헤더만 담당합니다.
def apply_naver_style() -> None:
    """밝은 배경과 파란색 포인트를 사용한 대시보드 스타일을 적용합니다."""
    # Streamlit 기본 UI 일부를 숨기고, metric 카드/버튼/탭의 CSS를 덮어씁니다.
    st.markdown(
        """
        <style>
        header[data-testid="stHeader"] {
            background: transparent;
        }

        div[data-testid="stDecoration"] {
            display: none;
        }

        button[data-testid="stSidebarCollapseButton"] {
            display: none !important;
            pointer-events: none !important;
        }

        :root {
            --primary: #2563eb;
            --primary-dark: #1d4ed8;
            --primary-soft: #dbeafe;
            --accent: #16a34a;
            --ink: #111827;
            --muted: #4b5563;
            --line: #d1d5db;
            --soft: #f8fafc;
            --panel: #ffffff;
            --panel-2: #f3f4f6;
        }

        .stApp {
            background: #ffffff;
            color: var(--ink);
        }

        .block-container {
            max-width: 1280px;
            padding-top: 1.4rem;
            padding-bottom: 3rem;
        }

        h1, h2, h3, h4 {
            color: var(--ink);
            letter-spacing: 0;
        }

        h3 {
            padding: 0.15rem 0 0.25rem;
            border-bottom: 2px solid var(--primary);
        }

        p, span, label, div[data-testid="stMarkdownContainer"] {
            color: var(--ink);
        }

        div[data-testid="stMetric"] {
            background: var(--panel);
            border: 1px solid var(--line);
            border-radius: 12px;
            padding: 1rem 1.05rem;
            box-shadow: 0 4px 18px rgba(15, 23, 42, 0.08);
        }

        div[data-testid="stMetricLabel"] {
            color: var(--muted);
            font-size: 0.88rem;
        }

        div[data-testid="stMetricValue"] {
            color: var(--ink);
            font-weight: 800;
        }

        div[data-testid="stTabs"] button {
            border-radius: 10px 10px 0 0;
            color: var(--muted);
            font-weight: 700;
        }

        div[data-testid="stTabs"] button[aria-selected="true"] {
            color: var(--primary-dark);
            border-bottom-color: var(--primary);
        }

        .stButton > button {
            border-radius: 10px;
            border: 1px solid var(--primary);
            font-weight: 800;
            color: var(--primary-dark);
            background: #ffffff;
        }

        .stButton > button[kind="primary"] {
            background: linear-gradient(135deg, var(--primary), var(--accent));
            border-color: var(--primary);
            color: #ffffff;
        }

        .stButton > button[kind="primary"]:hover {
            background: linear-gradient(135deg, var(--primary-dark), var(--accent));
            border-color: var(--primary-dark);
            color: #ffffff;
        }

        div[data-testid="stDataFrame"] {
            border: 1px solid var(--line);
            border-radius: 12px;
            overflow: hidden;
            background: var(--panel);
            box-shadow: 0 4px 18px rgba(15, 23, 42, 0.08);
        }

        div[data-baseweb="select"] > div,
        div[data-baseweb="input"] > div,
        div[data-baseweb="textarea"] > div {
            background-color: var(--panel) !important;
            border-color: var(--line) !important;
            color: var(--ink) !important;
        }

        input, textarea {
            color: var(--ink) !important;
        }

        div[data-testid="stAlert"] {
            color: var(--ink);
        }

        .sky-hero {
            background: linear-gradient(135deg, #eff6ff 0%, #ffffff 55%, #ecfdf5 100%);
            border: 1px solid var(--line);
            border-left: 6px solid var(--primary);
            border-radius: 14px;
            padding: 1.25rem 1.35rem;
            margin-bottom: 1.1rem;
            box-shadow: 0 8px 28px rgba(15, 23, 42, 0.1);
        }

        .sky-hero-title {
            display: flex;
            align-items: center;
            gap: 0.7rem;
            margin: 0 0 0.35rem;
            color: var(--ink);
            font-size: 1.75rem;
            font-weight: 900;
        }

        .sky-logo {
            display: inline-flex;
            align-items: center;
            justify-content: center;
            width: 2.2rem;
            height: 2.2rem;
            border-radius: 10px;
            background: linear-gradient(135deg, var(--primary), var(--accent));
            color: #ffffff;
            font-weight: 900;
            font-size: 1rem;
        }

        .sky-hero-copy {
            margin: 0;
            color: var(--muted);
            line-height: 1.6;
        }

        .info-strip {
            display: grid;
            grid-template-columns: repeat(3, minmax(0, 1fr));
            gap: 0.65rem;
            margin: 0.2rem 0 1.2rem;
        }

        .info-chip {
            background: var(--panel);
            border: 1px solid var(--line);
            border-radius: 12px;
            padding: 0.8rem 0.95rem;
            color: var(--ink);
            font-weight: 700;
            box-shadow: 0 3px 16px rgba(15, 23, 42, 0.08);
        }

        .info-chip strong {
            color: var(--primary-dark);
        }

        @media (max-width: 760px) {
            .info-strip {
                grid-template-columns: 1fr;
            }
            .sky-hero-title {
                font-size: 1.35rem;
            }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_app_header() -> None:
    """앱의 목적을 한눈에 알 수 있는 상단 헤더를 표시합니다."""
    # 모든 탭 위에 공통으로 보이는 앱 제목 영역입니다.
    st.markdown(
        """
        <section class="sky-hero">
            <h1 class="sky-hero-title">
                <span class="sky-logo">EV</span>
                전기차 충전소 실시간 플랫폼
            </h1>
            <p class="sky-hero-copy">실시간 전기차 충전소 현황을 확인할 수 있습니다.</p>
        </section>
        <div class="info-strip">
            <div class="info-chip"><strong>DB</strong> 지역별 사용량 분석</div>
            <div class="info-chip"><strong>LIVE</strong> 충전기 상태</div>
            <div class="info-chip"><strong>NEAR</strong> 내 위치 반경 조회</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
