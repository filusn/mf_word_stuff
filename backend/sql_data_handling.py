from pathlib import Path
import sqlite3

def create_sqlite_db(path_to_db: Path) -> None:
    if Path(path_to_db).exists():
        return
    else:
        conn = sqlite3.connect(path_to_db)
        print(sqlite3.sqlite_version)
        cur = conn.cursor()
        cur.execute(
            "CREATE TABLE IF NOT EXISTS urls_table (id INTEGER PRIMARY KEY AUTOINCREMENT, url TEXT NOT NULL)")
        conn.close()

def insert_urls_into_sqllite_db(path_to_txt_file: Path, path_to_db: Path) -> None:
    with open(path_to_txt_file,'r') as file:
        data_table = file.readlines()
        data = (x.strip("\n") for x in data_table)

    conn = sqlite3.connect(path_to_db)
    cur = conn.cursor()
    for url in data:
        cur.execute("INSERT INTO urls_table (url) VALUES (?)", (url,))
    conn.commit()
    conn.close()

if __name__ == "__main__":
    create_sqlite_db(Path(__file__).parent.joinpath("urls_db"))
