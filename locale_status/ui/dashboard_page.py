from __future__ import annotations

import pandas as pd
import pydeck as pdk
import streamlit as st

# 이 파일은 Streamlit 화면 전체를 조립하는 중심 파일입니다.
# DB 사용량 분석, 충전기 상태 지도, 추천 충전소, 내 주변 조회를 렌더링합니다.
try:
    # streamlit-geolocation은 브라우저 위치 권한을 받아 현재 위치를 가져오는 선택 기능입니다.
    # 설치되어 있지 않아도 앱 전체가 죽지 않도록 None으로 처리합니다.
    from streamlit_geolocation import streamlit_geolocation
except ModuleNotFoundError:
    streamlit_geolocation = None

from locale_status.api.charger_api import (
    ChargerAPIError,
    get_charger_info,
    get_charger_status,
)
from locale_status.config.settings import (
    AVAILABLE_STATUS,
    ChargerApiSettings,
    COORDS_CSV_PATH,
    DETAIL_COLUMNS,
    DETAIL_COLUMN_LABELS,
    REGION_CODES,
    SettingsError,
    STATUS_LABELS,
    USAGE_CSV_PATH,
    get_settings,
)
from locale_status.db.usage_repository import load_usage_dataset
from locale_status.models.charger import (
    add_distance,
    enrich_realtime_data,
    merge_charger_data,
)
from locale_status.models.dashboard import summarize_chargers
from locale_status.ui.layout import apply_naver_style, render_app_header


@st.cache_data(show_spinner=False)
def load_usage_data() -> pd.DataFrame:
    """DB 사용량 데이터를 읽어 대시보드용 DataFrame으로 만듭니다."""
    # DB 조회 결과는 앱 실행 중 자주 바뀌지 않으므로 Streamlit 캐시에 저장합니다.
    return load_usage_dataset(USAGE_CSV_PATH, COORDS_CSV_PATH)


@st.cache_data(ttl=3600, show_spinner=False)
def load_realtime_info(
    api_settings: ChargerApiSettings,
    zcode: str,
) -> list[dict[str, str]]:
    """충전소 기본정보 API 결과를 1시간 캐시합니다."""
    return get_charger_info(api_settings, zcode)


@st.cache_data(ttl=180, show_spinner=False)
def load_realtime_status(
    api_settings: ChargerApiSettings,
    zcode: str,
    period: int,
) -> list[dict[str, str]]:
    """충전기 실시간 상태 API 결과를 3분 캐시합니다."""
    return get_charger_status(api_settings, zcode, period=period)


def render_metric_row(charger_df: pd.DataFrame) -> None:
    """실시간 조회 결과의 기본 지표 4개를 metric 카드로 표시합니다."""
    # ChargerSummary 객체로 계산한 값을 Streamlit metric 카드에 배치합니다.
    summary = summarize_chargers(charger_df)

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("전체 충전소", f"{summary.total_stations:,}곳")
    col2.metric("전체 충전기", f"{summary.total_chargers:,}대")
    col3.metric("사용 가능", f"{summary.available_chargers:,}대")
    col4.metric("충전 중", f"{summary.charging_chargers:,}대")

def render_dashboard_summary(charger_df: pd.DataFrame) -> None:
    """최종 필터링 결과 기준으로 사용 가능률과 혼잡도를 metric 카드로 표시합니다."""

    if charger_df.empty:
        return

    # 검색/상태/용량 필터가 모두 적용된 데이터 기준의 요약입니다.
    summary = summarize_chargers(charger_df)

    c1, c2, c3, c4 = st.columns(4)

    c1.metric("⚡ 사용 가능", f"{summary.available_chargers:,}대")
    c2.metric("🔋 충전 중", f"{summary.charging_chargers:,}대")
    c3.metric("✅ 충전 가능률", f"{summary.availability_rate:.1f}%")
    c4.metric(
        "🚦 혼잡도",
        f"{summary.congestion_label} ({summary.congestion_rate:.1f}%)"
    )

