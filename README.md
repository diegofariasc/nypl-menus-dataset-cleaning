# NYPL Menus dataset cleaning
## Data loader
This script automates loading the NYPL dataset into a MySQL database using `LOAD DATA INFILE`.

### Requirements
- Python 3
- MySQL Server running
- NYPL dataset in CSV format
- mysql-connector-python

### Instructions for execution
2. Create `db_config.json` in the project root with your MySQL credentials:
```json
{
  "user": "your_mysql_username",
  "password": "your_mysql_password",
  "host": "localhost"
}
```

3. Copy the dataset (`NYPL-menus` folder) to the project root directory.

4. Verify MySQL’s `secure_file_priv` variable is set and that `LOAD DATA INFILE` is enabled:
```sql
SHOW VARIABLES LIKE 'secure_file_priv';
```

5. Run the loader script `setupDatabase.py`

### Notes

- The script copies CSVs to MySQL’s secure file directory before loading.  
- Schema is created from `regenerate-database.sql`.  
- Data loading uses `LOAD DATA INFILE` with error warnings.  
- Temporary CSV copies are cleaned up automatically.  
- Make sure MySQL has permission for file operations.
