CREATE DATABASE IF NOT EXISTS `ev_charger_dashboard`
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_0900_ai_ci;

-- 이 파일은 root 등 CREATE USER/GRANT 권한이 있는 관리자 계정으로 실행한다.
DROP USER IF EXISTS 'skn_team4'@'localhost';
DROP USER IF EXISTS 'skn_team4'@'%';
DROP USER IF EXISTS 'skn_4team'@'localhost';
DROP USER IF EXISTS 'skn_4team'@'%';

CREATE USER 'skn_team4'@'localhost' IDENTIFIED BY 'skn4team';
CREATE USER 'skn_team4'@'%' IDENTIFIED BY 'skn4team';

GRANT ALL PRIVILEGES ON `ev_charger_dashboard`.* TO 'skn_team4'@'localhost';
GRANT ALL PRIVILEGES ON `ev_charger_dashboard`.* TO 'skn_team4'@'%';

FLUSH PRIVILEGES;

SHOW GRANTS FOR 'skn_team4'@'localhost';
SHOW GRANTS FOR 'skn_team4'@'%';
