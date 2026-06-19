"""환경변수 기반 설정 파일.

.env에 작성한 네이버 API Key와 DB 접속 정보를 앱에서 사용할 수 있는 객체로 변환한다.
"""

from dataclasses import dataclass
from pathlib import Path
import os

from dotenv import load_dotenv


BASE_DIR = Path(__file__).resolve().parents[1]
ENV_PATH = BASE_DIR / ".env"

# .env 파일에 작성한 API Key와 DB 접속 정보를 환경변수로 등록한다.
# streamlit_naver_news/config/settings.py 기준으로 두 단계 위가 03_data_collection 폴더이다.
load_dotenv(ENV_PATH)
class SettingsError(ValueError):
    """필수 환경변수가 없을 때 화면에 보여줄 예외."""

# @dataclass: 데이터를 담기 위한 클래스를 간단하게 만들 수 있게 해주는 문법
# frozen=True: 객체를 만든 뒤 값을 바꾸지 못하게 하는 옵션
@dataclass(frozen=True)
class NaverApiSettings:
    """네이버 OpenAPI 인증에 필요한 설정."""

    client_id: str
    client_secret: str

    @property
    def headers(self) -> dict[str, str]:
        """네이버 API 요청에 필요한 인증 헤더를 만든다."""

        return {
            "X-Naver-Client-Id": self.client_id,
            "X-Naver-Client-Secret": self.client_secret,
        }


@dataclass(frozen=True)
class DatabaseSettings:
    """MySQL 접속에 필요한 설정."""

    host: str
    port: int
    user: str
    password: str
    database: str


@dataclass(frozen=True)
class AppSettings:
    """앱에서 사용하는 설정을 API 설정과 DB 설정으로 묶은 객체."""

    naver_api: NaverApiSettings
    database: DatabaseSettings


def _env_value(*names: str, default: str | None = None) -> str | None:
    for name in names:
        value = os.getenv(name)
        if value:
            return value
    return default


def _required_env(name: str) -> str:
    """필수 환경변수를 읽고, 없으면 어떤 값이 빠졌는지 알려준다."""

    value = os.getenv(name)
    if not value:
        raise SettingsError(f"{name} 환경변수가 설정되지 않았습니다.")
    return value


def get_settings() -> DatabaseSettings:
    """앱 전체에서 사용할 설정을 한 번에 만든다."""

    # API Key는 반드시 발급받아야 하므로 없으면 화면에 오류를 표시한다.
    # DB 정보는 수업용 기본값을 두어 .env 작성량을 줄였다.
    return DatabaseSettings(
            host=_env_value("DB_HOST", "MYSQL_HOST", default="localhost"),
            port=int(_env_value("DB_PORT", "MYSQL_PORT", default="3306")),
            user=_env_value("DB_USER", "MYSQL_USER"),
            password=_env_value("DB_PASSWORD", "MYSQL_PASSWORD", default=""),
            database=_env_value("DB_DATABASE", "MYSQL_DATABASE", default="ev_charger_dashboard")
    )
