# NYPL Menus dataset cleaning
## Data loader
This script automates the loading process of the NYPL dataset into a MySQL database using `LOAD DATA INFILE`.

### Requirements
- Python 3
- MySQL server running
- NYPL dataset in CSV format
- mysql-connector-python

### Instructions for execution
1. Create a `db_config.json` file in the `build_database` folder (this folder) with your MySQL credentials. It must look like this:
```json
{
  "user": "your_mysql_username",
  "password": "your_mysql_password",
  "host": "localhost"
}
```

3. Follow our `box_link.txt` links and download the dataset you want to load

4. In the code, change this constant `CSV_SOURCE_DIR` and make it point to the dataset folder path you want to load

5. Verify MySQL’s `secure_file_priv` variable is set and that `LOAD DATA INFILE` is enabled:
```sql
SHOW VARIABLES LIKE 'secure_file_priv';
```

6. Run the loader script `python load_dataset.py`

### What happens next?
- The script copies CSVs to MySQL’s secure file directory before loading.
- Schema is created from `regenerate-database.sql`.  
- Data loading uses `LOAD DATA INFILE` to load the contents.
- Temporary CSV copies are cleaned up automatically.  
- Before these steps you can run our queries on the database
