CREATE DATABASE IF NOT EXISTS `ev_charger_Dashboard`
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_0900_ai_ci;

USE `ev_charger_Dashboard`;

-- 삭제 쿼리
SET FOREIGN_KEY_CHECKS = 0;

-- 실시간 충전기 신규 스키마
DROP TABLE IF EXISTS charger_status_logs;
DROP TABLE IF EXISTS chargers;
DROP TABLE IF EXISTS charging_stations;
DROP TABLE IF EXISTS regions;
DROP TABLE IF EXISTS api_fetch_runs;

-- 기존 충전소·지도 스키마
DROP TABLE IF EXISTS tbl_charger_status_log;
DROP TABLE IF EXISTS tbl_station_congestion_stat;
DROP TABLE IF EXISTS map_station_region_cd;
DROP TABLE IF EXISTS tbl_charger;
DROP TABLE IF EXISTS tbl_charge_station;
DROP TABLE IF EXISTS tbl_region_cd;

-- API 캐시 스키마
DROP TABLE IF EXISTS charger_snapshots;
DROP TABLE IF EXISTS api_cache_runs;
DROP TABLE IF EXISTS tbl_api_charger_snapshot;

-- FAQ 스키마
DROP TABLE IF EXISTS ev_user_questions;

SET FOREIGN_KEY_CHECKS = 1;
