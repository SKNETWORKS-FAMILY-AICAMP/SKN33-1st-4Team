CREATE TABLE IF NOT EXISTS regions (
    zcode VARCHAR(2) NOT NULL COMMENT 'API province/city code',
    region_name VARCHAR(50) NOT NULL COMMENT 'Province/city name',
    PRIMARY KEY (zcode)
) COMMENT='Region lookup table for API zcode filters';

CREATE TABLE IF NOT EXISTS charging_stations (
    stat_id VARCHAR(20) NOT NULL COMMENT 'API statId: charging station ID',
    stat_nm VARCHAR(200) NOT NULL COMMENT 'API statNm: station name',
    addr VARCHAR(500) NULL COMMENT 'API addr',
    addr_detail VARCHAR(500) NULL COMMENT 'API addrDetail',
    location VARCHAR(255) NULL COMMENT 'API location',
    lat DECIMAL(10, 7) NULL COMMENT 'API lat',
    lng DECIMAL(10, 7) NULL COMMENT 'API lng',
    use_time VARCHAR(255) NULL COMMENT 'API useTime',
    busi_id VARCHAR(20) NULL COMMENT 'API busiId',
    busi_nm VARCHAR(100) NULL COMMENT 'API busiNm',
    busi_call VARCHAR(50) NULL COMMENT 'API busiCall',
    zcode VARCHAR(2) NULL COMMENT 'API zcode',
    zscode VARCHAR(10) NULL COMMENT 'API zscode',
    kind VARCHAR(10) NULL COMMENT 'API kind',
    kind_detail VARCHAR(10) NULL COMMENT 'API kindDetail',
    parking_free VARCHAR(10) NULL COMMENT 'API parkingFree',
    note TEXT NULL COMMENT 'API note',
    limit_yn VARCHAR(10) NULL COMMENT 'API limitYn',
    limit_detail TEXT NULL COMMENT 'API limitDetail',
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (stat_id),
    INDEX idx_charging_stations_zcode (zcode),
    INDEX idx_charging_stations_stat_nm (stat_nm),
    CONSTRAINT fk_charging_stations_region
        FOREIGN KEY (zcode) REFERENCES regions (zcode)
) COMMENT='Static charging station metadata from getChargerInfo';

CREATE TABLE IF NOT EXISTS chargers (
    stat_id VARCHAR(20) NOT NULL COMMENT 'API statId',
    chger_id VARCHAR(10) NOT NULL COMMENT 'API chgerId',
    chger_type VARCHAR(10) NULL COMMENT 'API chgerType',
    output DECIMAL(8, 2) NULL COMMENT 'API output',
    method VARCHAR(100) NULL COMMENT 'API method',
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (stat_id, chger_id),
    INDEX idx_chargers_type (chger_type),
    INDEX idx_chargers_output (output),
    CONSTRAINT fk_chargers_station
        FOREIGN KEY (stat_id) REFERENCES charging_stations (stat_id)
) COMMENT='Physical charger metadata from getChargerInfo';

CREATE TABLE IF NOT EXISTS charger_status_logs (
    id BIGINT NOT NULL AUTO_INCREMENT,
    stat_id VARCHAR(20) NOT NULL COMMENT 'API statId',
    chger_id VARCHAR(10) NOT NULL COMMENT 'API chgerId',
    busi_id VARCHAR(20) NULL COMMENT 'API busiId',
    stat VARCHAR(10) NOT NULL COMMENT 'API stat: raw charger status code',
    stat_upd_dt CHAR(14) NULL COMMENT 'API statUpdDt, format yyyyMMddHHmmss',
    last_tsdt CHAR(14) NULL COMMENT 'Optional API lastTsdt',
    last_tedt CHAR(14) NULL COMMENT 'Optional API lastTedt',
    now_tsdt CHAR(14) NULL COMMENT 'Optional API nowTsdt',
    fetched_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    INDEX idx_status_logs_charger_time (stat_id, chger_id, fetched_at),
    INDEX idx_status_logs_stat (stat),
    INDEX idx_status_logs_stat_upd_dt (stat_upd_dt),
    CONSTRAINT fk_status_logs_charger
        FOREIGN KEY (stat_id, chger_id) REFERENCES chargers (stat_id, chger_id)
) COMMENT='Real-time charger status snapshots from getChargerStatus';

CREATE TABLE IF NOT EXISTS api_fetch_runs (
    id BIGINT NOT NULL AUTO_INCREMENT,
    endpoint VARCHAR(50) NOT NULL,
    zcode VARCHAR(2) NULL,
    page_count INT NOT NULL DEFAULT 0,
    row_count INT NOT NULL DEFAULT 0,
    fetched_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    INDEX idx_api_fetch_runs_endpoint_time (endpoint, fetched_at)
) COMMENT='Optional audit table for API collection runs';