def render_usage_overview(usage_df: pd.DataFrame) -> None:
    """DB 기반의 지역별 사용량, 설치 분포, 좌표 지도를 표시합니다."""
    st.subheader("DB 기반 지역별 사용량")

    if usage_df.empty:
        st.warning("tbl_region_elec_usage 테이블에 표시할 데이터가 없습니다.")
        return

    usage_column = "사용량(키로와트시)"
    charger_columns = [
        column
        for column in usage_df.columns
        if "키로와트" in column and column != usage_column
    ]

    # 상단 요약 metric에 들어갈 전체 통계입니다.
    total_usage = usage_df[usage_column].sum()
    total_rows = len(usage_df)
    total_sgg = usage_df[["광역지자체", "시군구"]].drop_duplicates().shape[0]
    total_csv_chargers = usage_df[charger_columns].sum().sum()

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("DB 데이터 행", f"{total_rows:,}건")
    col2.metric("지역 수", f"{total_sgg:,}개")
    col3.metric("DB 충전기 합계", f"{total_csv_chargers:,.0f}대")
    col4.metric("총 사용량", f"{total_usage:,.0f} kWh")

    # DB 사용량 탭에서 특정 광역지자체만 골라 볼 수 있는 필터입니다.
    region_options = ["전체", *sorted(usage_df["광역지자체"].dropna().unique())]
    selected_region = st.selectbox(
        "지역 필터",
        options=region_options,
        key="csv_region_filter",
    )

    filtered_usage_df = usage_df.copy()
    if selected_region != "전체":
        filtered_usage_df = filtered_usage_df[
            filtered_usage_df["광역지자체"] == selected_region
        ]

    # 지역별 총 사용량 그래프 데이터입니다.
    region_usage = (
        filtered_usage_df.groupby("광역지자체", as_index=False)[usage_column]
        .sum()
        .sort_values(usage_column, ascending=False)
    )

    left, right = st.columns([1.15, 1])
    with left:
        st.markdown("#### 광역지자체별 사용량")
        st.bar_chart(
            region_usage,
            x="광역지자체",
            y=usage_column,
            color="#2563eb",
            width="stretch",
        )

    with right:
        st.markdown("#### 충전용량별 설치 분포")
        # 50kW, 100kW 등 용량 컬럼들을 합산해 설치 분포를 만듭니다.
        output_distribution = (
            filtered_usage_df[charger_columns]
            .sum()
            .reset_index()
            .rename(columns={"index": "충전용량", 0: "충전기 수"})
        )
        output_distribution["충전용량"] = output_distribution[
            "충전용량"
        ].str.strip()
        st.bar_chart(
            output_distribution,
            x="충전용량",
            y="충전기 수",
            color="#16a34a",
            width="stretch",
        )

