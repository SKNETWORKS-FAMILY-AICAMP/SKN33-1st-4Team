USE ev_charger_dashboard;

CREATE TABLE IF NOT EXISTS `tbl_region_cd` (
    `region_cd` int NOT NULL,
    `region_name` varchar(50) NOT NULL,
    `region_level` varchar(10) NOT NULL,
    `parent_cd` int NULL,
    CONSTRAINT `PK_TBL_REGION_CD` PRIMARY KEY (`region_cd`)
);

CREATE TABLE IF NOT EXISTS `tbl_region_elec_usage` (
    `record` int NOT NULL,
    `sido` varchar(10) NOT NULL,
    `sigungu` varchar(50) NOT NULL,
    `kw_50` int NULL DEFAULT 0,
    `kw_100` int NULL DEFAULT 0,
    `kw_100_dual` int NULL DEFAULT 0,
    `kw_200_dual` int NULL DEFAULT 0,
    `kw_300_dual` int NULL DEFAULT 0,
    `usage` int NULL DEFAULT 0,
    CONSTRAINT `PK_TBL_REGION_ELEC_USAGE` PRIMARY KEY (`record`)
);

CREATE TABLE IF NOT EXISTS `ev_user_questions` (
    `id` bigint NOT NULL,
    `source_name` varchar(100) NOT NULL,
    `category` varchar(100) NULL,
    `title` varchar(500) NOT NULL,
    `content` text NULL,
    `url` varchar(1000) NOT NULL,
    `published_at` varchar(50) NULL,
    `view_count` int NULL,
    `comment_count` int NULL,
    `collected_at` datetime NOT NULL DEFAULT current_timestamp,
    `search_keyword` varchar(100) NULL,
    CONSTRAINT `PK_EV_USER_QUESTIONS` PRIMARY KEY (`id`)
);

CREATE TABLE IF NOT EXISTS `tbl_charge_station` (
    `cs_id` int NOT NULL,
    `cs_name` varchar(50) NOT NULL,
    `cs_addr` varchar(255) NOT NULL,
    `cs_lat` decimal(9,6) NOT NULL,
    `cs_longi` decimal(9,6) NOT NULL,
    CONSTRAINT `PK_TBL_CHARGE_STATION` PRIMARY KEY (`cs_id`)
);

CREATE TABLE IF NOT EXISTS `tbl_region_coord` (
    `addr` varchar(200) NOT NULL,
    `lat` decimal(10,7) NOT NULL,
    `longi` decimal(10,7) NOT NULL,
    CONSTRAINT `PK_TBL_REGION_COORD` PRIMARY KEY (`addr`)
);

CREATE TABLE IF NOT EXISTS `tbl_charger` (
    `cp_id` int NOT NULL,
    `cp_name` varchar(10) NOT NULL,
    `cp_charge_type` int NOT NULL,
    `cp_stat` int NOT NULL DEFAULT 5,
    `cp_type` int NOT NULL,
    `cs_id` int NOT NULL,
    CONSTRAINT `PK_TBL_CHARGER` PRIMARY KEY (`cp_id`)
);

CREATE TABLE IF NOT EXISTS `tbl_station_congestion_stat` (
    `congestion_id` int NOT NULL,
    `cs_id` int NULL,
    `calculated_id` datetime NULL,
    `total_count` int NULL,
    `available_count` int NULL,
    `charging_count` int NULL,
    `unavailable_count` int NULL,
    `available_rate` decimal(5,2) NULL,
    `congestion_rate` decimal(5,2) NULL,
    `recommend_grade` varchar(20) NULL,
    `cs_id2` int NOT NULL,
    CONSTRAINT `PK_TBL_STATION_CONGESTION_STAT` PRIMARY KEY (`congestion_id`)
);

CREATE TABLE IF NOT EXISTS `map_station_region_cd` (
    `cs_id` int NOT NULL,
    `region_cd` int NOT NULL,
    CONSTRAINT `PK_MAP_STATION_REGION_CD` PRIMARY KEY (`cs_id`),
    CONSTRAINT `FK_tbl_charge_station_TO_map_station_region_cd_1`
        FOREIGN KEY (`cs_id`) REFERENCES `tbl_charge_station` (`cs_id`)
);

CREATE TABLE IF NOT EXISTS `tbl_charger_status_log` (
    `ststus_log_id` int NOT NULL,
    `cp_id` int NULL,
    `cp_stat` int NULL,
    `stat_upd_dt` datetime NULL,
    `collected_at` datetime NULL,
    `cp_id2` int NOT NULL,
    CONSTRAINT `PK_TBL_CHARGER_STATUS_LOG` PRIMARY KEY (`ststus_log_id`)
);
