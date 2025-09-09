from procyclingstats import Race, RaceStartlist, Stage
import sqlite3

from utils import get_id_rider_by_name, normalize_name, clear_database


def year_scraper(first_year, last_year):
    """ 
    Function enabling retrieving all data between 2 given year, by starting the races_scraper function for each year in range 
    The unique cursor ensure waiting a year to be completed before population the db, and avoid incomplete update caused by an interruption. 
    No return.
    """
    for year in range(first_year, last_year + 1):
        try:
            with sqlite3.connect("data/grand_tours.db") as conn:
                conn.isolation_level = None
                cursor = conn.cursor()
                cursor.execute("BEGIN")
                RacesScraper.races_scraper(year, cursor)
                cursor.execute("COMMIT")
                print(f"Year {year} committed successfully.")
        except Exception as e:
            print(f"Error in year {year}: {e}")
            try:
                cursor.execute("ROLLBACK")
                print(f"Rolled back changes for year {year}.")
            except Exception as rollback_e:
                print(f"Rollback failed for year {year}: {rollback_e}")

class RacesScraper:
    @staticmethod
    def races_scraper(year, cursor):
        """
        Function that, for every year given, collect all the datas for the 3 grand tours
        The function launch other functions about stage, rider and climb and populate the db with : 
        name, year, gc_winner, kom_winner in the race table
        name, id_race in the rider table.
        
        No return.

        """
        gt_list = ['giro-d-italia','tour-de-france','vuelta-a-espana']
        for gt_name in gt_list:
            try:
                id_race = RacesScraper.insert_race(gt_name, year, cursor)

                ## Data Scrapping Part
                
                # populate the rider table
                url_race= f"race/{gt_name}/{year}"
                url_race_startlist = f"race/{gt_name}/{year}/startlist"
                startlist = RaceStartlist(url_race_startlist)
                riders = startlist.startlist()
                for rider in riders:
                    rider_name = rider['rider_name']
                    RacesScraper.insert_rider(rider_name, id_race,cursor)

                # populate the race table
                last_stage = Race(url_race).stages()[-1]
                race_result= Stage(last_stage['stage_url'])
                gc_list = race_result.gc()
                kom_list = race_result.kom()
                if gc_list and kom_list:
                    name_gc_winner = gc_list[0]['rider_name'] 
                    name_kom_winner = kom_list[0]['rider_name'] 

                    gc_winner = get_id_rider_by_name(name_gc_winner, id_race, cursor)
                    kom_winner = get_id_rider_by_name(name_kom_winner, id_race, cursor)

                    RacesScraper.insert_race_winners(id_race, gc_winner, kom_winner,cursor)
            except Exception as e:
                print('Error race table'+e)
            StagesScraper.stages_scraper(id_race, url_race, cursor)

    @staticmethod
    def insert_race(name, year, cursor):
        """
        Insert a race into the DB and return its id.
        """
        cursor.execute(
            "INSERT INTO race (name, year) VALUES (?, ?)",
            (name, year)
        )
        print("Inserted race:", name, "year:", year)
        return cursor.lastrowid
        
    
    @staticmethod    
    def insert_rider(rider_name, id_race, cursor):
        """
        Insert a rider into the DB and return its id.
        """
        cursor.execute(
            "INSERT INTO rider (name, id_race) VALUES (?, ?)",
            (normalize_name(rider_name), id_race)
        )
        print("Inserted rider:", normalize_name(rider_name), "id_race:", id_race)
        return cursor.lastrowid

    @staticmethod
    def insert_race_winners(id_race, gc_winner, kom_winner, cursor):
        """
        Insert a race into the DB and return its id.
        """
        cursor.execute(
            f"UPDATE race SET gc_winner = ?, kom_winner = ? WHERE id = ?",
            (gc_winner, kom_winner, id_race)
        )
        print("Updated race data: winner", gc_winner, "kom_winner:", kom_winner, "id_race:", id_race)


