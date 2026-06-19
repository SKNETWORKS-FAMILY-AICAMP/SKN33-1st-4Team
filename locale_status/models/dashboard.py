from __future__ import annotations

from dataclasses import dataclass

import pandas as pd

from locale_status.config.settings import AVAILABLE_STATUS


# 이 파일은 대시보드 상단 metric 카드에 들어갈 요약 숫자를 계산합니다.
@dataclass(frozen=True)
class ChargerSummary:
    # 충전소/충전기 현황을 한 번에 전달하기 위한 읽기 전용 데이터 객체입니다.
    total_stations: int
    total_chargers: int
    available_chargers: int
    charging_chargers: int

    @property
    def availability_rate(self) -> float:
        if self.total_chargers == 0:
            return 0.0
        return self.available_chargers / self.total_chargers * 100

    @property
    def congestion_rate(self) -> float:
        if self.total_chargers == 0:
            return 0.0
        return self.charging_chargers / self.total_chargers * 100

    @property
    def congestion_label(self) -> str:
        if self.congestion_rate < 30:
            return "🟢 여유"
        if self.congestion_rate < 70:
            return "🟡 보통"
        return "🔴 혼잡"


def summarize_chargers(charger_df: pd.DataFrame) -> ChargerSummary:
    # 필터링된 DataFrame을 기준으로 총 충전소 수, 충전기 수, 사용 가능 수를 계산합니다.
    if charger_df.empty:
        return ChargerSummary(0, 0, 0, 0)

    total_stations = (
        charger_df["statId"].nunique()
        if "statId" in charger_df.columns
        else 0
    )
    available_chargers = (
        (charger_df["stat"].astype(str) == AVAILABLE_STATUS).sum()
        if "stat" in charger_df.columns
        else 0
    )
    charging_chargers = (
        (charger_df["stat"].astype(str) == "3").sum()
        if "stat" in charger_df.columns
        else 0
    )

    return ChargerSummary(
        total_stations=int(total_stations),
        total_chargers=len(charger_df),
        available_chargers=int(available_chargers),
        charging_chargers=int(charging_chargers),
    )
