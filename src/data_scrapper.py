from procyclingstats import *
import sqlite3

from utils import get_id_rider_by_name


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
            url_race = f"race/{gt_name}/{year}/startlist"
            startlist = RaceStartlist(url_race)
            riders = startlist.startlist()
            for rider in riders:
                rider_name = rider['rider_name']
                RacesScraper.insert_rider(rider_name, id_race)

            # populate the race table
            race= Stage(f"race/{gt_name}/{year}/stage-21")
            gc_list = race.gc()
            kom_list = race.kom()
            if gc_list and kom_list:
                name_gc_winner = race.gc()[0]['name'] 
                name_kom_winner = race.kom()[0]['name'] 

                gc_winner = get_id_rider_by_name(name_gc_winner, id_race)
                kom_winner = get_id_rider_by_name(name_kom_winner, id_race)

                RacesScraper.insert_race_winners(id_race, gc_winner, kom_winner)
        
            StagesScraper.stages_scraper(id_race, url_race)

    @staticmethod
    def insert_race(name, year):
        """
        Insert a race into the DB and return its id.
        """
        with sqlite3.connect("grand_tours.db") as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO race (name, year) VALUES (?, ?)",
                (name, year)
            )
            return cursor.lastrowid
    
    @staticmethod    
    def insert_rider(rider_name, id_race):
        """
        Insert a rider into the DB and return its id.
        """
        conn = sqlite3.connect("grand_tours.db")
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO rider (name, id_race) VALUES (?, ?)",
            (rider_name, id_race)
        )
        conn.commit()
        id_rider = cursor.lastrowid
        conn.close()
        return id_rider

    @staticmethod
    def insert_race_winners(id_race, gc_winner, kom_winner):
        """
        Insert a race into the DB and return its id.
        """
        with sqlite3.connect("grand_tours.db") as conn:
            cursor = conn.cursor()
            cursor.execute(
                f"INSERT INTO race (gc_winner, kom_winner) VALUES (?, ?) WHERE id = {id_race}",
                (gc_winner, kom_winner)
            )


class StagesScraper:
    @staticmethod
    def stages_scraper(id_race, url_race):
        """
        """

        url_list_races = Race.stages(url_race, url_race)
        for i, url_race in enumerate(url_list_races, start=1):
            stage = Stage(url_race).parse
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

    
        
    @staticmethod
    def insert_stage(id_race, stage_number, type, profile, distance_km, elevation_m, winner):
        """
        Insert a stage into the DB and return its id.
        """
        with sqlite3.connect("grand_tours.db") as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO stage (id_race, stage_number, type, profile, distance_km, elevation_m, winner) VALUES (?, ?, ?, ?, ?, ?, ?)",
                (id_race, stage_number, type, profile, distance_km, elevation_m, winner)
            )
            return cursor.lastrowid

    def insert_stage_result(id_rider, id_stage, gc_position, kom_position, kom_points):
        """
        Insert a stage_result into the DB. 
        """
        with sqlite3.connect("grand_tours.db") as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO stage_result (id_rider, id_stage, gc_position, kom_position, kom_points) VALUES (?, ?, ?, ?, ?)",
                (id_rider, id_stage, gc_position, kom_position, kom_points)
            )

class ClimbsScraper:
    @staticmethod
    def climbs_scraper():
        """
        """


    @staticmethod
    def insert_stage(id_race, stage_number, type, profile, distance_km, elevation_m, winner):
        """
        Insert a stage into the DB and return its id.
        """
        with sqlite3.connect("grand_tours.db") as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO stage (id_race, stage_number, type, profile, distance_km, elevation_m, winner) VALUES (?, ?, ?, ?, ?, ?, ?)",
                (id_race, stage_number, type, profile, distance_km, elevation_m, winner)
            )
            return cursor.lastrowid

    def insert_stage_result(id_rider, id_stage, gc_position, kom_position, kom_points):
        """
        Insert a stage_result into the DB. 
        """
        with sqlite3.connect("grand_tours.db") as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO stage_result (id_rider, id_stage, gc_position, kom_position, kom_points) VALUES (?, ?, ?, ?, ?)",
                (id_rider, id_stage, gc_position, kom_position, kom_points)
            )