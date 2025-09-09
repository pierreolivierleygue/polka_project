import sqlite3
import pandas as pd

conn = sqlite3.connect("data/grand_tours.db")


races = pd.read_sql(
    """
    SELECT r.id AS race_id,
           r.name AS race_name,
           r.year AS year,
           r.gc_winner AS gc_winner_id,
           r.kom_winner AS kom_winner_id
    FROM race r
    WHERE r.kom_winner IS NOT NULL
    """,
    conn,
)


stage_agg = pd.read_sql(
    """
    SELECT s.id_race AS race_id,
           COUNT(*) AS n_stages,
           SUM(s.distance_km) AS total_stage_distance_km,
           SUM(COALESCE(s.elevation_m,0)) AS total_stage_elevation_m,
           SUM(CASE WHEN s.type='ITT' THEN 1 ELSE 0 END) AS n_itt,
           SUM(CASE WHEN s.type='TTT' THEN 1 ELSE 0 END) AS n_ttt,
           SUM(CASE WHEN s.type='RR'  THEN 1 ELSE 0 END) AS n_rr,
           SUM(CASE WHEN s.profile='p0' THEN 1 ELSE 0 END) AS n_p0,
           SUM(CASE WHEN s.profile='p1' THEN 1 ELSE 0 END) AS n_p1,
           SUM(CASE WHEN s.profile='p2' THEN 1 ELSE 0 END) AS n_p2,
           SUM(CASE WHEN s.profile='p3' THEN 1 ELSE 0 END) AS n_p3,
           SUM(CASE WHEN s.profile='p4' THEN 1 ELSE 0 END) AS n_p4,
           SUM(CASE WHEN s.profile='p5' THEN 1 ELSE 0 END) AS n_p5
    FROM stage s
    GROUP BY s.id_race
    """,
    conn,
)

climb_agg = pd.read_sql(
    """
    WITH climbs AS (
        SELECT c.*, s.id_race, s.stage_number
        FROM climb c
        JOIN stage s ON s.id = c.id_stage
    )
    SELECT id_race AS race_id,
           COUNT(*) AS n_climbs,
           SUM(CASE WHEN category='HC' THEN 1 ELSE 0 END) AS n_hc,
           SUM(CASE WHEN category='1'  THEN 1 ELSE 0 END) AS n_cat1,
           SUM(CASE WHEN category='2'  THEN 1 ELSE 0 END) AS n_cat2,
           SUM(CASE WHEN category='3'  THEN 1 ELSE 0 END) AS n_cat3,
           SUM(CASE WHEN category='4'  THEN 1 ELSE 0 END) AS n_cat4,
           AVG(percentage) AS avg_gradient_all,
           MAX(percentage) AS max_gradient_all,
           AVG(distance_km) AS avg_climb_distance_km,
           SUM(distance_km) AS total_climb_distance_km,
           AVG(elevation_m) AS avg_climb_elevation_m,
           SUM(elevation_m) AS total_climb_elevation_m,
           -- Late-climb features: climbs appearing close to finish
           SUM(CASE WHEN distance_remaining_km <= 10 THEN 1 ELSE 0 END) AS n_climbs_last10km,
           SUM(CASE WHEN distance_remaining_km BETWEEN 10 AND 20 THEN 1 ELSE 0 END) AS n_climbs_10to20km
    FROM climbs
    GROUP BY id_race
    """,
    conn,
)

final_climb = pd.read_sql(
    """
    WITH climbs AS (
        SELECT c.*, s.id_race, s.id AS stage_id
        FROM climb c
        JOIN stage s ON s.id = c.id_stage
    ), final_per_stage AS (
        SELECT stage_id,
               id_race,
               MIN(distance_remaining_km) AS min_dist_rem
        FROM climbs
        GROUP BY stage_id, id_race
    )
    SELECT f.id_race AS race_id,
           COUNT(*) AS stages_with_climbs,
           SUM(CASE WHEN c.category='HC' THEN 1 ELSE 0 END) AS stages_final_HC,
           SUM(CASE WHEN c.category='1'  THEN 1 ELSE 0 END) AS stages_final_cat1,
           SUM(CASE WHEN c.category='2'  THEN 1 ELSE 0 END) AS stages_final_cat2,
           SUM(CASE WHEN c.category='3'  THEN 1 ELSE 0 END) AS stages_final_cat3,
           SUM(CASE WHEN c.category='4'  THEN 1 ELSE 0 END) AS stages_final_cat4
    FROM final_per_stage f
    JOIN climbs c
      ON c.stage_id = f.stage_id AND c.distance_remaining_km = f.min_dist_rem
    GROUP BY f.id_race
    """,
    conn,
)

features = (
    races.merge(stage_agg, on="race_id", how="left")
          .merge(climb_agg, on="race_id", how="left")
          .merge(final_climb, on="race_id", how="left")
)

features["climb_density_per_stage"] = features["n_climbs"].fillna(0) / features["n_stages"].clip(lower=1)
features["hc_ratio"] = features["n_hc"].fillna(0) / features["n_climbs"].clip(lower=1)
features["cat1plus_ratio"] = (features["n_hc"].fillna(0) + features["n_cat1"].fillna(0)) / features["n_climbs"].clip(lower=1)
features["late_climb_share"] = (features["n_climbs_last10km"].fillna(0)) / features["n_climbs"].clip(lower=1)
features["final_hard_stage_share"] = (features["stages_final_HC"].fillna(0) + features["stages_final_cat1"].fillna(0)) / features["n_stages"].clip(lower=1)

# --- 3) LABEL: Is KOM winner effectively a GC rider? ---
# Final GC per rider+race from stage_result (lowest gc_position encountered is the final)
final_gc = pd.read_sql(
    """
    SELECT sr.id_rider,
           s.id_race AS race_id,
           sr.gc_position AS final_gc_position
    FROM stage_result sr
    JOIN stage s ON s.id = sr.id_stage
    WHERE sr.gc_position IS NOT NULL AND s.stage_number = 21
    GROUP BY sr.id_rider, s.id_race
    """,
    conn,
)

features = features.merge(final_gc, left_on=["kom_winner_id","race_id"], right_on=["id_rider","race_id"], how="left")

# Label rule: 1 if KOM winner finished top-N in GC OR kom_winner == gc_winner
TOP_N_GC = 5          
features["label_gc"] = 0
features.loc[(features["final_gc_position"] <= TOP_N_GC) | (features["kom_winner_id"] == features["gc_winner_id"]), "label_gc"] = 1