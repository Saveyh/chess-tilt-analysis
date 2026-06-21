"""Repair the raw CSV export and publish an anonymized UTF-8 dataset.

The original course export mixes valid CSV rows with rows stored as a single
quoted string. This script repairs those lines, anonymizes player handles, and
writes a clean public dataset that is safe to commit to GitHub.
"""

from __future__ import annotations

import csv
import io
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RAW_CSV = ROOT / "DataBase_Liskamm.csv"
PUBLIC_CSV = ROOT / "data" / "chess_games_public.csv"

EXPECTED_COLUMNS = [
    "Player",
    "Color",
    "Opponent",
    "PlayerElo",
    "OpponentElo",
    "Result",
    "Date",
    "UTCTime",
    "Opening",
    "NumMoves",
]


def repair_rows(path: Path) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []

    with path.open("r", encoding="latin-1", newline="") as handle:
        reader = csv.reader(handle)
        header = next(reader)

        if header != EXPECTED_COLUMNS:
            raise ValueError(f"Unexpected columns: {header!r}")

        for line_number, raw_row in enumerate(reader, start=2):
            if len(raw_row) == len(EXPECTED_COLUMNS):
                repaired_row = raw_row
            elif len(raw_row) == 1:
                repaired_row = next(csv.reader(io.StringIO(raw_row[0])))
            else:
                raise ValueError(
                    f"Line {line_number}: expected 10 columns, got {len(raw_row)}"
                )

            if len(repaired_row) != len(EXPECTED_COLUMNS):
                raise ValueError(
                    f"Line {line_number}: row still malformed after repair: {repaired_row!r}"
                )

            rows.append(dict(zip(EXPECTED_COLUMNS, repaired_row, strict=True)))

    return rows


def anonymize_rows(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    player_names = sorted({row["Player"] for row in rows})
    opponent_names = sorted({row["Opponent"] for row in rows})

    player_map = {
        name: f"player_{index:02d}" for index, name in enumerate(player_names, start=1)
    }
    opponent_map = {
        name: f"opponent_{index:04d}"
        for index, name in enumerate(opponent_names, start=1)
    }

    public_rows: list[dict[str, str]] = []
    for row in rows:
        public_rows.append(
            {
                "Player": player_map[row["Player"]],
                "Color": row["Color"],
                "Opponent": opponent_map[row["Opponent"]],
                "PlayerElo": row["PlayerElo"],
                "OpponentElo": row["OpponentElo"],
                "Result": row["Result"],
                "Date": row["Date"].replace(".", "-"),
                "UTCTime": row["UTCTime"],
                "Opening": row["Opening"].strip(),
                "NumMoves": row["NumMoves"],
            }
        )

    return public_rows


def write_public_csv(rows: list[dict[str, str]], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)

    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=EXPECTED_COLUMNS)
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    repaired_rows = repair_rows(RAW_CSV)
    public_rows = anonymize_rows(repaired_rows)
    write_public_csv(public_rows, PUBLIC_CSV)

    print(f"Repaired rows: {len(repaired_rows)}")
    print(f"Public dataset: {PUBLIC_CSV}")
    print(f"Unique players: {len({row['Player'] for row in public_rows})}")
    print(f"Unique opponents: {len({row['Opponent'] for row in public_rows})}")


if __name__ == "__main__":
    main()