def render_realtime_map(
    charger_df: pd.DataFrame,
    user_location: tuple[float, float] | None = None,
) -> None:
    """실시간 충전기 데이터를 상태별 색상 점으로 지도에 표시합니다."""
    # pydeck 지도에 필요한 lat/lng 컬럼이 없으면 지도를 그릴 수 없습니다.
    if charger_df.empty or not {"lat", "lng"}.issubset(charger_df.columns):
        st.info("지도에 표시할 좌표 데이터가 없습니다.")
        return

    map_df = charger_df.dropna(subset=["lat", "lng"]).copy()
    if map_df.empty:
        st.info("지도에 표시할 좌표 데이터가 없습니다.")
        return

    # 지도 중심은 기본적으로 조회된 충전기들의 평균 좌표를 사용합니다.
    center_lat = float(map_df["lat"].mean())
    center_lng = float(map_df["lng"].mean())

    # 필터링된 데이터 개수에 따라 지도를 자동 확대/축소합니다.
    # 예: 경기도 전체는 넓게, 고양시/강남구처럼 좁은 지역은 더 확대합니다.
    if user_location:
        zoom_level = 12
    elif len(map_df) <= 1:
        zoom_level = 15
    elif len(map_df) < 30:
        zoom_level = 13
    elif len(map_df) < 100:
        zoom_level = 11
    else:
        zoom_level = 9

    # 추천 충전소에서 "지도에서 보기"를 누르면 해당 충전소만 표시하거나 지도 중심으로 잡습니다.
    selected_station = st.session_state.get("selected_station")
    show_selected_only = st.session_state.get("show_selected_station_only", False)

    if selected_station and show_selected_only and not user_location:
        selected_station = {
            **selected_station,
            "status_color": selected_station.get("status_color", [15, 23, 42, 120]),
        }
        map_df = pd.DataFrame([selected_station])

    if selected_station and not user_location:
        center_lat = float(selected_station["lat"])
        center_lng = float(selected_station["lng"])
        zoom_level = 17 if show_selected_only else 15

    # 충전기 위치 레이어입니다. status_color 컬럼으로 상태별 색상을 입힙니다.
    layers = [
        pdk.Layer(
            "ScatterplotLayer",
            data=map_df,
            get_position="[lng, lat]",
            get_radius=35,
            get_fill_color="status_color",
            pickable=True,
            auto_highlight=True,
        )
    ]


    # 추천 충전소 선택 위치를 반투명 검은색 점으로 강조합니다.
    if selected_station and not user_location:
        layers.append(
            pdk.Layer(
                "ScatterplotLayer",
                data=pd.DataFrame([selected_station]),
                get_position="[lng, lat]",
                get_radius=22,
                get_fill_color=[15, 23, 42, 120],
                pickable=True,
            )
        )

    # 내 위치 조회 탭에서는 사용자 위치를 별도 점으로 추가하고 지도의 중심으로 잡습니다.
    if user_location:
        user_lat, user_lng = user_location
        center_lat = user_lat
        center_lng = user_lng
        layers.append(
            pdk.Layer(
                "ScatterplotLayer",
                data=pd.DataFrame(
                    [{"lat": user_lat, "lng": user_lng, "label": "내 위치"}]
                ),
                get_position="[lng, lat]",
                get_radius=120,
                get_fill_color=[17, 24, 39, 230],
                pickable=True,
            )
        )

    # pydeck 지도 객체를 만들고, 마우스 오버 시 충전소 상세 정보를 보여줍니다.
    deck = pdk.Deck(
        map_style="https://basemaps.cartocdn.com/gl/positron-gl-style/style.json",
        initial_view_state=pdk.ViewState(
            latitude=center_lat,
            longitude=center_lng,
            zoom=zoom_level,
            pitch=0,
        ),
        layers=layers,
        tooltip={
            "html": (
                "<b>{statNm}</b><br/>"
                "{addr}<br/>"
                "상태: {stat_label}<br/>"
                "용량: {output} kW"
            )
        },
    )
    st.pydeck_chart(deck, width="stretch")

    if selected_station and not user_location:
        with st.container(border=True):
            st.markdown(f"### 📍 선택한 충전소: {selected_station.get('statNm', '-')}")
            st.write(f"🏠 주소: {selected_station.get('addr', '-')}")
            st.write(f"🟢 상태: {selected_station.get('stat_label', '-')}")
            st.write(f"⚡ 충전용량: {selected_station.get('output', '-')} kW")

            if st.button("선택한 충전소 해제"):
                st.session_state["show_selected_station_only"] = False
                st.session_state.pop("selected_station", None)
                st.rerun()


def render_detail_table(charger_df: pd.DataFrame, key: str) -> None:
    """충전기 목록을 한글 컬럼명으로 바꿔 상세 테이블로 표시합니다."""
    if charger_df.empty:
        st.info("조건에 맞는 충전기가 없습니다.")
        return

    # 거리 컬럼이 있는 경우 소수점 둘째 자리까지만 보여줍니다.
    table_df = charger_df.copy()
    if "distance_km" in table_df.columns:
        table_df["distance_km"] = table_df["distance_km"].round(2)
    if "statUpdDt" in table_df.columns:
        # API 원본은 yyyymmddhhmmss 형식입니다.
        # 화면에서는 날짜를 제외하고 hh시 mm분 ss초만 보여줍니다.
        table_df["statUpdDt"] = table_df["statUpdDt"].apply(format_status_time)

    # API마다 컬럼 유무가 다를 수 있어 존재하는 컬럼만 골라 표시합니다.
    columns = [column for column in DETAIL_COLUMNS if column in table_df.columns]
    st.dataframe(
        table_df[columns].rename(columns=DETAIL_COLUMN_LABELS),
        hide_index=True,
        width="stretch",
        key=key,
    )


def format_status_time(value: object) -> str:
    """API 상태갱신시각을 'hh시 mm분 ss초' 형식으로 바꿉니다."""
    if pd.isna(value):
        return "-"

    text = str(value).strip()
    if text.endswith(".0"):
        text = text[:-2]

    if len(text) < 14 or not text[:14].isdigit():
        return text or "-"

    hour = text[8:10]
    minute = text[10:12]
    second = text[12:14]
    return f"{hour}시 {minute}분 {second}초"


