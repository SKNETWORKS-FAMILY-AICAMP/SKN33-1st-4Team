import streamlit as st
import pydeck as pdk

import locale_service.charge_station_map as map

def view_station_map():

    # 선택된 충전소 id 저장
    if "selected_cs_id" not in st.session_state:
        st.session_state.selected_cs_id = '1'

    # 충전소 정보 호출
    map_df = map.get_station_coord_to_df()

    # 지도 데이터가 비었는지 확인
    if map_df.empty:
        # 표시할 좌표가 없음을 안내
        st.error("지도에 표시할 좌표가 없습니다.")
    else:
        # 중심 좌표
        center_lat = map_df["lat"].mean()
        center_lon = map_df["lon"].mean()

        # 충전소 좌표를 지도에 표시
        # 마커 레이어
        layer = pdk.Layer(
            "ScatterplotLayer",
            data=map_df,
            id="geojson-scatterplot-layer",
            location=[center_lat, center_lon],
            get_position=["lon", "lat"],
            get_radius=300,
            radius_min_pixels=5,
            radius_max_pixels=50,
            get_fill_color=[255, 140, 0, 160],
            pickable=True,
            auto_highlight=True
        )

        # 초기 지도 위치 설정
        view_state = pdk.ViewState(
            latitude=map_df["lat"].mean(),
            longitude=map_df["lon"].mean(),
            zoom=6
        )

        # 지도 객체 생성
        deck = pdk.Deck(
            layers=[layer],
            initial_view_state=view_state,
            map_style="light",
            tooltip={"text": "{충전소 이름}"}  # hover 시 표시
        )

        # 클릭이벤트
        event = (
            st.pydeck_chart(
                deck,
                on_select="rerun",
                selection_mode="single-object"
            ))


        st.subheader("선택된 충전소 정보")
        layer_name = 'geojson-scatterplot-layer'

        if (event and
                "selection" in event and
                "objects" in event["selection"] and
                layer_name in event["selection"]["objects"]):
            objects = event['selection']['objects']
            selected = objects[layer_name][0]
            st.session_state.selected_cs_id = selected["id"]
            detail_df = map.get_station_details(
                st.session_state.selected_cs_id
            )
            st.table(detail_df)
        else:
            st.info("지도에서 포인트를 클릭하세요.")

        # 지도에 사용한 좌표를 표로 표시
        st.subheader('충전소 목록')
        st.dataframe(map_df[["충전소 이름", "lat", "lon"]])


def view_station_by_region():
    st.subheader('지역구별 전기차 충전소 분포')
    if "selected_sido_code" not in st.session_state:
        st.session_state.selected_sido_code = '11'

    summary_df = map.get_station_by_region_summary_df()
    st.dataframe(summary_df[['시/도' ,'시/군/구', '충전소 수']])

    sido = map.get_sido()

    if sido.empty:
        st.error("시/도 정보가 없습니다.")
    else:
        sido_dict = dict(zip(sido.iloc[:, 0].astype(str), sido.iloc[:, 1]))

        if st.session_state.selected_sido_code not in sido_dict:
            st.session_state.selected_sido_code = list(sido_dict.keys())[0]

        selected_sido_code = st.selectbox(
            "시도 선택",
            options=list(sido_dict.keys()),
            format_func=lambda x: sido_dict[x],
            key="selected_sido_code"  # 이 key가 위의 session_state와 연결됩니다.
        )

        # 선택된 시도 코드에 따라 시군구 데이터 가져오기
        sigungu = map.get_sigungu(selected_sido_code)

        if not sigungu.empty:
            # 시군구 딕셔너리 변환 (0번째 컬럼: 코드, 1번째 컬럼: 이름)
            sigungu_dict = dict(zip(sigungu.iloc[:, 0].astype(str), sigungu.iloc[:, 1]))

            # 시군구 선택 상자
            selected_sigungu_code = st.selectbox(
                "시군구 선택",
                options=list(sigungu_dict.keys()),
                format_func=lambda x: sigungu_dict[x],
                key="selected_sigungu_cd"
            )

            selected_sigungu_name = sigungu_dict[selected_sigungu_code]

            # 시군구 코드로 충전소 데이터 조회 및 출력
            map_df = map.get_station_by_region(selected_sigungu_code)

            if map_df.empty:
                st.error(f'선택한 지역({selected_sigungu_name})에 전기차 충전소가 조회되지 않습니다.')
            else:
                st.write(f"### {selected_sigungu_name} 충전소 목록")
                # 지도
                # 중심 좌표
                center_lat = map_df["lat"].mean()
                center_lon = map_df["lon"].mean()

                # 충전소 좌표를 지도에 표시
                # 마커 레이어
                layer = pdk.Layer(
                    "ScatterplotLayer",
                    data=map_df,
                    id="geojson-scatterplot-layer",
                    location=[center_lat, center_lon],
                    get_position=["lon", "lat"],
                    get_radius=300,
                    radius_min_pixels=5,
                    radius_max_pixels=10,
                    get_fill_color=[255, 140, 0, 160],
                    pickable=True,
                    auto_highlight=True
                )

                # 초기 지도 위치 설정
                view_state = pdk.ViewState(
                    latitude=map_df["lat"].mean(),
                    longitude=map_df["lon"].mean(),
                    zoom=12
                )

                # 지도 객체 생성
                deck = pdk.Deck(
                    layers=[layer],
                    initial_view_state=view_state,
                    map_style="light",
                    tooltip={"text": "{충전소 이름}"}  # hover 시 표시
                )

                # 클릭이벤트
                event = (
                    st.pydeck_chart(
                        deck,
                        on_select="rerun",
                        selection_mode="single-object"
                    ))

                st.subheader("선택된 충전소 정보")
                layer_name = 'geojson-scatterplot-layer'

                if (event and
                        "selection" in event and
                        "objects" in event["selection"] and
                        layer_name in event["selection"]["objects"]):
                    objects = event['selection']['objects']
                    selected = objects[layer_name][0]
                    st.session_state.selected_cs_id = selected["충전소 id"]
                    detail_df = map.get_station_details(
                        st.session_state.selected_cs_id
                    )
                    st.table(detail_df)
                else:
                    st.info("지도에서 포인트를 클릭하세요.")
                st.dataframe(map_df)
        else:
            st.warning("선택한 시도에 해당하는 시군구 정보가 없습니다.")

