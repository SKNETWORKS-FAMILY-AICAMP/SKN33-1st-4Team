# SQL Setup Files

Run from the project root with the MySQL CLI:

```powershell
mysql --default-character-set=utf8mb4 -u root -p -e "SOURCE docs/create_table.sql"
```

File roles:

- `00_create_database.sql`: creates and selects `ev_charger_dashboard` if needed.
- `01_create_user.sql`: optional admin-only user/grant script. Run this separately with a privileged account if the project user does not exist.
- `02_create_schema.sql`: creates the final `skn_team4_1st_pro.sql` table structure without dropping existing tables.
- `02_align_existing_schema.sql`: fixes known old constraints on existing databases without dropping tables/data.
- `03_seed_initial_data.sql`: loads initial region, usage, coordinate, station, charger, and station-region mapping data.
- `04_cleanup_encoding_artifacts.sql`: removes old mojibake coordinate rows after UTF-8 seed upserts.

The `resources/elec_vehicle_*.sql` files are data-only seed files. Do not put ERD table DDL there; canonical schema belongs in `skn_team4_1st_pro.sql`.
Korean-text seed inserts update existing rows so repeated runs can repair mojibake created by a wrong MySQL client character set.
