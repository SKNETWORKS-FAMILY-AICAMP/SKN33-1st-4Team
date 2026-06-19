from __future__ import annotations

from pathlib import Path


def get_project_root() -> Path:
    """현재 파일 위치를 기준으로 프로젝트 루트 경로를 반환합니다."""
    return Path(__file__).resolve().parents[1]
