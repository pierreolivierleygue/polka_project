import sqlite3
import unicodedata

def normalize_name(name):
    nfkd_form = unicodedata.normalize('NFKD', name)
    only_ascii = nfkd_form.encode('ASCII', 'ignore').decode('ASCII')
    return only_ascii.lower()


def get_id_rider_by_name(rider_name, id_race, cursor):
    cursor.execute("SELECT id FROM rider WHERE LOWER(name) = LOWER(?) AND id_race = ?", (normalize_name(rider_name), id_race))
    result = cursor.fetchone()
    if result:
        return result[0]
    else:
        return None
    
def clear_database():
    with sqlite3.connect("data/grand_tours.db") as conn:
        cursor = conn.cursor()
        tables = ["race", "rider", "stage", "stage_result", "climb", "climb_result"]
        for table in tables:
            cursor.execute(f"DELETE FROM {table}")
        print("Database cleared.")

