"""프로젝트 실행에 필요한 Python 환경과 패키지를 점검합니다."""

from __future__ import annotations

import sys
from importlib import import_module
from importlib.util import find_spec
from importlib.metadata import PackageNotFoundError, version
from pathlib import Path


# PyPI 패키지 이름과 Python에서 사용하는 import 이름
REQUIRED_PACKAGES = {
    "streamlit": "streamlit",
    "pandas": "pandas",
    "requests": "requests",
    "geopy": "geopy",
    "pydeck": "pydeck",
    "python-dotenv": "dotenv",
}

PROJECT_ROOT = Path(__file__).resolve().parent
VENV_PATH = PROJECT_ROOT / ".venv"


def is_project_venv_active() -> bool:
    """현재 Python이 프로젝트의 .venv에서 실행 중인지 확인합니다."""
    try:
        return Path(sys.prefix).resolve() == VENV_PATH.resolve()
    except FileNotFoundError:
        return False


def find_missing_packages() -> list[str]:
    """필수 패키지 중 설치되지 않은 패키지 이름을 반환합니다."""
    missing_packages = []

    for package_name in REQUIRED_PACKAGES:
        try:
            version(package_name)
        except PackageNotFoundError:
            missing_packages.append(package_name)

    return missing_packages


def is_pip_available() -> bool:
    """현재 Python 환경에서 pip를 실행할 수 있는지 확인합니다."""
    return find_spec("pip") is not None


def print_install_command() -> None:
    """pip 설치 상태에 맞는 의존성 설치 명령을 출력합니다."""
    if is_pip_available():
        print("설치 명령: python -m pip install -r requirements.txt")
    else:
        print("pip 준비 명령: python -m ensurepip --upgrade")
        print("설치 명령: python -m pip install -r requirements.txt")


def print_installed_versions() -> None:
    """설치된 필수 패키지의 버전을 출력합니다."""
    print("\n[설치된 패키지 버전]")
    for package_name in REQUIRED_PACKAGES:
        print(f"- {package_name}: {version(package_name)}")


def find_import_failures() -> list[tuple[str, str]]:
    """설치된 패키지를 실제로 import할 수 있는지 확인합니다."""
    failures = []

    print("\n[모듈 import 확인]")
    for package_name, module_name in REQUIRED_PACKAGES.items():
        try:
            import_module(module_name)
            print(f"- {package_name}: 성공")
        except ImportError as exc:
            failures.append((package_name, str(exc)))
            print(f"- {package_name}: 실패 ({exc})")

    return failures


def main() -> int:
    """환경 점검 결과를 출력하고 성공 여부를 종료 코드로 반환합니다."""
    print(f"Python 실행 경로: {sys.executable}")

    if is_project_venv_active():
        print("가상환경: 프로젝트 .venv가 활성화되어 있습니다.")
    else:
        print("가상환경: 프로젝트 .venv가 활성화되어 있지 않습니다.")
        print("활성화 명령: source .venv/bin/activate")

    missing_packages = find_missing_packages()
    if missing_packages:
        print("\n설치되지 않은 필수 패키지:")
        for package_name in missing_packages:
            print(f"- {package_name}")
        print()
        print_install_command()
        return 1

    print("\n필수 패키지가 모두 설치되어 있습니다.")
    print_installed_versions()

    if find_import_failures():
        print("\n일부 패키지를 import하지 못했습니다.")
        print_install_command()
        return 1

    print("\n환경 점검을 통과했습니다.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
