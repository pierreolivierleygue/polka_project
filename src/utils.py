import sqlite3

@staticmethod
def get_id_rider_by_name(rider_name, id_race):
    conn = sqlite3.connect("grand_tours.db")
    cursor = conn.cursor()

    cursor.execute("SELECT id FROM rider WHERE name = ? AND id_race = ?", (rider_name, id_race))
    result = cursor.fetchone()

    conn.close()

    if result:
        return result[0]
    else:
        return None