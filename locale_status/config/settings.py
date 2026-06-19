from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv


# 프로젝트 기준 경로와 데이터 파일 위치를 한곳에서 관리합니다.
# 다른 파일에서는 문자열 경로를 직접 만들지 않고 아래 상수를 가져다 씁니다.
BASE_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = BASE_DIR / "Data"
ENV_PATH = BASE_DIR / ".env"
PROJECT_ENV_PATH = BASE_DIR.parent / ".env"
USAGE_CSV_PATH = DATA_DIR / "test_data.csv"
COORDS_CSV_PATH = DATA_DIR / "coords.csv"

API_BASE_URL = "https://apis.data.go.kr/B552584/EvCharger"

# 공공데이터 충전소 API에서 사용하는 광역지자체 코드입니다.
# 화면에서는 한글 지역명을 보여주고, API 요청에는 오른쪽 숫자 코드를 보냅니다.
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

# API 상태값 중 "2"가 충전 대기, 즉 현재 사용 가능한 충전기입니다.
AVAILABLE_STATUS = "2"
AVAILABLE_STATUS_LABEL = "충전 대기"

# API가 숫자로 내려주는 상태 코드를 화면에 보여줄 한글 라벨로 바꿉니다.
STATUS_LABELS = {
    "1": "통신 이상",
    "2": "충전 대기",
    "3": "충전 중",
    "4": "운영 중지",
    "5": "점검 중",
    "9": "상태 미확인",
}

# 지도 위 점 색상입니다. 상태 코드별로 RGBA 색상을 지정합니다.
STATUS_COLORS = {
    "1": [239, 68, 68, 190],
    "2": [34, 197, 94, 210],
    "3": [59, 130, 246, 200],
    "4": [107, 114, 128, 190],
    "5": [245, 158, 11, 200],
    "9": [148, 163, 184, 180],
}

# CSV의 짧은 지역명(서울, 경기 등)을 API가 쓰는 공식 지역명으로 맞춥니다.
REGION_NAME_ALIASES = {
    "서울": "서울특별시",
    "부산": "부산광역시",
    "대구": "대구광역시",
    "인천": "인천광역시",
    "광주": "광주광역시",
    "대전": "대전광역시",
    "울산": "울산광역시",
    "세종": "세종특별자치시",
    "경기": "경기도",
    "강원": "강원특별자치도",
    "충북": "충청북도",
    "충남": "충청남도",
    "전북": "전북특별자치도",
    "전남": "전라남도",
    "경북": "경상북도",
    "경남": "경상남도",
    "제주": "제주특별자치도",
}

# 상세 테이블에 보여줄 API 컬럼 순서입니다.
DETAIL_COLUMNS = [
    "statNm",
    "chgerId",
    "addr",
    "stat_label",
    "output",
    "method",
    "useTime",
    "distance_km",
    "statUpdDt",
]

# API 원본 컬럼명을 사용자가 읽기 쉬운 한글명으로 바꿉니다.
DETAIL_COLUMN_LABELS = {
    "statNm": "충전소명",
    "chgerId": "충전기ID",
    "addr": "주소",
    "stat_label": "상태",
    "output": "충전용량(kW)",
    "method": "충전방식",
    "useTime": "이용시간",
    "distance_km": "거리(km)",
    "statUpdDt": "상태갱신시각",
}


class SettingsError(ValueError):
    """필수 설정이 없을 때 화면에 보여줄 예외."""


@dataclass(frozen=True)
class ChargerApiSettings:
    # API 호출에 필요한 인증키와 기본 URL을 묶어 전달하기 위한 설정 객체입니다.
    service_key: str
    base_url: str = API_BASE_URL


@dataclass(frozen=True)
class AppSettings:
    # 앱 전체에서 공통으로 사용하는 설정을 한 객체에 모아둡니다.
    charger_api: ChargerApiSettings
    base_dir: Path = BASE_DIR
    data_dir: Path = DATA_DIR
    usage_csv_path: Path = USAGE_CSV_PATH
    coords_csv_path: Path = COORDS_CSV_PATH


def get_settings() -> AppSettings:
    """앱 전체에서 사용할 설정을 만든다."""
    # .env 파일에서 EV_CHARGER_API_KEY를 읽어옵니다.
    # serar_locale/.env가 없어도 상위 프로젝트 폴더의 .env를 함께 확인합니다.
    # 키가 없으면 실시간 API 탭을 사용할 수 없으므로 명확한 오류를 냅니다.
    load_dotenv(PROJECT_ENV_PATH, override=False)
    load_dotenv(ENV_PATH, override=False)
    service_key = os.getenv("EV_CHARGER_API_KEY", "").strip()
    if not service_key:
        raise SettingsError("EV_CHARGER_API_KEY 환경변수가 설정되지 않았습니다.")

    return AppSettings(charger_api=ChargerApiSettings(service_key=service_key))
