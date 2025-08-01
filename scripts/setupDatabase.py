import json 
import shutil
import csv
import mysql.connector
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
CONFIG_PATH = BASE_DIR / 'db_config.json'
SQL_SCHEMA_PATH = BASE_DIR / 'regenerate-database.sql'
CSV_SOURCE_DIR = (BASE_DIR / '..' / 'NYPL-menus').resolve()
CSV_FILES = [ 'Menu.csv', 'Dish.csv', 'MenuPage.csv', 'MenuItem.csv' ]

# --- Helper Functions ---
def load_db_config(config_path: Path) -> dict:
    with open(config_path, 'r') as f:
        return json.load(f)

def get_secure_file_priv(conn) -> str | None:
    with conn.cursor() as cursor:
        cursor.execute("SHOW VARIABLES LIKE 'secure_file_priv'")
        result = cursor.fetchone()
        return result[1] if result else None

def run_sql_file(conn, sql_file_path: Path):
    with open(sql_file_path, 'r', encoding='utf-8') as f:
        commands = f.read()

    with conn.cursor() as cursor:
        for command in commands.split(';'):
            cmd = command.strip()
            if cmd:
                try:
                    cursor.execute(cmd)
                except mysql.connector.Error as err:
                    print(f"[ERROR] Failed executing:\n{cmd}\n→ {err}")
    conn.commit()

def copy_csvs(source_dir: Path, target_dir: Path) -> list[Path]:
    copied_files = []
    for file in source_dir.glob("*.csv"):
        dst = target_dir / file.name
        shutil.copy(file, dst)
        copied_files.append(dst)
    return copied_files

def count_rows_in_csv(file_path: Path) -> int:
    with open(file_path, newline='', encoding='utf-8') as f:
        return sum(1 for _ in csv.reader(f)) - 1  # Subtract header

def get_table_row_count(conn, table_name: str) -> int:
    with conn.cursor() as cursor:
        cursor.execute(f"""
            SELECT table_rows FROM information_schema.tables
            WHERE table_schema = 'NYPLMenu' AND table_name = %s
        """, (table_name,))
        result = cursor.fetchone()
        return result[0] if result else -1

def load_data_into_tables(conn, target_dir: Path):
    with conn.cursor() as cursor:
        for file_name in CSV_FILES:
            csv_file = target_dir / file_name
            if not csv_file.exists():
                print(f"[ERROR] File not found: {csv_file.name}")
                continue

            table_name = csv_file.stem
            full_path = str(csv_file.resolve()).replace("\\", "/")
            expected_rows = count_rows_in_csv(csv_file)

            query = f"""
                LOAD DATA INFILE '{full_path}' IGNORE
                INTO TABLE {table_name}
                FIELDS TERMINATED BY ','
                ENCLOSED BY '"'
                LINES TERMINATED BY '\\n'
            """
            try:
                print(f"\nLoading: {csv_file.name} -> {table_name}...")
                cursor.execute(query)
                conn.commit()

                actual_rows = get_table_row_count(conn, table_name)
                difference = expected_rows - actual_rows

                print(f"[OK] Loaded: {csv_file.name} -> {table_name}")
                print(f"- Rows expected: {expected_rows}")
                print(f"- Rows loaded:   {actual_rows}")
                print(f"- Rows missing:  {difference} ({(100 / actual_rows * difference):.2f}%)")
            except mysql.connector.Error as err:
                print(f"[ERROR] Loading {csv_file.name} into {table_name}: {err}")

def cleanup_temp_files(files: list[Path]):
    for file in files:
        try:
            file.unlink()
        except Exception as e:
            print(f"[WARNING] Could not delete {file}: {e}")

# --- Main Execution ---
def main():
    config = load_db_config(CONFIG_PATH)
    conn = None
    try:
        conn = mysql.connector.connect(
            user=config["user"],
            password=config["password"],
            host=config.get("host", "localhost"),
            allow_local_infile=True
        )
    except mysql.connector.Error as err:
        print(f"Connection failed: {err}")
        return

    try:
        secure_dir = get_secure_file_priv(conn)
        if not secure_dir:
            print("secure_file_priv is not set in MySQL. Aborting. "
                  "Please configure it to allow local file loading.")
            return

        print(f"Copying CSVs from: {CSV_SOURCE_DIR} to {secure_dir}...")
        copied_files = copy_csvs(CSV_SOURCE_DIR, Path(secure_dir))

        print("Running database schema creation...")
        run_sql_file(conn, SQL_SCHEMA_PATH)

        print("Loading CSV data into tables...")
        load_data_into_tables(conn, Path(secure_dir))

        print("Cleaning up temporary CSV files...")
        cleanup_temp_files(copied_files)

        print("Database setup and data loading complete.")

    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    main()
