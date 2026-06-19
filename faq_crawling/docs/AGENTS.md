

Streamlit으로 전기차 충전소 대시보드를 구현해줘.

목표:
한국환경공단 전기차 충전소 API 데이터를 사용해서 충전소 지도와 실시간 상태 대시보드를 만든다.

사용 API:
- getChargerInfo: 충전소 기본정보
- getChargerStatus: 충전기 실시간 상태정보

주요 기능:
1. 지역 선택 필터
2. 충전소 지도 표시
3. 충전기 상태별 색상 표시
   - 1: 통신 이상
   - 2: 충전 대기
   - 3: 충전 중
   - 4: 운영 중지
   - 5: 점검 중
   - 9: 상태 미확인
4. 전체 충전소 수, 충전기 수, 사용 가능 충전기 수 metric 표시
5. 상태별 충전기 개수 막대그래프
6. 충전 용량(output)별 분포 그래프
7. 충전소 상세 테이블 표시

기술 조건:
- Python
- Streamlit
- pandas
- requests
- pydeck 또는 folium
- API 키는 .env 파일에서 불러오기
- 데이터 요청 함수는 src/api.py로 분리
- 전처리 함수는 src/preprocess.py로 분리
- Streamlit 실행 파일은 app.py로 작성

폴더 구조:
ev_charger_dashboard/
├── app.py
├── .env.example
├── requirements.txt
├── src/
│   ├── api.py
│   ├── preprocess.py
│   └── constants.py
└── README.md

먼저 전체 파일 구조를 만들고, 실행 가능한 최소 버전부터 구현해줘.