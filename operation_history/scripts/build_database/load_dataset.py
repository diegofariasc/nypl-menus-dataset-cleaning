import json
import shutil
import csv23
import mysql.connector
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent
BUILD_DB_PATH = BASE_DIR / 'operation_history' / 'scripts' / 'build_database'
CONFIG_PATH = BUILD_DB_PATH / 'db_config.json'
SQL_SCHEMA_PATH = BUILD_DB_PATH / 'regenerate_database.sql'
CSV_FILES = ['Menu.csv', 'Dish.csv', 'MenuPage.csv', 'MenuItem.csv']

# Reviewers: modify this line and make it point to your dataset path
CSV_SOURCE_DIR = BASE_DIR / 'datasets' / 'dirty_dataset' 

def load_db_config(config_path: Path) -> dict:
    with open(config_path, 'r') as f:
        return json.load(f)

def get_secure_file_priv(conn) -> str | None:
    with conn.cursor() as cursor:
        cursor.execute("SHOW VARIABLES LIKE 'secure_file_priv'")
        result = cursor.fetchone()
        return result[1] if result else None

def get_table_columns(conn, table_name: str) -> list[str]:
    with conn.cursor() as cursor:
        cursor.execute(f"""
            SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS
            WHERE TABLE_SCHEMA = 'NYPLMenu' AND TABLE_NAME = %s
            ORDER BY ORDINAL_POSITION
        """, (table_name,))
        columns = [row[0] for row in cursor.fetchall()]
    return columns

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
        return sum(1 for _ in csv23.reader(f)) - 1

def get_table_row_count(conn, table_name: str) -> int:
    with conn.cursor() as cursor:
        cursor.execute(f"""
            SELECT table_rows FROM information_schema.tables
            WHERE table_schema = 'NYPLMenu' AND table_name = %s
        """, (table_name,))
        result = cursor.fetchone()
        return result[0] if result else -1

def is_number(value):
    try:
        float(value)
        return True
    except ValueError:
        return False

def escape_backticks_and_backslashes(text):
    text = text.replace('\\', '\\\\').replace('`', '\\`')
    return text

def preprocess_csv_for_db(input_path: Path, output_path: Path):
    with open(input_path, 'r', encoding='utf-8', newline='') as infile:
        reader = csv23.reader(infile)
        with open(output_path, 'w', encoding='utf-8', newline='') as outfile:
            writer = csv23.writer(outfile, quoting=csv23.QUOTE_NONE, escapechar='\\', delimiter=',')

            for row in reader:
                new_row = []
                for field in row:
                    sanitized = escape_backticks_and_backslashes(field)
                    sanitized = sanitized if is_number(sanitized) else f"`{sanitized}`"
                    sanitized = "" if sanitized == "``" else sanitized
                    new_row.append(sanitized)
                writer.writerow(new_row)

def load_data_into_tables(conn, target_dir: Path):
    for file_name in CSV_FILES:
        original_csv = target_dir / file_name
        if not original_csv.exists():
            print(f"[ERROR] File not found: {original_csv.name}")
            continue

        preprocessed_csv = target_dir / f"preprocessed_{file_name}"
        preprocess_csv_for_db(original_csv, preprocessed_csv)

        table_name = original_csv.stem
        full_path = str(preprocessed_csv.resolve()).replace("\\", "/")
        expected_rows = count_rows_in_csv(preprocessed_csv)

        columns = get_table_columns(conn, table_name)
        if not columns:
            print(f"[ERROR] No columns found for table {table_name}")
            continue

        user_vars = ', '.join(f"@col{i+1}" for i in range(len(columns)))
        set_statements = ',\n  '.join(f"{col} = NULLIF(@col{i+1}, '')" for i, col in enumerate(columns))

        query = f"""
            LOAD DATA INFILE '{full_path}' IGNORE
            INTO TABLE {table_name}
            FIELDS TERMINATED BY ',' ENCLOSED BY '"' ESCAPED BY '"'
            LINES TERMINATED BY '\\n' IGNORE 1 LINES
            ({user_vars})
            SET
              {set_statements}
        """

        try:
            print(f"\nLoading: {preprocessed_csv.name} -> {table_name}...")
            with conn.cursor() as cursor:
                cursor.execute(query)
            conn.commit()

            actual_rows = get_table_row_count(conn, table_name)
            difference = expected_rows - actual_rows

            print(f"[OK] Loaded: {preprocessed_csv.name} -> {table_name}")
            print(f"- Rows in file:     {expected_rows}")
            print(f"- Rows inserted:    {actual_rows}")
            print(f"- Rows skipped:     {difference} ({(100 / expected_rows * actual_rows):.2f}%)")

        except mysql.connector.Error as err:
            print(f"[ERROR] Loading {preprocessed_csv.name} into {table_name}: {err}")

        try:
            preprocessed_csv.unlink()
        except Exception as e:
            print(f"[WARNING] Could not delete {preprocessed_csv}: {e}")

def cleanup_temp_files(files: list[Path]):
    for file in files:
        try:
            file.unlink()
        except Exception as e:
            print(f"[WARNING] Could not delete {file}: {e}")

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
