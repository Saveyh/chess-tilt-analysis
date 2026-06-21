# Extended Analysis

This note captures the main methodological improvement from the later continuation of the project.

## What the second phase added

The original course project mostly asked a binary question: what happens after two consecutive losses?

The later continuation pushed the analysis further by adding:

- `StreakLength`: a continuous variable counting how many losses immediately precede each game
- `EloDiff`: the player's Elo minus the opponent's Elo
- `Color`: a control for playing White or Black
- linear regression models to separate the raw streak effect from structural game factors

## Why this is worth showing in the repository

This extension makes the portfolio story stronger because it shows progression:

- first, a classical inferential statistics project
- then, a more explicit modeling step with controls and diagnostics

That is a better signal on GitHub than only showing the first report.

## Public-safe takeaway from the current anonymized dataset

Using the cleaned public dataset in this repository:

- the simple model `Score ~ StreakLength` gives a negative coefficient for `StreakLength` of about `-0.0158`
- after adding controls with `Score ~ StreakLength + EloDiff + Color`, the streak coefficient remains negative at about `-0.0082`
- the Elo gap is strongly positive, around `0.000857` points of expected score per Elo point
- playing White is also positive, around `0.046`
- model fit stays modest (`R^2 ~= 0.035` in the multiple model), which is consistent with noisy blitz-game outcomes

These values differ from the private course report because this repository works from the public cleaned dataset and keeps all 40 tracked players instead of reproducing the exact private classroom sample.
