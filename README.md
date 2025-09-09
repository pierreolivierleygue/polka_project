# Polka Project

The Polka Project aims to predict the future **KOM** outcomes of the **Tour de France 2026**. Specifically, we seek to determine whether the KOM jersey will be won by a GC rider or a breakaway climber.

---

**Data Sources:**

In this project, we used data from the 3 Grand Tours, from 2005 to 2025. For doing so, we used the [`procyclingstats.com`](https://www.procyclingstats.com)  website ressources, mainly working with the `procyclingstats` scraping package.

---

**Methodology:**
- **Machine Learning Model:** **CatBoost** for predictive analysis.

First we retrieve all data available about the route, results for each stage, for each climb for every race (63). 
Note that we have lot more infos available for each climb since 2020-21, but to have a reasonable amount of editions and to keep infos homogeneity for each race, we choose to only focus on infos available since 2005. 

Then in order to prepare the best our data for the machine learning analysis, we had to put each race into only one row, and hence had to put key agglomerated infos about each edition. We had a particular attention about giving only data that are going to be available when the route is going to be announced (number of each category climb... but not startlist infos)

Now what are we testing ? 
Our objective is to see if the KOM winner is a GC rider or a Breakaway climber (i.e. someone that is not fighting for his GC rank).
Therefore we set an indicator: 1 if the KOM was won by a GC rider, 0 otherwise.
Hence we aim to predict the binary outcome of the TDF 2026. 

What define a GC rider ? We choose define a GC rider as someone finishing in the top 5. 

---

**Results:**

--- 
**Projections:**

--- 
**Main Contributor:**
Pierre-Olivier LEYGUE