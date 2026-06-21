"""Generate a small markdown summary from the public dataset."""

from __future__ import annotations

import csv
import math
from collections import Counter, defaultdict
from pathlib import Path
from statistics import mean, median


ROOT = Path(__file__).resolve().parents[1]
PUBLIC_CSV = ROOT / "data" / "chess_games_public.csv"
SUMMARY_MD = ROOT / "docs" / "public_summary.md"


def load_rows() -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    with PUBLIC_CSV.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            result = str(row["Result"])
            color = str(row["Color"])
            if result == "1-0" and color == "White":
                player_result = "win"
            elif result == "0-1" and color == "White":
                player_result = "lose"
            elif result == "1-0" and color == "Black":
                player_result = "lose"
            elif result == "0-1" and color == "Black":
                player_result = "win"
            else:
                player_result = "draw"

            rows.append(
                {
                    "Player": str(row["Player"]),
                    "Color": color,
                    "Opponent": str(row["Opponent"]),
                    "PlayerElo": int(row["PlayerElo"]),
                    "OpponentElo": int(row["OpponentElo"]),
                    "Result": result,
                    "Date": str(row["Date"]),
                    "UTCTime": str(row["UTCTime"]),
                    "Opening": str(row["Opening"]).strip(),
                    "NumMoves": int(row["NumMoves"]),
                    "PlayerResult": player_result,
                }
            )

    rows.sort(key=lambda row: (row["Player"], row["Date"], row["UTCTime"]))
    return rows


def proportion_test(success_a: int, total_a: int, success_b: int, total_b: int) -> tuple[float, float]:
    p_a = success_a / total_a
    p_b = success_b / total_b
    pooled = (success_a + success_b) / (total_a + total_b)
    variance = pooled * (1 - pooled) * ((1 / total_a) + (1 / total_b))
    z_value = (p_a - p_b) / math.sqrt(variance)
    p_value = 2 * (1 - normal_cdf(abs(z_value)))
    return z_value, p_value


def normal_cdf(z_value: float) -> float:
    return 0.5 * (1 + math.erf(z_value / math.sqrt(2)))


def build_summary(rows: list[dict[str, object]]) -> str:
    games_per_player = Counter(row["Player"] for row in rows)
    players = sorted(games_per_player)

    overall_loss_rate = mean(
        1 if row["PlayerResult"] == "lose" else 0 for row in rows
    )
    overall_moves = mean(int(row["NumMoves"]) for row in rows)

    rows_by_player: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in rows:
        rows_by_player[str(row["Player"])].append(row)

    results_after_two_losses: list[int] = []
    moves_after_two_losses: list[int] = []

    preferred_openings: dict[tuple[str, str], str] = {}
    for player in players:
        for color in ("White", "Black"):
            subset = [
                row
                for row in rows_by_player[player]
                if str(row["Color"]) == color
            ]
            if not subset:
                continue
            counts = Counter(str(row["Opening"]).lower() for row in subset)
            preferred_openings[(player, color)] = sorted(
                counts.items(), key=lambda item: (-item[1], item[0])
            )[0][0]

    opening_groups: dict[str, dict[str, list[bool]]] = {
        "White": {"after": [], "normal": []},
        "Black": {"after": [], "normal": []},
    }

    for player in players:
        player_rows = rows_by_player[player]
        loss_binary = [1 if row["PlayerResult"] == "lose" else 0 for row in player_rows]

        for index, row in enumerate(player_rows):
            color = str(row["Color"])
            is_after = index >= 2 and loss_binary[index - 1] == 1 and loss_binary[index - 2] == 1
            played_preferred = (
                str(row["Opening"]).lower() == preferred_openings[(player, color)]
            )
            group = "after" if is_after else "normal"
            opening_groups[color][group].append(played_preferred)

            if is_after:
                results_after_two_losses.append(loss_binary[index])
                moves_after_two_losses.append(int(row["NumMoves"]))

    after_two_loss_rate = mean(results_after_two_losses)
    after_two_moves = mean(moves_after_two_losses)

    white_z, white_p = proportion_test(
        sum(opening_groups["White"]["after"]),
        len(opening_groups["White"]["after"]),
        sum(opening_groups["White"]["normal"]),
        len(opening_groups["White"]["normal"]),
    )
    black_z, black_p = proportion_test(
        sum(opening_groups["Black"]["after"]),
        len(opening_groups["Black"]["after"]),
        sum(opening_groups["Black"]["normal"]),
        len(opening_groups["Black"]["normal"]),
    )

    top_openings = Counter(str(row["Opening"]).lower() for row in rows).most_common(5)
    result_counts = Counter(str(row["PlayerResult"]) for row in rows)

    lines = [
        "# Public Summary",
        "",
        "This file is generated from the anonymized public dataset.",
        "",
        "## Dataset snapshot",
        "",
        f"- Games: {len(rows)}",
        f"- Players: {len(players)}",
        f"- Average games per player: {mean(games_per_player.values()):.2f}",
        f"- Median games per player: {median(games_per_player.values()):.2f}",
        "",
        "## Results distribution",
        "",
        f"- Wins: {result_counts['win']}",
        f"- Losses: {result_counts['lose']}",
        f"- Draws: {result_counts['draw']}",
        f"- Overall loss rate: {overall_loss_rate:.3f}",
        "",
        "## Main public checks",
        "",
        f"- Loss rate after two consecutive losses: {after_two_loss_rate:.3f} (n = {len(results_after_two_losses)})",
        f"- Average moves in all games: {overall_moves:.2f}",
        f"- Average moves after two consecutive losses: {after_two_moves:.2f}",
        "",
        "## Preferred opening comparison",
        "",
        (
            f"- White: after = {mean(opening_groups['White']['after']):.3f}, "
            f"normal = {mean(opening_groups['White']['normal']):.3f}, "
            f"z = {white_z:.3f}, p = {white_p:.3f}"
        ),
        (
            f"- Black: after = {mean(opening_groups['Black']['after']):.3f}, "
            f"normal = {mean(opening_groups['Black']['normal']):.3f}, "
            f"z = {black_z:.3f}, p = {black_p:.3f}"
        ),
        "",
        "## Top 5 openings",
        "",
    ]

    for opening_name, opening_count in top_openings:
        lines.append(f"- {opening_name}: {opening_count}")

    lines.append("")
    return "\n".join(lines)


def main() -> None:
    rows = load_rows()
    SUMMARY_MD.write_text(build_summary(rows), encoding="utf-8")
    print(f"Wrote {SUMMARY_MD}")


if __name__ == "__main__":
    main()
