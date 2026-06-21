read_public_data <- function(path = "data/chess_games_public.csv") {
  df <- read.csv(path, stringsAsFactors = FALSE, encoding = "UTF-8")

  df$GameDateTime <- as.POSIXct(
    paste(df$Date, df$UTCTime),
    format = "%Y-%m-%d %H:%M:%S",
    tz = "UTC"
  )

  df <- df[order(df$Player, df$GameDateTime), ]
  rownames(df) <- NULL

  df$PlayerResult <- with(
    df,
    ifelse(Result == "1-0" & Color == "White", "win",
      ifelse(Result == "0-1" & Color == "White", "lose",
        ifelse(Result == "0-1" & Color == "Black", "win",
          ifelse(Result == "1-0" & Color == "Black", "lose", "draw")
        )
      )
    )
  )

  df$LoseBinary <- ifelse(df$PlayerResult == "lose", 1L, 0L)
  df$Score <- ifelse(df$PlayerResult == "win", 1,
    ifelse(df$PlayerResult == "draw", 0.5, 0)
  )
  df$EloDiff <- df$PlayerElo - df$OpponentElo
  df$ColorWhite <- ifelse(df$Color == "White", 1L, 0L)
  df$OpeningPlayed <- tolower(trimws(df$Opening))
  df
}

sample_players <- function(df, n_players = NULL, seed = 123) {
  all_players <- sort(unique(df$Player))

  if (is.null(n_players) || n_players >= length(all_players)) {
    return(all_players)
  }

  set.seed(seed)
  sort(sample(all_players, n_players))
}

subset_players <- function(df, players) {
  df[df$Player %in% players, , drop = FALSE]
}

compute_loss_streak_flags <- function(df) {
  df$AfterTwoLosses <- FALSE
  df$StreakLength <- 0L

  for (player in unique(df$Player)) {
    index <- which(df$Player == player)
    losses <- df$LoseBinary[index]
    current_streak <- 0L

    for (i in seq_along(index)) {
      df$StreakLength[index[i]] <- current_streak

      if (losses[i] == 1L) {
        current_streak <- current_streak + 1L
      } else {
        current_streak <- 0L
      }
    }

    if (length(index) >= 3) {
      df$AfterTwoLosses[index[3:length(index)]] <-
        losses[2:(length(losses) - 1)] == 1 &
        losses[1:(length(losses) - 2)] == 1
    }
  }

  df
}

normal_ci <- function(values) {
  n <- length(values)
  x_bar <- mean(values)
  variance <- sum((values - x_bar)^2) / (n - 1)
  standard_error <- sqrt(variance / n)
  c(
    lower = x_bar - 1.96 * standard_error,
    upper = x_bar + 1.96 * standard_error
  )
}

analyse_loss_probability <- function(df) {
  baseline_loss_rate <- mean(df$LoseBinary)
  after_values <- df$LoseBinary[df$AfterTwoLosses]

  x_bar <- mean(after_values)
  variance <- sum((after_values - x_bar)^2) / (length(after_values) - 1)
  standard_deviation <- sqrt(variance)
  standard_error <- standard_deviation / sqrt(length(after_values))
  z_value <- (x_bar - baseline_loss_rate) / standard_error
  p_value <- 1 - pnorm(z_value)

  list(
    baseline_loss_rate = baseline_loss_rate,
    after_two_losses_rate = x_bar,
    sample_size = length(after_values),
    variance = variance,
    standard_deviation = standard_deviation,
    standard_error = standard_error,
    z_value = z_value,
    p_value = p_value,
    confidence_interval = normal_ci(after_values)
  )
}

preferred_opening_map <- function(df) {
  keys <- paste(df$Player, df$Color, sep = "::")
  opening_tables <- split(df$OpeningPlayed, keys)

  preferred <- lapply(opening_tables, function(openings) {
    counts <- sort(table(openings), decreasing = TRUE)
    names(counts)[1]
  })

  unlist(preferred, use.names = TRUE)
}

analyse_openings <- function(df) {
  preferred <- preferred_opening_map(df)
  keys <- paste(df$Player, df$Color, sep = "::")
  df$PlayedPreferred <- preferred[keys] == df$OpeningPlayed

  compare_color <- function(color_name) {
    after_values <- df$PlayedPreferred[df$Color == color_name & df$AfterTwoLosses]
    normal_values <- df$PlayedPreferred[df$Color == color_name & !df$AfterTwoLosses]

    p_after <- mean(after_values)
    p_normal <- mean(normal_values)
    pooled <- (sum(after_values) + sum(normal_values)) /
      (length(after_values) + length(normal_values))
    variance <- pooled * (1 - pooled) * (
      1 / length(after_values) + 1 / length(normal_values)
    )
    standard_deviation <- sqrt(variance)
    z_value <- (p_after - p_normal) / standard_deviation
    p_value <- 2 * (1 - pnorm(abs(z_value)))

    data.frame(
      Color = color_name,
      p_after = p_after,
      p_normal = p_normal,
      variance = variance,
      standard_deviation = standard_deviation,
      z_value = z_value,
      p_value = p_value
    )
  }

  rbind(compare_color("White"), compare_color("Black"))
}

