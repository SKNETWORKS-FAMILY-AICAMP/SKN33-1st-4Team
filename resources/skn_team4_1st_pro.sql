USE `ev_charger_dashboard`;

CREATE TABLE IF NOT EXISTS `tbl_region_cd` (
	`region_cd`	int	NOT NULL	COMMENT '지역구별 코드',
	`region_name`	varchar(50)	NOT NULL	COMMENT '지역구이름',
	`region_level`	varchar(10)	NOT NULL	COMMENT '지역구 레벨(시/도:sido, 시군구:sigungu)',
	`parent_cd`	int	NULL	COMMENT '상위레벨 지역구 코드'
);

CREATE TABLE IF NOT EXISTS `tbl_region_elec_usage` (
	`record`	int	NOT NULL	COMMENT '레코드 번호',
	`sido`	varchar(10)	NOT NULL	COMMENT '광역지자체(시/도)',
	`sigungu`	varchar(50)	NOT NULL	COMMENT '시군구',
	`kw_50`	int	NULL	DEFAULT 0	COMMENT '50킬로와트',
	`kw_100`	int	NULL	DEFAULT 0	COMMENT '100킬로와트',
	`kw_100_dual`	int	NULL	DEFAULT 0	COMMENT '100킬로와트듀얼',
	`kw_200_dual`	int	NULL	DEFAULT 0	COMMENT '200킬로와트 듀얼',
	`kw_300_dual`	int	NULL	DEFAULT 0	COMMENT '300킬로와트 듀얼',
	`usage`	int	NULL	DEFAULT 0	COMMENT '사용량(kw/h)'
);

CREATE TABLE IF NOT EXISTS `ev_user_questions` (
	`id`	bigint	NOT NULL	COMMENT '질문 고유 id, AUTO_INCREMENT',
	`source_name`	varchar(100)	NOT NULL	COMMENT '수집 사이트',
	`category`	varchar(100)	NULL	COMMENT '게시판',
	`title`	varchar(500)	NOT NULL	COMMENT '게시글 제목',
	`content`	text	NULL	COMMENT '게시글 본문',
	`url`	varchar(1000)	NOT NULL	COMMENT '원본 url, UNIQUE',
	`published_at`	varchar(50)	NULL	COMMENT '작성일',
	`view_count`	int	NULL	COMMENT '조회수',
	`comment_count`	int	NULL	COMMENT '댓글 수',
	`collected_at`	datetime	NOT NULL	DEFAULT current_timestamp	COMMENT '수집일',
	`search_keyword`	varchar(100)	NULL	COMMENT '수집 시 사용한 검색어'
);

CREATE TABLE IF NOT EXISTS `tbl_charge_station` (
	`cs_id`	int	NOT NULL	COMMENT '충전소 고유 id',
	`cs_name`	varchar(50)	NOT NULL	COMMENT '충전소 명칭',
	`cs_addr`	varchar(255)	NOT NULL	COMMENT '충전소 주소',
	`cs_lat`	DECIMAL(9,6)	NOT NULL	COMMENT '충전소 위도',
	`cs_longi`	DECIMAL(9,6)	NOT NULL	COMMENT '충전소 경도'
);

CREATE TABLE IF NOT EXISTS `tbl_region_coord` (
	`addr`	varchar(200)	NOT NULL	COMMENT '지역구 주소',
	`lat`	DECIMAL(10,7)	NOT NULL	COMMENT '위도',
	`longi`	DECIMAL(10,7)	NOT NULL	COMMENT '경도'
);

CREATE TABLE IF NOT EXISTS `tbl_charger` (
	`cp_id`	int	NOT NULL	COMMENT '충전기 고유 id',
	`cp_name`	varchar(10)	NOT NULL	COMMENT '충전기 이름',
	`cp_charge_type`	int	NOT NULL	COMMENT '충전기 타입1:완속, 2:급속',
	`cp_stat`	int	NOT NULL	DEFAULT 5	COMMENT '충전상태코드1:충전가능 2:충전중 3:고장/점검 4:통신장애 5:통신미연결 6:충전종료 7:계획정지',
	`cp_type`	int	NOT NULL	COMMENT '충전방식1:B타입(5핀) 2:C타입(5핀) 3:BC타입(5핀) 4:BC타입(7핀) 5:C차 데모 6:AC3상 7:DC콤보 8:DC차데모+DC콤보',
	`cs_id`	int	NOT NULL	COMMENT '충전소 고유 id'
);

CREATE TABLE IF NOT EXISTS `tbl_station_congestion_stat` (
	`congestion_id`	int	NOT NULL	COMMENT '혼잡도 통계 고유 ID',
	`cs_id`	int	NULL	COMMENT '충전소 고유 ID',
	`calculated_id`	datetime	NULL	COMMENT '혼잡도 계산 시간',
	`total_count`	int	NULL	COMMENT '전체 충전기 수',
	`available_count`	int	NULL	COMMENT '사용 가능한 충전기 수',
	`charging_count`	int	NULL	COMMENT '충전 중인 충전기 수',
	`unavailable_count`	int	NULL	COMMENT '사용 불가  또는 상태 미확인 충전기 수',
	`available_rate`	decimal(5,2)	NULL	COMMENT '사용 가능 충전기 비율',
	`congestion_rate`	decimal(5,2)	NULL	COMMENT '충전소 혼잡도',
	`recommend_grade`	varchar(20)	NULL	COMMENT '이용 추천 등급',
	`cs_id2`	int	NOT NULL	COMMENT '충전소 고유 id'
);

CREATE TABLE IF NOT EXISTS `map_station_region_cd` (
	`cs_id`	int	NOT NULL	COMMENT '충전소 고유 id',
	`region_cd`	int	NOT NULL	COMMENT '지역구별 코드'
);

