-- Local database initialize/update entrypoint.
-- Run from the project root:
-- mysql -u <project-or-admin-user> -p < docs/create_table.sql
--
-- User creation is intentionally separate because it requires admin privileges:
-- mysql -u root -p < resources/sql/01_create_user.sql

SOURCE resources/sql/00_create_database.sql
SOURCE resources/sql/02_create_schema.sql
SOURCE resources/sql/02_align_existing_schema.sql
SOURCE resources/sql/03_seed_initial_data.sql
SOURCE resources/sql/04_cleanup_encoding_artifacts.sql
