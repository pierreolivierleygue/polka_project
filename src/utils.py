import sqlite3
import unicodedata

def normalize_name(name):
    nfkd_form = unicodedata.normalize('NFKD', name)
    only_ascii = nfkd_form.encode('ASCII', 'ignore').decode('ASCII')
    return only_ascii.lower()


def get_id_rider_by_name(rider_name, id_race):
    try:
        with sqlite3.connect("data/grand_tours.db") as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM rider WHERE LOWER(name) = LOWER(?) AND id_race = ?", (normalize_name(rider_name), id_race))
            result = cursor.fetchone()
            if result:
                return result[0]
            else:
                return None
    except Exception as e:
        print("Not able to retrieve the rider:", e)
        return None

