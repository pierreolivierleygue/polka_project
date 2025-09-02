CREATE TABLE race(
    id INTEGER PRIMARY KEY,
    name TEXT CHECK (name IN ('tour-de-france','giro-d-italia','vuelta-a-espana')),
    year INTEGER NOT NULL,
    gc_winner INTEGER,
    kom_winner INTEGER,
    FOREIGN KEY (gc_winner) REFERENCES rider(id),
    FOREIGN KEY (kom_winner) REFERENCES rider(id)
);

CREATE TABLE stage(
    id INTEGER PRIMARY KEY,
    id_race INTEGER NOT NULL,
    stage_number INTEGER NOT NULL,
    type TEXT CHECK (type IN ('ITT','TTT','RR')),
    profile TEXT CHECK (profile IN ('p0','p1','p2','p3','p4','p5')),
    distance_km REAL,
    elevation_m REAL,
    winner INTEGER,
    FOREIGN KEY (id_race) REFERENCES race(id),
    FOREIGN KEY (winner) REFERENCES rider(id)
);

CREATE TABLE rider(
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    id_race INTEGER NOT NULL,
    FOREIGN KEY (id_race) REFERENCES race(id)
);

CREATE TABLE climb(
    id INTEGER PRIMARY KEY,
    id_stage INTEGER NOT NULL,
    category TEXT CHECK (category IN ('4','3','2','1','HC')),
    distance_remaining_km REAL,
    distance_km REAL,
    elevation_m REAL,
    percentage REAL,
    FOREIGN KEY (id_stage) REFERENCES stage(id)
);

CREATE TABLE stage_result(
    id_rider INTEGER NOT NULL,
    id_stage INTEGER NOT NULL,
    gc_position INTEGER,
    kom_position INTEGER,
    kom_points INTEGER,
    PRIMARY KEY (id_rider, id_stage),
    FOREIGN KEY (id_rider) REFERENCES rider(id),
    FOREIGN KEY (id_stage) REFERENCES stage(id)
);

CREATE TABLE climb_result(
    id_rider INTEGER NOT NULL,
    id_climb INTEGER NOT NULL,
    position INTEGER,
    kom_points_earned INTEGER,
    PRIMARY KEY (id_rider, id_climb),
    FOREIGN KEY (id_rider) REFERENCES rider(id),
    FOREIGN KEY (id_climb) REFERENCES climb(id)
);