CREATE TABLE IF NOT EXISTS `tbl_charger_status_log` (
	`ststus_log_id`	int	NOT NULL	COMMENT '충전기 상태 이력 고유 ID',
	`cp_id`	int	NULL	COMMENT '충전기 고유 ID',
	`cp_stat`	int	NULL	COMMENT '충전기 상태 코드',
	`stat_upd_dt`	datetime	NULL	COMMENT '공공데이터 API 기준 상태 갱신 시간',
	`collected_at`	datetime	NULL	COMMENT '데이터를 수집한 시간',
	`cp_id2`	int	NOT NULL	COMMENT '충전기 고유 id'
);

DELIMITER //

DROP PROCEDURE IF EXISTS `add_constraints_if_missing`//
CREATE PROCEDURE `add_constraints_if_missing`()
BEGIN
	IF NOT EXISTS (
		SELECT 1 FROM information_schema.table_constraints
		WHERE table_schema = DATABASE()
		  AND table_name = 'tbl_region_cd'
		  AND constraint_type = 'PRIMARY KEY'
	) THEN
		ALTER TABLE `tbl_region_cd`
			ADD CONSTRAINT `PK_TBL_REGION_CD` PRIMARY KEY (`region_cd`);
	END IF;

	IF NOT EXISTS (
		SELECT 1 FROM information_schema.table_constraints
		WHERE table_schema = DATABASE()
		  AND table_name = 'tbl_region_elec_usage'
		  AND constraint_type = 'PRIMARY KEY'
	) THEN
		ALTER TABLE `tbl_region_elec_usage`
			ADD CONSTRAINT `PK_TBL_REGION_ELEC_USAGE` PRIMARY KEY (`record`);
	END IF;

	IF NOT EXISTS (
		SELECT 1 FROM information_schema.table_constraints
		WHERE table_schema = DATABASE()
		  AND table_name = 'ev_user_questions'
		  AND constraint_type = 'PRIMARY KEY'
	) THEN
		ALTER TABLE `ev_user_questions`
			ADD CONSTRAINT `PK_EV_USER_QUESTIONS` PRIMARY KEY (`id`);
	END IF;

	IF NOT EXISTS (
		SELECT 1 FROM information_schema.table_constraints
		WHERE table_schema = DATABASE()
		  AND table_name = 'tbl_charge_station'
		  AND constraint_type = 'PRIMARY KEY'
	) THEN
		ALTER TABLE `tbl_charge_station`
			ADD CONSTRAINT `PK_TBL_CHARGE_STATION` PRIMARY KEY (`cs_id`);
	END IF;

	IF NOT EXISTS (
		SELECT 1 FROM information_schema.table_constraints
		WHERE table_schema = DATABASE()
		  AND table_name = 'tbl_region_coord'
		  AND constraint_type = 'PRIMARY KEY'
	) THEN
		ALTER TABLE `tbl_region_coord`
			ADD CONSTRAINT `PK_TBL_REGION_COORD` PRIMARY KEY (`addr`);
	END IF;

	IF NOT EXISTS (
		SELECT 1 FROM information_schema.table_constraints
		WHERE table_schema = DATABASE()
		  AND table_name = 'tbl_charger'
		  AND constraint_type = 'PRIMARY KEY'
	) THEN
		ALTER TABLE `tbl_charger`
			ADD CONSTRAINT `PK_TBL_CHARGER` PRIMARY KEY (`cp_id`);
	END IF;

	IF NOT EXISTS (
		SELECT 1 FROM information_schema.table_constraints
		WHERE table_schema = DATABASE()
		  AND table_name = 'tbl_station_congestion_stat'
		  AND constraint_type = 'PRIMARY KEY'
	) THEN
		ALTER TABLE `tbl_station_congestion_stat`
			ADD CONSTRAINT `PK_TBL_STATION_CONGESTION_STAT` PRIMARY KEY (`congestion_id`);
	END IF;

	IF NOT EXISTS (
		SELECT 1 FROM information_schema.table_constraints
		WHERE table_schema = DATABASE()
		  AND table_name = 'map_station_region_cd'
		  AND constraint_type = 'PRIMARY KEY'
	) THEN
		ALTER TABLE `map_station_region_cd`
			ADD CONSTRAINT `PK_MAP_STATION_REGION_CD` PRIMARY KEY (`cs_id`);
	END IF;

	IF NOT EXISTS (
		SELECT 1 FROM information_schema.table_constraints
		WHERE table_schema = DATABASE()
		  AND table_name = 'tbl_charger_status_log'
		  AND constraint_type = 'PRIMARY KEY'
	) THEN
		ALTER TABLE `tbl_charger_status_log`
			ADD CONSTRAINT `PK_TBL_CHARGER_STATUS_LOG` PRIMARY KEY (`ststus_log_id`);
	END IF;

	IF NOT EXISTS (
		SELECT 1 FROM information_schema.key_column_usage
		WHERE table_schema = DATABASE()
		  AND table_name = 'map_station_region_cd'
		  AND column_name = 'cs_id'
		  AND referenced_table_name = 'tbl_charge_station'
		  AND referenced_column_name = 'cs_id'
	) THEN
		ALTER TABLE `map_station_region_cd`
			ADD CONSTRAINT `FK_tbl_charge_station_TO_map_station_region_cd_1`
			FOREIGN KEY (`cs_id`) REFERENCES `tbl_charge_station` (`cs_id`);
	END IF;
END//

CALL `add_constraints_if_missing`()//
DROP PROCEDURE `add_constraints_if_missing`//

DELIMITER ;
