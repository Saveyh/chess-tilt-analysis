# Psychological Impact of Consecutive Losses in Chess

This repository contains a cleaned public version of a university statistics project about losing streaks in online chess. The goal is to test whether two consecutive losses are associated with a higher probability of losing again, a change in opening choice, or a shorter game.

It also includes a later extension of the project that moves from simple hypothesis tests to a more explicit modeling approach using streak length, Elo difference, and color controls.

The original course material was reorganized before publication so the repository is reproducible and safe to share publicly. Raw course files with personal or non-publication-friendly information are intentionally excluded from Git.

## What is in this public version

- `analysis/chess_tilt_analysis.R`: cleaned R script for the statistical analysis
- `data/chess_games_public.csv`: repaired and anonymized dataset for the public repo
- `scripts/prepare_public_dataset.py`: utility that repairs the original CSV export and anonymizes usernames
- `scripts/compute_public_summary.py`: utility that generates a markdown summary from the public dataset
- `docs/public_summary.md`: generated summary used to quickly inspect the public dataset
- `docs/extended_analysis.md`: public-safe summary of the later modeling extension
- `docs/publication_notes.md`: notes about what was changed before publication

## Research question

After two consecutive losses, do chess players:

1. become more likely to lose again?
2. change their preferred opening?
3. play shorter games?

## Public dataset

The source data came from public Lichess games gathered for the class project. For the GitHub version:

- player and opponent usernames were anonymized
- malformed CSV rows were repaired
- dates were normalized to `YYYY-MM-DD`
- the dataset was exported again as UTF-8 CSV

The public dataset contains 3,695 games played by 40 tracked players in a single session window.

## Main findings from the public dataset

- The overall loss rate is about `0.489`.
- After two consecutive losses, the loss rate rises to about `0.530`.
- Preferred opening usage changes only slightly after a losing streak.
- Average game length stays almost unchanged after two losses.
- In the later extension, the effect remains negative when performance is modeled against full streak length with Elo and color controls, but it becomes smaller once those structural factors are included.

These findings are directionally consistent with the original project report, although exact values may differ slightly because the public repository rebuilds a cleaned dataset and reproducible pipeline from the course files.

## How to reproduce

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

The same script now also returns:

- descriptive moments
- score by streak length
- a simple regression on `StreakLength`
- a multiple regression with `EloDiff` and `Color`

## Why some original files are missing

The original private course folder included:

- a PDF report with author names, student numbers, and PDF author metadata
- a raw CSV containing public usernames
- a draft R script tied to a local machine path

Those files are still available locally, but they are excluded from the public repository on purpose.

## Portfolio note

This repository is intended to show a real school project in a cleaner, more professional format:

- reproducible data preparation
- public-safe data
- readable analysis code
- documentation that explains both the research question and the publication choices
- a visible progression from hypothesis testing to a more mature modeling step
