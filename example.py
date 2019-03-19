#!/usr/bin/env python3

import json

# Hearthstone HOF Dust
from sat_examples.hearthstone_hof_dust import solve as hearth_solve

budget = 3000
cards_in_collection = {
    "naturalize": {"standard": 2, "golden": 1},
    "doomguard": {"standard": 1, "golden": 2},
    "divine favor": {"standard": 2, "golden": 0},
    "murkspark eel": {"standard": 2, "golden": 0},
    "gloom stag": {"standard": 1, "golden": 0},
    "glitter moth": {"standard": 1, "golden": 0},
    "baku the mooneater": {"standard": 1, "golden": 0},
    "genn greymane": {"standard": 0, "golden": 0}
}
card_rarity = {
    "naturalize": "common",
    "doomguard": "rare",
    "divine favor": "rare",
    "murkspark eel": "rare",
    "gloom stag": "epic",
    "glitter moth": "epic",
    "baku the mooneater": "legendary",
    "genn greymane": "legendary"
}

solution = hearth_solve(budget, cards_in_collection, card_rarity)

# Parse out cards to craft/de-craft
for card_name, card_counts in solution["cards"].items():
    for i in ("std", "gold"):
        print(f"{card_name}_{i}: Craft {card_counts[i]['craft']}, De-craft {card_counts[i]['decraft']}")

print(solution["dust"])
# print(json.dumps(solution, indent=2))
