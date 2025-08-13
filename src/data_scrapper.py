from procyclingstats import *


def global_scrapper(first_year, last_year):
    """ 
    Function made in order to run all the data needed
    2 parameters : first_year and last_year
    No return, just run other functions in order to feed the db.
    """
    for i in range(last_year - first_year + 1):
        year = first_year+i
        grand_tour_scrapper(year)

def grand_tour_scrapper(year):
    """
    Function that, for every year given, collect all the datas for the 3 grand tours
    The function start other functions about stage, rider and climb but feed the db with : 
    name, year, gc_winner, kom_winner in the race table

    1 parameter: the year

    """
    gt_list = ['giro-d-italia','tour-de-france','vuelta-a-espana']
    for i in range(len(gt_list)):
        name=gt_list[i]
        # procycling stats with name, year, gc_winner, kom_winner
        race= Race(f"race/{name}/{year}")
        print(race.parse())
        #list = [name,year,gc_winner, kow_winner]
        #stage_scrapper(year, gt_list[i])
        #rider_scrapper()

print(grand_tour_scrapper(2025))


#def stage_scrapper(year, name):

   # for i in range(21): 

#def rider_scrapper():

#def climb_scrapper()