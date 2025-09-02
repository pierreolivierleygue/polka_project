from procyclingstats import Race, RaceStartlist, Stage, RaceClimbs
import sqlite3

from utils import get_id_rider_by_name, normalize_name


def year_scraper(first_year, last_year):
    """ 
    Function made in order to run all the data needed
    2 parameters : first_year and last_year
    No return, just run other functions in order to feed the db.
    """
    for year in range(first_year, last_year + 1):
        RacesScraper.races_scraper(year)

class RacesScraper:
    @staticmethod
    def races_scraper(year):
        """
        Function that, for every year given, collect all the datas for the 3 grand tours
        The function start other functions about stage, rider and climb but feed the db with : 
        name, year, gc_winner, kom_winner in the race table
        name, id_race in the rider table (from the startlist)

        1 parameter: the year

        """
        gt_list = ['giro-d-italia','tour-de-france','vuelta-a-espana']
        for gt_name in gt_list:
            id_race = RacesScraper.insert_race(gt_name, year)

            ## Data Scrapping Part
            
            # populate the rider table
            url_race= f"race/{gt_name}/{year}"
            url_race_startlist = f"race/{gt_name}/{year}/startlist"
            startlist = RaceStartlist(url_race_startlist)
            riders = startlist.startlist()
            for rider in riders:
                rider_name = rider['rider_name']
                RacesScraper.insert_rider(rider_name, id_race)

            # populate the race table
            race= Stage(f"race/{gt_name}/{year}/stage-21")
            gc_list = race.gc()
            kom_list = race.kom()
            if gc_list and kom_list:
                name_gc_winner = race.gc()[0]['rider_name'] 
                name_kom_winner = race.kom()[0]['rider_name'] 

                gc_winner = get_id_rider_by_name(name_gc_winner, id_race)
                kom_winner = get_id_rider_by_name(name_kom_winner, id_race)

                RacesScraper.insert_race_winners(id_race, gc_winner, kom_winner)
        
            StagesScraper.stages_scraper(id_race, url_race, gt_name,year)

    @staticmethod
    def insert_race(name, year):
        """
        Insert a race into the DB and return its id.
        """
        with sqlite3.connect("data/grand_tours.db") as conn:
            cursor = conn.cursor()
            try:
                cursor.execute(
                    "INSERT INTO race (name, year) VALUES (?, ?)",
                    (name, year)
                )
                print("Inserted race:", name, "year:", year)
            except  Exception as e:
                print(" DB Error inserting race:", e)
            return cursor.lastrowid
        
    
    @staticmethod    
    def insert_rider(rider_name, id_race):
        """
        Insert a rider into the DB and return its id.
        """
        with sqlite3.connect("data/grand_tours.db") as conn:
            cursor = conn.cursor()
            try: 
                cursor.execute(
                    "INSERT INTO rider (name, id_race) VALUES (?, ?)",
                    (normalize_name(rider_name), id_race)
                )
                print("Inserted rider:", normalize_name(rider_name), "id_race:", id_race)
            except  Exception as e:
                print(" DB Error inserting rider:", e)
            return cursor.lastrowid

    @staticmethod
    def insert_race_winners(id_race, gc_winner, kom_winner):
        """
        Insert a race into the DB and return its id.
        """
        with sqlite3.connect("data/grand_tours.db") as conn:
            cursor = conn.cursor()
            try:
                cursor.execute(
                    f"UPDATE race SET gc_winner = ?, kom_winner = ? WHERE id = ?",
                    (gc_winner, kom_winner, id_race)
                )
                print("Updated race data: winner", gc_winner, "kom_winner:", kom_winner, "id_race:", id_race)
            except  Exception as e:
                print(" DB Error inserting race winners:", e)

