from __future__ import annotations

import argparse
import os
from datetime import datetime
from pathlib import Path

import pandas as pd
from dotenv import load_dotenv

from src.api_fields import EXPORT_METADATA_COLUMNS, SELECTED_COLUMNS_BY_ENDPOINT
from src.collect.ev_charger_client import EvChargerAPIError, EvChargerClient
from src.constants import REGION_CODES


DEFAULT_ENDPOINTS = tuple(SELECTED_COLUMNS_BY_ENDPOINT.keys())


def main() -> None:
    """OpenAPI에서 필요한 컬럼만 수집해 CSV 백업 파일로 저장합니다."""
    args = _parse_args()
    project_root = Path(__file__).resolve().parents[2]
    env_path = project_root / ".env"
    load_dotenv(dotenv_path=env_path, override=False)

    api_key = os.getenv("EV_CHARGER_API_KEY", "").strip()
    client = EvChargerClient(api_key, timeout=args.timeout)

    output_dir = (project_root / args.output_dir).resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    zcode_values = _resolve_zcodes(args)
    fetched_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    filename_timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    try:
        for endpoint in args.endpoint:
            selected_df = _collect_selected_rows(
                client=client,
                endpoint=endpoint,
                zcode_values=zcode_values,
                period=args.period,
                num_of_rows=args.num_of_rows,
                max_pages=args.max_pages,
                fetched_at=fetched_at,
            )
            output_path = output_dir / f"{endpoint}_selected_{filename_timestamp}.csv"
            selected_df.to_csv(output_path, index=False, encoding="utf-8-sig")
            print(f"Wrote {len(selected_df)} rows: {output_path}")
    except EvChargerAPIError as exc:
        raise SystemExit(str(exc)) from exc


def _collect_selected_rows(
    *,
    client: EvChargerClient,
    endpoint: str,
    zcode_values: list[str | None],
    period: int,
    num_of_rows: int,
    max_pages: int | None,
    fetched_at: str,
) -> pd.DataFrame:
    """여러 지역의 API 응답을 모아 선택 컬럼만 남긴 DataFrame을 만듭니다."""
    selected_columns = SELECTED_COLUMNS_BY_ENDPOINT[endpoint]
    rows: list[dict[str, str]] = []

    for zcode in zcode_values:
        # 상태 조회에만 period 파라미터가 필요합니다.
        endpoint_rows = client.fetch_all(
            endpoint,
            zcode=zcode,
            period=period if endpoint == "getChargerStatus" else None,
            num_of_rows=num_of_rows,
            max_pages=max_pages,
        )

        # API 원본 row에서 프로젝트에 필요한 컬럼만 추출합니다.
        for row in endpoint_rows:
            selected_row = {
                column: row.get(column, "")
                for column in selected_columns
            }
            selected_row["source_endpoint"] = endpoint
            selected_row["requested_zcode"] = zcode or ""
            selected_row["fetched_at"] = fetched_at
            rows.append(selected_row)

    # 응답이 0건이어도 CSV 헤더는 유지되도록 컬럼 순서를 명시합니다.
    return pd.DataFrame(
        rows,
        columns=[*selected_columns, *EXPORT_METADATA_COLUMNS],
    )


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="전기차 충전소 OpenAPI에서 선택 컬럼만 CSV로 저장합니다.",
    )
    parser.add_argument(
        "--endpoint",
        action="append",
        choices=DEFAULT_ENDPOINTS,
        default=None,
        help="수집할 엔드포인트입니다. 여러 번 지정할 수 있습니다.",
    )
    parser.add_argument(
        "--zcode",
        action="append",
        default=None,
        help="수집할 시도 코드입니다. 여러 번 지정할 수 있습니다.",
    )
    parser.add_argument(
        "--all-regions",
        action="store_true",
        help="src.constants.REGION_CODES에 정의된 모든 시도 코드를 수집합니다.",
    )
    parser.add_argument(
        "--period",
        type=int,
        default=10,
        help="getChargerStatus 상태갱신 조회 범위입니다. API 문서 기준 최대 10분입니다.",
    )
    parser.add_argument(
        "--num-of-rows",
        type=int,
        default=9999,
        help="한 페이지당 요청 건수입니다. API 문서 기준 최대 9999입니다.",
    )
    parser.add_argument(
        "--output-dir",
        default="data/debug",
        help="CSV 백업 파일을 저장할 디렉터리입니다.",
    )
    parser.add_argument(
        "--max-pages",
        type=int,
        default=None,
        help="테스트용 최대 페이지 수입니다. 전체 수집 시에는 지정하지 않습니다.",
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=90,
        help="API 요청 타임아웃 초 단위입니다.",
    )
    args = parser.parse_args()
    if args.endpoint is None:
        args.endpoint = list(DEFAULT_ENDPOINTS)
    return args


def _resolve_zcodes(args: argparse.Namespace) -> list[str | None]:
    """사용자가 지정한 지역 옵션을 실제 API 요청 zcode 목록으로 변환합니다."""
    if args.all_regions:
        return list(REGION_CODES.values())
    if args.zcode:
        return args.zcode
    return [None]


if __name__ == "__main__":
    main()
