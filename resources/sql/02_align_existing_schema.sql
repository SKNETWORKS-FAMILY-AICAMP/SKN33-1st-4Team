USE ev_charger_dashboard;

DELIMITER //

DROP PROCEDURE IF EXISTS align_ev_charger_dashboard_schema//
CREATE PROCEDURE align_ev_charger_dashboard_schema()
BEGIN
    IF EXISTS (
        SELECT 1
        FROM information_schema.key_column_usage
        WHERE table_schema = DATABASE()
          AND table_name = 'map_station_region_cd'
          AND constraint_name = 'FK_tbl_region_cd_TO_map_station_region_cd_1'
          AND referenced_table_name = 'tbl_region_cd'
    ) THEN
        ALTER TABLE map_station_region_cd
            DROP FOREIGN KEY FK_tbl_region_cd_TO_map_station_region_cd_1;
    END IF;

    IF NOT EXISTS (
        SELECT 1
        FROM information_schema.key_column_usage
        WHERE table_schema = DATABASE()
          AND table_name = 'map_station_region_cd'
          AND constraint_name = 'FK_tbl_charge_station_TO_map_station_region_cd_1'
          AND column_name = 'cs_id'
          AND referenced_table_name = 'tbl_charge_station'
          AND referenced_column_name = 'cs_id'
    ) THEN
        ALTER TABLE map_station_region_cd
            ADD CONSTRAINT FK_tbl_charge_station_TO_map_station_region_cd_1
            FOREIGN KEY (cs_id) REFERENCES tbl_charge_station (cs_id);
    END IF;
END//

CALL align_ev_charger_dashboard_schema()//
DROP PROCEDURE align_ev_charger_dashboard_schema//

DELIMITER ;
