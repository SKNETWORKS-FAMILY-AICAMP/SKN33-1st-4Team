import db.charge_station as station
from config.settings import DatabaseSettings
import pandas as pd


def get_region_elec_usage_df():
    usage_rows = station.find_region_elec_usage(DatabaseSettings)
    return pd.DataFrame(
        usage_rows,
        columns=[
            "record",
            "sido",
            "sigungu",
            "kw_50",
            "kw_100",
            "kw_100_dual",
            "kw_200_dual",
            "kw_300_dual",
            "usage",
        ],
    )


def get_station_coord_to_df() :
    stations = station.find_station_map(DatabaseSettings)[0]
    df = pd.DataFrame(stations, columns=["id", "충전소 이름", "lat", "lon"])

    df["lat"] = df["lat"].astype(float)
    df["lon"] = df["lon"].astype(float)
    # print('충전소 리스트 가져오기 완료')
    return df

def get_station_details(keyword) :
    station_details = station.find_station_details(DatabaseSettings, keyword)
    df = pd.DataFrame(station_details, columns=["id", "충전소 이름", "주소", "완속", '급속'])
    # print('충전소 상세 정보 가져오기 완료')

    return df

def get_station_by_region_summary_df() :
    stations = station.find_station_by_region_summary(DatabaseSettings)
    df = pd.DataFrame(stations, columns=["시도 코드", "시군구 코드", "시/도", "시/군/구", "충전소 수"])

    return df

def get_sido():
    sido_list = station.find_region_sido(DatabaseSettings)
    df = pd.DataFrame(sido_list)

    return df

def get_sigungu(sido_cd):
    sigungu_list = station.find_region_sigungu(DatabaseSettings,sido_cd)
    df = pd.DataFrame(sigungu_list)

    return df

def get_station_by_region(region_cd):
    station_by_region = station.find_station_by_region(DatabaseSettings,region_cd)
    df = pd.DataFrame(station_by_region,
                      columns=["지역 코드", "지역명", "충전소 id", "충전소 이름", 'lat', 'lon'])
    df["lat"] = df["lat"].astype(float)
    df["lon"] = df["lon"].astype(float)

    return df