analyse_move_count <- function(df) {
  overall_mean <- mean(df$NumMoves)
  after_values <- df$NumMoves[df$AfterTwoLosses]

  x_bar <- mean(after_values)
  variance <- sum((after_values - x_bar)^2) / (length(after_values) - 1)
  standard_deviation <- sqrt(variance)
  standard_error <- standard_deviation / sqrt(length(after_values))
  z_value <- (x_bar - overall_mean) / standard_error
  p_value <- pnorm(z_value)

  list(
    baseline_move_average = overall_mean,
    after_two_losses_average = x_bar,
    sample_size = length(after_values),
    variance = variance,
    standard_deviation = standard_deviation,
    standard_error = standard_error,
    z_value = z_value,
    p_value = p_value,
    confidence_interval = normal_ci(after_values)
  )
}

empirical_moments <- function(df) {
  variables <- list(
    Score = df$Score,
    StreakLength = df$StreakLength,
    EloDiff = df$EloDiff,
    PlayerElo = df$PlayerElo,
    OpponentElo = df$OpponentElo,
    NumMoves = df$NumMoves
  )

  data.frame(
    variable = names(variables),
    mean = sapply(variables, mean),
    median = sapply(variables, median),
    sd = sapply(variables, sd),
    min = sapply(variables, min),
    max = sapply(variables, max),
    row.names = NULL
  )
}

streak_profile <- function(df, max_streak = 6) {
  streak_values <- sort(unique(df$StreakLength[df$StreakLength <= max_streak]))

  data.frame(
    StreakLength = streak_values,
    Games = sapply(streak_values, function(streak) {
      sum(df$StreakLength == streak)
    }),
    AverageScore = sapply(streak_values, function(streak) {
      mean(df$Score[df$StreakLength == streak])
    }),
    row.names = NULL
  )
}

run_regression_models <- function(df) {
  simple_model <- lm(Score ~ StreakLength, data = df)
  multiple_model <- lm(Score ~ StreakLength + EloDiff + Color, data = df)

  list(
    simple_model = simple_model,
    multiple_model = multiple_model,
    simple_summary = summary(simple_model),
    multiple_summary = summary(multiple_model)
  )
}

descriptive_stats <- function(df) {
  games_per_player <- table(df$Player)
  top_openings <- sort(table(df$OpeningPlayed), decreasing = TRUE)[1:5]

  list(
    games = nrow(df),
    players = length(unique(df$Player)),
    mean_games_per_player = mean(as.numeric(games_per_player)),
    median_games_per_player = median(as.numeric(games_per_player)),
    results = table(df$PlayerResult),
    top_openings = top_openings,
    moments = empirical_moments(df),
    streak_profile = streak_profile(df)
  )
}

run_analysis <- function(path = "data/chess_games_public.csv", n_players = NULL, seed = 123) {
  df <- read_public_data(path)
  selected_players <- sample_players(df, n_players = n_players, seed = seed)
  df <- subset_players(df, selected_players)
  df <- compute_loss_streak_flags(df)

  list(
    data = df,
    descriptive = descriptive_stats(df),
    loss_probability = analyse_loss_probability(df),
    opening_shift = analyse_openings(df),
    move_count = analyse_move_count(df),
    regressions = run_regression_models(df)
  )
}

if (sys.nframe() == 0) {
  results <- run_analysis()

  cat("Public chess tilt analysis\n")
  cat("==========================\n\n")

  cat("Dataset\n")
  print(results$descriptive)
  cat("\nEmpirical moments\n")
  print(results$descriptive$moments)
  cat("\nScore by streak length\n")
  print(results$descriptive$streak_profile)
  cat("\nLoss probability after two losses\n")
  print(results$loss_probability)
  cat("\nPreferred opening comparison\n")
  print(results$opening_shift)
  cat("\nMove count after two losses\n")
  print(results$move_count)
  cat("\nSimple regression: Score ~ StreakLength\n")
  print(results$regressions$simple_summary)
  cat("\nMultiple regression: Score ~ StreakLength + EloDiff + Color\n")
  print(results$regressions$multiple_summary)
}
