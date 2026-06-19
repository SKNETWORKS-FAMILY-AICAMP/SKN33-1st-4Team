USE ev_charger_dashboard;

DELETE FROM tbl_region_coord
WHERE addr LIKE '%?%'
   OR addr NOT LIKE '%대한민국';

