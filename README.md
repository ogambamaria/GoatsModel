# Goat Population Projection Model

## Overview

This project implements a **Leslie matrix–style population projection model** for Kenya’s meat goat sector. The model combines **KNBS livestock totals** with **KIAMIS survey age-sex proportions** to initialize a structured baseline (2023). From this base, the system projects future population, milk, meat, and feed intake over a chosen horizon (e.g., 10 years).

The model is deterministic, parameterized from literature and expert ranges, and designed to explore **slow, progressive growth scenarios** under realistic herd dynamics.


## Key Features

* **Structured population**
  Animals are grouped into age classes:

  * Kids 0–6 months
  * Kids 6–12 months
  * Yearlings 1–2 years
  * Adults 2–4 years
  * Adults 4–6 years

* **Leslie matrix approach**

  * **Top row**: fertility (number of female kids per doe per year, adjusted by breeding fractions, kidding rate, litter size, and sex ratio).
  * **Sub-diagonal**: survival probabilities (1 – mortality – offtake).
  * Applied annually to update the state vector of each cohort.

* **Production outputs**

  * **Milk**: derived from lactating proportion × milk yield per day × lactation days.
  * **Meat**: off-take numbers × live weight × carcass yield.
  * **Feed demand**: dry matter intake as % of body weight × live weight × population.

* **Data-driven baseline (2023)**

  * **KNBS (2018–2023)**: national totals for meat goats.
  * **KIAMIS (2021)**: age-sex distribution, scaled to KNBS totals.


## Parameters

Core biological and management parameters (tunable within observed ranges):

* **Reproduction**: kidding rate, litter size, kidding interval, sex ratio at birth.
* **Mortality**: age-specific mortality rates.
* **Offtake**: sales + culling rates by age class (can be biased toward males).
* **Breeding fractions**: proportion of females in each age class that reproduce.
* **Milk**: yield per doe per day, lactation length, lactating proportion.
* **Weights & DMI**: average live weights per class, dry matter intake % body weight.


## Workflow

1. **Load & clean KNBS and KIAMIS data**.
2. **Aggregate KIAMIS proportions** into the defined age classes.
3. **Scale to KNBS national totals** for 2023 baseline population.
4. **Build initial state vector** (age × sex × reproductive status).
5. **Iterate Leslie projection** for chosen years ahead.
6. **Calculate outputs**: population, milk, meat, feed.
7. **Visualize results** (plots of total herd, age classes, milk/meat/feed).


## Assumptions

* **Mid-year births**: kidding occurs halfway through the year, smoothing cohort transitions.
* **Constant parameters**: no shocks or improvements (though scenario analysis is possible).
* **No density dependence**: feed constraints and land limits are not yet modeled.
* **Equal male/female mortality** unless explicitly biased in offtake rules.