class StagesScraper:
    @staticmethod
    def stages_scraper(id_race, url_race, cursor):
        """
        Function that, for every race given, collect all the data for every stage
        The function launch the climbs_scraper function and populate the db with : 
        id_race, stage_number, type, profile, distance, elevation, winner in the stage table ; 
        id_rider, id_stage, gc_rank, kom_rank, kom_points in the stage_result table for each rider.
        
        No return.
        """
        race_obj = Race(url_race)
        url_list_stages = race_obj.stages('stage_url')
        for i, url_stage in enumerate(url_list_stages, start=1):
            try: 
                stage = Stage(url_stage['stage_url']).parse()
                type = stage['stage_type']
                distance = stage['distance']
                elevation = stage['vertical_meters']
                profile = stage['profile_icon']
                winner = get_id_rider_by_name(stage['results'][0]['rider_name'], id_race, cursor)
                stage_number = i
                id_stage = StagesScraper.insert_stage(id_race, stage_number, type, profile, distance, elevation, winner, cursor)
                
                
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

                    id_rider = get_id_rider_by_name(rider_name, id_race, cursor)
                    StagesScraper.insert_stage_result(id_rider, id_stage, gc_rank, kom_rank, kom_points, cursor)
            except Exception as e: 
                print(f'Error stage table{e}')
            
            ClimbsScraper.climbs_scraper(id_stage, url_stage, id_race, distance, cursor)

        
    @staticmethod
    def insert_stage(id_race, stage_number, type, profile, distance_km, elevation_m, winner, cursor):
        """
        Insert a stage into the DB and return its id.
        """
        cursor.execute(
            "INSERT INTO stage (id_race, stage_number, type, profile, distance_km, elevation_m, winner) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (id_race, stage_number, type, profile, distance_km, elevation_m, winner)
        )
        print("Insert stage:",id_race, stage_number, type, profile, distance_km, elevation_m, winner )
        return cursor.lastrowid
    
    @staticmethod   
    def insert_stage_result(id_rider, id_stage, gc_position, kom_position, kom_points, cursor):
        """
        Insert a stage_result into the DB. 
        """
        cursor.execute(
            "INSERT INTO stage_result (id_rider, id_stage, gc_position, kom_position, kom_points) VALUES (?, ?, ?, ?, ?)",
            (id_rider, id_stage, gc_position, kom_position, kom_points)
        )
        print("Insert stage result:", id_rider, id_stage, gc_position, kom_position, kom_points)

class ClimbsScraper:
    @staticmethod
    def climbs_scraper(id_stage, url_stage, id_race, stage_distance, cursor):
        """
        Function that, for every stage given, collect all the data for every climb
        The function populate the db with : 
        id_stage, climb_category, climb_to_finish in the climb table ; 
        id_rider, id_climb, position, kom_points_earned in the climb_result table for each rider ranked.
        
        No return.
        """
        stage_climbs  = Stage(url_stage['stage_url']).climbs()
        
        for climb in stage_climbs:
            try:
                climb_category = climb['category']
                climb_rank = climb['rank']
                if climb['km_from_start'] != None:
                    climb_to_finish = stage_distance - climb['km_from_start']
                else : 
                    climb_to_finish = None

                id_climb=ClimbsScraper.insert_climb(id_stage, climb_category, climb_to_finish, cursor)

                for rider in climb_rank: 
                    id_rider = get_id_rider_by_name(rider['rider_name'], id_race, cursor)
                    position = rider['rank']
                    kom_points_earned = rider['points']
                    ClimbsScraper.insert_climb_result(id_rider, id_climb, position, kom_points_earned, cursor)
            except Exception as e:
                print(f'Error climb table: {e}')


    @staticmethod
    def insert_climb(id_stage, category, distance_remaining_km, cursor):
        """
        Insert a climb into the DB and return its id.
        """
        cursor.execute(
            "INSERT INTO climb (id_stage, category, distance_remaining_km) VALUES (?, ?, ?)",
            (id_stage, category, distance_remaining_km)
        )
        print("Insert climb:", id_stage, category, distance_remaining_km)
        return cursor.lastrowid

    @staticmethod
    def insert_climb_result(id_rider, id_climb, position, kom_points_earned, cursor):
        """
        Insert a climb_result into the DB. 
        """
        cursor.execute(
            "INSERT INTO climb_result (id_rider, id_climb, position, kom_points_earned) VALUES (?, ?, ?, ?)",
            (id_rider, id_climb, position, kom_points_earned)
        )
        print('Insert climb result:', id_rider, id_climb, position, kom_points_earned)

year_scraper(2005, 2025)