class StagesScraper:
    @staticmethod
    def stages_scraper(id_race, url_race, gt_name, year):
        """
        """
        race_obj = Race(url_race)
        url_list_stages = race_obj.stages('stage_url')
        for i, url_stage in enumerate(url_list_stages, start=1):
            stage = Stage(url_stage['stage_url']).parse()
            type = stage['stage_type']
            distance = stage['distance']
            elevation = stage['vertical_meters']
            profile = stage['profile_icon']
            winner = get_id_rider_by_name(stage['results'][0]['rider_name'], id_race)
            stage_number = i
            id_stage = StagesScraper.insert_stage(id_race, stage_number, type, profile, distance, elevation, winner)
            
            
            list_gc = stage['gc']
            list_kom = stage['kom']

            for rider in list_gc:
                rider_name = rider['rider_name']
                gc_rank = rider['rank']

                kom_info = next((r for r in list_kom if r['rider_name'] == rider_name), None)
                if kom_info:
                    kom_rank = kom_info['rank']
                    kom_points = kom_info['points']
                else:
                    kom_rank = None
                    kom_points = 0

                id_rider = get_id_rider_by_name(rider_name, id_race)
                StagesScraper.insert_stage_result(id_rider, id_stage, gc_rank, kom_rank, kom_points)
            
            ClimbsScraper.climbs_scraper(id_stage, url_stage, year, gt_name, id_race)

        
    @staticmethod
    def insert_stage(id_race, stage_number, type, profile, distance_km, elevation_m, winner):
        """
        Insert a stage into the DB and return its id.
        """
        with sqlite3.connect("data/grand_tours.db") as conn:
            cursor = conn.cursor()
            try:
                cursor.execute(
                    "INSERT INTO stage (id_race, stage_number, type, profile, distance_km, elevation_m, winner) VALUES (?, ?, ?, ?, ?, ?, ?)",
                    (id_race, stage_number, type, profile, distance_km, elevation_m, winner)
                )
                print("Insert stage:",id_race, stage_number, type, profile, distance_km, elevation_m, winner )
            except  Exception as e:
                print(" DB Error inserting stage:", e)
            return cursor.lastrowid
    
    @staticmethod   
    def insert_stage_result(id_rider, id_stage, gc_position, kom_position, kom_points):
        """
        Insert a stage_result into the DB. 
        """
        with sqlite3.connect("data/grand_tours.db") as conn:
            cursor = conn.cursor()
            try:
                cursor.execute(
                    "INSERT INTO stage_result (id_rider, id_stage, gc_position, kom_position, kom_points) VALUES (?, ?, ?, ?, ?)",
                    (id_rider, id_stage, gc_position, kom_position, kom_points)
                )
                print("Insert stage result:", id_rider, id_stage, gc_position, kom_position, kom_points)
            except  Exception as e:
                print(" DB Error inserting stage result:", e)

class ClimbsScraper:
    @staticmethod
    def climbs_scraper(id_stage, url_stage, year, gt_name, id_race):
        """
        """
        stage_climbs  = Stage(url_stage['stage_url']).climbs()
        race_climbs = RaceClimbs(f"race/{gt_name}/{year}/route/climbs").climbs()
        
        for climb in stage_climbs:
            climb_name = climb['climb_name']
            climb_category = climb['category']
            climb_rank = climb['rank']
            climb_info = next((r for r in race_climbs if r['climb_name'] == climb_name), None)

            if climb_info:
                distance_km = climb_info['length']
                percentage = climb_info['steepness']
                distance_remaining_km = climb_info['km_before_finnish']
                elevation_m = (distance_km * 1000) * (percentage/100)
            else:
                distance_km = 0
                percentage = 0
                distance_remaining_km = 0
                elevation_m = 0
        

            id_climb=ClimbsScraper.insert_climb(id_stage, climb_category, distance_km, elevation_m, percentage, distance_remaining_km)

            for rider in climb_rank: 
                id_rider = get_id_rider_by_name(rider['rider_name'], id_race)
                position = rider['rank']
                kom_points_earned = rider['points']
                ClimbsScraper.insert_climb_result(id_rider, id_climb, position, kom_points_earned)


    @staticmethod
    def insert_climb(id_stage, category, distance_km, elevation_m, percentage, distance_remaining_km):
        """
        Insert a climb into the DB and return its id.
        """
        with sqlite3.connect("data/grand_tours.db") as conn:
            cursor = conn.cursor()
            try:
                cursor.execute(
                    "INSERT INTO climb (id_stage, category, distance_km, elevation_m, percentage, distance_remaining_km) VALUES (?, ?, ?, ?, ?, ?)",
                    (id_stage, category, distance_km, elevation_m, percentage, distance_remaining_km)
                )
                print("Insert climb:", id_stage, category, distance_km, elevation_m, percentage, distance_remaining_km)
            except  Exception as e:
                print(" DB Error inserting climb:", e)
            return cursor.lastrowid

    @staticmethod
    def insert_climb_result(id_rider, id_climb, position, kom_points_earned):
        """
        Insert a climb_result into the DB. 
        """
        with sqlite3.connect("data/grand_tours.db") as conn:
            cursor = conn.cursor()
            try:
                cursor.execute(
                    "INSERT INTO climb_result (id_rider, id_climb, position, kom_points_earned) VALUES (?, ?, ?, ?)",
                    (id_rider, id_climb, position, kom_points_earned)
                )
                print('Insert climb result:', id_rider, id_climb, position, kom_points_earned)
            except  Exception as e:
                print(" DB Error inserting climb result:", e)

def clear_database():
    with sqlite3.connect("data/grand_tours.db") as conn:
        cursor = conn.cursor()
        tables = ["race", "rider", "stage", "stage_result", "climb", "climb_result"]
        for table in tables:
            cursor.execute(f"DELETE FROM {table}")
        print("Database cleared.")


clear_database()
RacesScraper.races_scraper(2024)
