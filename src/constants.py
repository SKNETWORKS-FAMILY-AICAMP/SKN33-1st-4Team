# 공공데이터 API 기본 주소입니다.
# 상세 기능명(getChargerStatus, getChargerInfo)을 뒤에 붙여 호출합니다.
API_BASE_URL = "http://apis.data.go.kr/B552584/EvCharger"

# 공공데이터포털 API가 간헐적으로 느리게 응답하므로 연결/읽기 timeout을 분리합니다.
API_CONNECT_TIMEOUT = 10
API_READ_TIMEOUT = 120
API_NUM_OF_ROWS = 10
API_STATUS_PERIOD = 5

# 지역 이름을 API 코드로 변환
REGION_CODES = {
    "서울특별시": "11",
    "부산광역시": "26",
    "대구광역시": "27",
    "인천광역시": "28",
    "광주광역시": "29",
    "대전광역시": "30",
    "울산광역시": "31",
    "세종특별자치시": "36",
    "경기도": "41",
    "충청북도": "43",
    "충청남도": "44",
    "전라남도": "46",
    "경상북도": "47",
    "경상남도": "48",
    "제주특별자치도": "50",
    "강원특별자치도": "51",
    "전북특별자치도": "52",
}

# 사용 가능한 충전기 상태 코드
AVAILABLE_STATUS = "2"
# 상태 코드를 화면 문구로 표시
AVAILABLE_STATUS_LABEL = "충전 대기"
