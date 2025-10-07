# Polka Project

The **Polka Project** aims to predict the future **King of the Mountains (KOM)** outcome of the **Tour de France 2026**.  
Specifically, we seek to determine whether the KOM jersey will be won by a GC contender or a breakaway climber.

This motivation emerged from this year's debate on the true nature of the KOM jersey, as more and more Grand Tour winners have collected the KOM jersey without explicitly targeting it.  
Race organizers are often accused of fueling this trend through their course design — awarding a large number of points at stage finishes and increasing the gap between small and large climbs.

**Can we predict the KOM outcome using only the Grand Tour route?**

---

**Methodology:**

- **Data Scraping**

Using and adapting the `procyclingstats` package, we retrieved all available data on routes, stage results, and climb details for every race (63 in total).  
The data are not consistent across all years — much more information has been available since 2021, for instance.  
To ensure dataset homogeneity, we focused on data available since 2005.

All data were stored in a SQL database (schema provided at the end).


- **Data Preparation**

To meet predictive analysis requirements, data were aggregated into one row per race.  
Particular attention was given to including only the type of data that would be available when the route is announced.

Using **CatBoost**, we encoded the dataset with binary columns to prepare for the TDF 2026 prediction.  
We created an indicator variable:  
- **1** if the KOM was won by a GC rider (top 5 overall)  
- **0** otherwise  

Our objective is to determine whether the KOM winner is a GC rider or a breakaway climber (i.e., someone not competing for the general classification).


- **Machine Learning training**

We used a **CatBoostClassifier** for predictive analysis, leveraging a Leave-One-Group-Out (LOGO) cross-validation strategy, where each “group” corresponds to a race year.  

Since the dataset contains many features (over 20) but relatively few rows (63), training was split into two versions:
- A main model using all features — to determine feature importance  
- A lite model using only 8 features — to focus on prediction accuracy  

For each fold:
- The model is trained on all but one year and tested on the held-out year  
- Performance is measured using AUC and classification reports  
- Feature importances are extracted to identify the most predictive variables  

**Model parameters:**
- 300 iterations  
- Learning rate: 0.05  
- Depth: 3  
- Loss function: Logloss  
- Evaluation metric: AUC  
---

**Results:**

No reliable results were obtained due to the small dataset size.

Despite tuning parameters, experimenting with different cross-validation methods, and optimizing setups for small samples, we could not prevent overfitting.

Although such a small dataset could theoretically work with fewer features, the low proportion of positive cases (GC rider winning the KOM) made cross-validation unstable, as some validation folds contained no positive examples.


--- 

**Data Sources:**

This project rely on data from the 3 Grand Tours, from 2005 to 2025. For doing so, we used the [`procyclingstats.com`](https://www.procyclingstats.com)  website ressources, mainly working with the `procyclingstats` scraping package.

--- 

### Database Schema

**Tables:**

- **race**: `id`, `name`, `year`, `gc_winner`, `kom_winner`
- **rider**: `id`, `name`, `id_race`
- **stage**: `id`, `id_race`, `stage_number`, `type`, `profile`, `distance_km`, `elevation_m`, `winner`
- **stage_result**: `id_rider`, `id_stage`, `gc_position`, `kom_position`, `kom_points`
- **climb**: `id`, `id_stage`, `category`, `distance_remaining_km`
- **climb_result**: `id_rider`, `id_climb`, `position`, `kom_points_earned`

---

**Main Contributor:**

Pierre-Olivier LEYGUE

pierreolivier.leygue@sciencespo.fr