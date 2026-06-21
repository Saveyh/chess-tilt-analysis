# Chess Tilt Analysis
![R](https://img.shields.io/badge/R-Statistical%20Analysis-276DC3?logo=r&logoColor=white)
![Python](https://img.shields.io/badge/Python-Data%20Preparation-3776AB?logo=python&logoColor=white)
![CSV](https://img.shields.io/badge/CSV-Cleaned%20Dataset-4D9A3A?logo=files&logoColor=white)
![Regression](https://img.shields.io/badge/Regression-OLS%20Modeling-8A2BE2)
![Hypothesis Testing](https://img.shields.io/badge/Hypothesis%20Testing-Inferential%20Stats-C0392B)
![Data Cleaning](https://img.shields.io/badge/Data%20Cleaning-Anonymization%20%26%20Repair-16A085)
![Lichess](https://img.shields.io/badge/Lichess-Game%20Data-000000?logo=lichess&logoColor=white)
![Status](https://img.shields.io/badge/Status-Public%20Portfolio%20Version-2E8B57)

This repository presents a public, reproducible analysis of losing streaks in online chess. It starts from raw Lichess game exports and asks whether consecutive losses are associated with weaker subsequent performance.

The project combines two stages of work:

- an inferential statistics phase focused on what happens after two consecutive losses
- a later modeling phase that extends the analysis with streak length, Elo difference, and color controls

## Project Overview

Main research questions:

1. Are players more likely to lose again after two consecutive losses?
2. Do they change their preferred opening more often after a losing streak?
3. Do games become shorter after consecutive losses?
4. Does the effect remain when performance is modeled with structural controls?

## Skills Demonstrated

- Data cleaning and repair of malformed CSV exports
- Anonymization of public usernames for safe publication
- Exploratory analysis and descriptive statistics
- Hypothesis testing on behavioral outcomes
- Regression modeling with control variables
- Reproducible workflow across Python and R

## Dataset

The public dataset contains `3,695` Blitz games from `40` tracked players.

For the GitHub version:

- player and opponent usernames were anonymized
- malformed CSV rows were repaired
- dates were normalized to `YYYY-MM-DD`
- the dataset was exported as UTF-8 CSV

## Methods

The repository includes:

- binary-event analysis after two consecutive losses
- opening preference comparison after a losing streak
- move-count comparison after a losing streak
- an extended regression analysis using:
  - `StreakLength`
  - `EloDiff`
  - `Color`

## Key Findings

- The overall loss rate is about `0.489`.
- After two consecutive losses, the loss rate rises to about `0.530`.
- Preferred opening usage changes only slightly after a losing streak.
- Average game length stays almost unchanged after two losses.
- In the extended model, the streak effect remains negative, but it becomes smaller once Elo difference and color are included.

## Repository Structure

- `analysis/chess_tilt_analysis.R`: main analysis script
- `data/chess_games_public.csv`: repaired and anonymized public dataset
- `scripts/prepare_public_dataset.py`: data-repair and anonymization utility
- `scripts/compute_public_summary.py`: summary-generation utility
- `docs/public_summary.md`: generated dataset summary
- `docs/extended_analysis.md`: note on the later modeling extension

## Reproduce

Generate the public dataset:

```bash
python scripts/prepare_public_dataset.py
```

Generate the markdown summary:

```bash
python scripts/compute_public_summary.py
```

Run the R analysis:

```r
source("analysis/chess_tilt_analysis.R")
results <- run_analysis()
```

The R analysis returns:

- descriptive moments
- score by streak length
- a simple regression on `StreakLength`
- a multiple regression with `EloDiff` and `Color`