def render_realtime_empty_tabs(message: str) -> None:
    """실시간 데이터가 아직 없을 때도 주요 기능 탭을 화면에 표시합니다."""
    # API 키 누락, API 오류, 검색 결과 없음 같은 상황에서도 화면 구조는 유지합니다.
    tab_map, tab_available, tab_nearby, tab_table = st.tabs(
        [
            "🗺️ 실시간 지도",
            "⚡ 사용 가능",
            "📍 내 주변",
            "📋 상세 데이터",
        ]
    )

    with tab_map:
        st.info(message)
    with tab_available:
        st.info(message)
    with tab_nearby:
        st.info(message)
    with tab_table:
        st.info(message)


def render_realtime_dashboard(usage_df: pd.DataFrame) -> None:
    """공공데이터 OpenAPI를 호출해 충전소 상태 대시보드를 구성합니다."""
    st.subheader("실시간 충전소 현황")

    try:
        settings = get_settings()
    except SettingsError:
        st.warning(
            ".env 파일에 EV_CHARGER_API_KEY가 없습니다. "
            ".env.example을 참고해 API 키를 설정해주세요."
        )
        return

    # 기본 조회 지역은 서울특별시입니다.
    default_region = "서울특별시"
    if "api_region_from_csv" in st.session_state:
        default_region = st.session_state["api_region_from_csv"]

    region_names = list(REGION_CODES)
    default_index = (
        region_names.index(default_region)
        if default_region in region_names
        else 0
    )

    # 1단계: API에서 조회할 광역 지역을 선택하고, 필요하면 시군구/구/동을 선택합니다.
    st.markdown("#### 1단계. 조회 지역 선택")
    region_col, district_col = st.columns([1, 2])
    with region_col:
        selected_region = st.selectbox(
            "광역 지역 선택",
            options=region_names,
            index=default_index,
        )

    district_options = ["전체"]
    if not usage_df.empty and {"시군구", "api_region"}.issubset(usage_df.columns):
        district_series = (
            usage_df.loc[
                usage_df["api_region"] == selected_region,
                "시군구",
            ]
            .dropna()
            .astype(str)
            .str.strip()
            .replace({
                "고양": "고양시",
            })
        )
        district_options.extend(sorted(district_series.unique().tolist()))

    with district_col:
        selected_district = st.selectbox(
            "시군구/구/동 선택",
            options=district_options,
        )

    district_query = "" if selected_district == "전체" else selected_district

    st.caption(f"API 조회 지역: {selected_region}")

    # 광역 지역이나 시군구 선택이 바뀌면 이전에 선택한 추천 충전소 지도를 초기화합니다.
    current_area_key = f"{selected_region}-{district_query}"

    if st.session_state.get("current_area_key") != current_area_key:
        st.session_state["current_area_key"] = current_area_key
        st.session_state["show_selected_station_only"] = False
        st.session_state.pop("selected_station", None)

    col3, col4 = st.columns([1, 1])
    with col3:
        period = st.slider(
            "상태 갱신 범위(분)",
            min_value=5,
            max_value=60,
            value=10,
            step=5,
        )
    with col4:
        only_available = st.toggle("사용 가능만 보기", value=False)

    # 사용량 데이터와 조회 지역명이 연결되는 경우 사용자에게 알려줍니다.
    if not usage_df.empty:
        csv_regions = sorted(
            usage_df["api_region"].dropna().unique().tolist()
        )
        matched_csv_region = selected_region in csv_regions
        if matched_csv_region:
            st.caption(
                f"선택 지역은 사용량 데이터와 지역 코드가 연결됩니다: {selected_region}"
            )

    # 이미 데이터를 한 번 불러온 뒤에는 광역 지역이나 갱신 범위가 바뀌면 다시 조회합니다.
    # 첫 진입부터 서울특별시 전체 API 조회를 자동 실행하지 않고,
    # 최초 조회는 아래 "실시간 데이터 새로고침" 버튼을 눌렀을 때만 실행합니다.
    current_period = st.session_state.get("realtime_period")
    current_region = st.session_state.get("realtime_region")
    has_data = st.session_state.get("realtime_charger_df") is not None
    should_auto_load = (
        has_data
        and (
            current_region != selected_region
            or current_period != period
        )
    )

    manual_refresh = st.button("2단계. 실시간 데이터 새로고침", type="primary")

    if should_auto_load or manual_refresh:
        try:
            with st.spinner("충전소 기본정보와 실시간 상태를 불러오는 중입니다."):
                zcode = REGION_CODES[selected_region]
                # 기본정보와 실시간 상태정보를 각각 가져온 뒤 statId/chgerId 기준으로 결합합니다.
                info_items = load_realtime_info(settings.charger_api, zcode)
                status_items = load_realtime_status(
                    settings.charger_api,
                    zcode,
                    period,
                )
                charger_df = merge_charger_data(info_items, status_items)
                # 병합된 원본 데이터에 상태 라벨, 지도 색상, 숫자형 좌표 등을 추가합니다.
                st.session_state["realtime_charger_df"] = enrich_realtime_data(
                    charger_df
                )
                st.session_state["realtime_region"] = selected_region
                st.session_state["realtime_period"] = period
                st.session_state["show_selected_station_only"] = False
                st.session_state.pop("selected_station", None)
        except ChargerAPIError as exc:
            st.error(str(exc))
            render_realtime_empty_tabs("실시간 데이터를 불러오지 못했습니다. 잠시 후 다시 시도해주세요.")
            return

    # 조회 결과는 session_state에 저장해 화면 조작 때마다 API를 다시 부르지 않습니다.
    charger_df = st.session_state.get("realtime_charger_df")
    realtime_region = st.session_state.get("realtime_region")

    if charger_df is None or realtime_region != selected_region:
        render_realtime_empty_tabs(
            "지역을 선택한 뒤 '2단계. 실시간 데이터 새로고침' 버튼을 눌러주세요."
        )
        return

    if charger_df.empty:
        render_realtime_empty_tabs("조회된 실시간 충전기 데이터가 없습니다.")
        return
    st.success(f"현재 조회 지역: {selected_region}")

    # 사용 가능만 보기 토글이 켜져 있으면 충전 대기 상태(stat == "2")만 남깁니다.
    filtered_df = charger_df.copy()
    if only_available:
        filtered_df = filtered_df[
            filtered_df["stat"].astype(str) == AVAILABLE_STATUS
        ]

    st.markdown("#### 선택 사항. 충전소명 또는 상세 주소로 더 좁히기")
    search_text = st.text_input(
        "충전소명 또는 주소 검색",
        placeholder="예: 고양시청, 킨텍스, 백석역처럼 특정 충전소를 찾을 때만 입력",
        key="station_address_search",
    )

    if search_text:
        st.session_state["show_selected_station_only"] = False
        st.session_state.pop("selected_station", None)



    # 상태 필터입니다. 예: 충전 대기, 충전 중, 점검 중 등.
    status_options = [
        label
        for code, label in STATUS_LABELS.items()
        if code in filtered_df["stat"].astype(str).unique()
    ]
    selected_statuses = st.multiselect(
        "상태 필터",
        options=status_options,
        default=status_options,
    )
    if selected_statuses:
        filtered_df = filtered_df[
            filtered_df["stat_label"].isin(selected_statuses)
        ]

    # 충전용량 필터입니다. 예: 50kW, 100kW, 200kW 등.
    output_values = sorted(filtered_df["output"].dropna().unique().tolist())
    selected_outputs = st.multiselect(
        "충전용량 필터",
        options=output_values,
        default=output_values,
        format_func=lambda value: f"{value:g} kW",
    )
    if selected_outputs:
        filtered_df = filtered_df[filtered_df["output"].isin(selected_outputs)]

    # 1단계에서 선택한 시군구/구/동 기준으로 먼저 필터링합니다.
    if district_query:
        district_mask = filtered_df.get("addr", pd.Series("", index=filtered_df.index)).astype(str).str.contains(
            district_query,
            case=False,
            na=False,
        )
        filtered_df = filtered_df[district_mask]

    # 선택 사항 검색창에 입력한 충전소명 또는 주소 기준으로 결과를 한 번 더 좁힙니다.
    if search_text:
        mask = (
            filtered_df.get("statNm", pd.Series("", index=filtered_df.index))
            .astype(str)
            .str.contains(search_text, case=False, na=False)
            | filtered_df.get("addr", pd.Series("", index=filtered_df.index))
            .astype(str)
            .str.contains(search_text, case=False, na=False)
        )
        filtered_df = filtered_df[mask]

    if filtered_df.empty:
        render_realtime_empty_tabs("검색 조건에 맞는 충전소가 없습니다.")
        return

    # 최종 필터링된 결과 기준으로 사용 가능률과 혼잡도를 표시합니다.
    render_dashboard_summary(filtered_df)

    st.markdown("### 🗺️ 실시간 지도")
    render_realtime_map(filtered_df)

    recommended = (
        # 사용 가능한 충전기 중 충전용량이 큰 순서로 상위 충전소를 추천합니다.
        # 같은 충전소에 충전기가 여러 대 있으면 충전소명 기준으로 한 번만 보여줍니다.
        filtered_df[filtered_df["stat"].astype(str) == AVAILABLE_STATUS]
        .sort_values("output", ascending=False)
        .drop_duplicates(subset=["statNm"])
        .head(5)
    )

    st.markdown("### 🏆 추천 충전소 TOP 5")

    if recommended.empty:
        st.info("현재 조건에 맞는 사용 가능 추천 충전소가 없습니다.")
    else:
        rank_badges = ["🥇", "🥈", "🥉", "🏅", "🏅"]
        for index, (_, row) in enumerate(recommended.iterrows(), start=1):
            rank_badge = rank_badges[index - 1]
            station_name = row["statNm"]
            station_addr = row["addr"]
            output_value = row.get("output", "-")
            output_badge = "초급속" if pd.notna(output_value) and float(output_value) >= 200 else "급속/완속"

            with st.container(border=True):
                # 추천 충전소마다 길찾기 링크와 지도 포커스 버튼을 제공합니다.
                info_col, action_col = st.columns([5, 2])
                with info_col:
                    st.markdown(f"**{rank_badge} {station_name}**")
                    st.caption(f"⚡ {output_value} kW · {output_badge}  |  🟢 {row.get('stat_label', '사용 가능')}")
                    st.caption(f"🏠 {station_addr}")
                with action_col:
                    st.link_button(
                        "길찾기",
                        f"https://map.naver.com/p/search/{station_addr}",
                        use_container_width=True,
                    )
                    if st.button(
                        "지도에서 보기",
                        key=f"focus_recommended_station_{index}_{row['statNm']}",
                        use_container_width=True,
                    ):
                        # 좌표가 있는 추천 충전소만 지도 중심으로 이동할 수 있습니다.
                        if pd.isna(row.get("lat")) or pd.isna(row.get("lng")):
                            st.warning("이 충전소는 좌표 정보가 없어 지도로 이동할 수 없습니다.")
                        else:
                            st.session_state["selected_station"] = {
                                "statNm": row["statNm"],
                                "addr": row["addr"],
                                "stat_label": row.get("stat_label", ""),
                                "output": row.get("output", ""),
                                "distance_km": row.get("distance_km", ""),
                                "lat": float(row["lat"]),
                                "lng": float(row["lng"]),
                                "status_color": [15, 23, 42, 120],
                            }
                            st.session_state["show_selected_station_only"] = True
                            st.rerun()

    # 필터링된 데이터 기준으로 상태별/용량별 그래프를 표시합니다.
    chart_left, chart_right = st.columns(2)
    with chart_left:
        st.markdown("#### 상태별 충전기 수")
        # 필터링된 결과를 상태 라벨별로 집계해 막대그래프로 표시합니다.
        status_counts = (
            filtered_df["stat_label"]
            .value_counts()
            .reindex(STATUS_LABELS.values(), fill_value=0)
            .reset_index()
        )
        status_counts.columns = ["상태", "충전기 수"]
        st.bar_chart(
            status_counts,
            x="상태",
            y="충전기 수",
            color="#2563eb",
            width="stretch",
        )

    with chart_right:
        st.markdown("#### 충전용량별 충전기 수")
        # 충전용량(output)별 충전기 수를 집계합니다.
        output_counts = (
            filtered_df.dropna(subset=["output"])
            .groupby("output", as_index=False)
            .size()
            .rename(columns={"size": "충전기 수"})
        )
        st.bar_chart(
            output_counts,
            x="output",
            y="충전기 수",
            color="#16a34a",
            width="stretch",
        )

    tab_map, tab_available, tab_nearby, tab_table = st.tabs(
        [
            "🗺️ 실시간 지도",
            "⚡ 사용 가능",
            "📍 내 주변",
            "📋 상세 데이터",
        ]
    )

    # 실시간 지도는 상단에 먼저 표시했으므로 탭 안에서는 안내 문구만 표시합니다.
    with tab_map:
        st.info("실시간 지도는 추천 충전소 TOP5 위쪽에 먼저 표시됩니다.")

    # stat == "2"인 현재 충전 대기 충전기만 별도로 보여주는 탭입니다.
    with tab_available:
        available_df = filtered_df[
            filtered_df["stat"].astype(str) == AVAILABLE_STATUS
        ].copy()
        selected_available_output = st.selectbox(
            "사용 가능 리스트에서 볼 충전용량",
            options=["전체", *sorted(available_df["output"].dropna().unique())],
            format_func=lambda value: (
                "전체" if value == "전체" else f"{value:g} kW"
            ),
        )
        if selected_available_output != "전체":
            available_df = available_df[
                available_df["output"] == selected_available_output
            ]
        render_detail_table(available_df, "available_table")

    # 사용자가 입력한 현재 위치 기준으로 반경 내 충전기를 찾는 탭입니다.
    with tab_nearby:
        st.caption(
            "현재 위치 가져오기를 누른 뒤 브라우저 위치 권한을 허용하면 가까운 충전소를 찾을 수 있습니다."
        )

        if streamlit_geolocation is None:
            st.warning(
                "내 주변 조회를 사용하려면 streamlit-geolocation 패키지를 설치해주세요."
            )
            location = None
        else:
            location = streamlit_geolocation()

        radius_km = st.number_input(
            "반경(km)",
            min_value=0.1,
            max_value=20.0,
            value=1.0,
            step=0.1,
        )

        if not location or location.get("latitude") is None:
            st.info("📍 브라우저 위치 권한을 허용하면 주변 충전소를 조회할 수 있습니다.")
            return

        # 브라우저에서 받은 현재 위치 좌표입니다.
        user_lat = float(location["latitude"])
        user_lng = float(location["longitude"])

        st.success(
            f"현재 위치: 위도 {user_lat:.5f}, 경도 {user_lng:.5f}"
        )

        # 모든 충전기에 거리 컬럼을 붙인 뒤 반경 안쪽 데이터만 남깁니다.
        distance_df = add_distance(filtered_df, user_lat, user_lng)

        if "distance_km" not in distance_df.columns:
            st.info("현재 조건에 맞는 좌표 데이터가 없어 주변 충전소를 계산할 수 없습니다.")

            nearby_df = pd.DataFrame()
            nearby_available_df = pd.DataFrame()

        else:
            nearby_df = distance_df[
                distance_df["distance_km"] <= radius_km
            ]

            nearby_available_df = nearby_df[
                nearby_df["stat"].astype(str) == AVAILABLE_STATUS
            ]

        # 반경 내 전체/사용 가능/가장 가까운 거리 지표를 표시합니다.
        ncol1, ncol2, ncol3 = st.columns(3)
        ncol1.metric("반경 내 충전기", f"{len(nearby_df):,}대")
        ncol2.metric("반경 내 사용 가능", f"{len(nearby_available_df):,}대")
        ncol3.metric(
            "가장 가까운 거리",
            (
                f"{nearby_df['distance_km'].min():.2f} km"
                if not nearby_df.empty
                else "-"
            ),
        )

        # 내 위치와 반경 내 충전기를 지도에 같이 표시합니다.
        render_realtime_map(nearby_df, user_location=(user_lat, user_lng))
        st.markdown("#### 1km 이내 사용 가능 충전기")
        render_detail_table(nearby_available_df, "nearby_available_table")

    # 현재 필터 조건이 적용된 전체 상세 데이터입니다.
    with tab_table:
        render_detail_table(filtered_df, "all_charger_table")


def render_usage_analysis_dashboard() -> None:
    """DB 기반 사용량 분석 화면을 구성합니다."""
    usage_df = load_usage_data()
    render_usage_overview(usage_df)

def render_search_locale_dashboard() -> None:
    """Backward-compatible wrapper for older imports."""
    render_usage_analysis_dashboard()


def main() -> None:
    """앱의 시작점입니다."""
    st.set_page_config(
        page_title="전기차 충전소 실시간 대시보드",
        page_icon="⚡",
        layout="wide",
    )
    apply_naver_style()
    render_app_header()
    render_usage_analysis_dashboard()


if __name__ == "__main__":
    main()
