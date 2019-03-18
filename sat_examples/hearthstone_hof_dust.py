from . import *

from typing import Dict

CRAFT_COST = {
    "common": 40,
    "common_gold": 400,
    "rare": 100,
    "rare_gold": 800,
    "epic": 400,
    "epic_gold": 1600,
    "legendary": 1600,
    "legendary_gold": 3200,
}

DECRAFT_COST = {
    "common": 5,
    "common_gold": 50,
    "rare": 20,
    "rare_gold": 100,
    "epic": 100,
    "epic_gold": 400,
    "legendary": 400,
    "legendary_gold": 1600,
}

# Normalize to max copies
MAX_COPIES = 2


def solve(budget: int, cards_in_collection: Dict, card_rarity: Dict):
    model = cp_model.CpModel()

    cards_present = {
        k: {k2: min(MAX_COPIES, v2) for k2, v2 in v.items()}
        for k, v in cards_in_collection.items()
    }

    # Lookup table for costs, opt_var, etc.
    CARDS = {}

    # Declare vars and constraints
    # Assumption 1: We do not mind de-crafting extra copies if it makes sense
    for name, present in cards_present.items():
        CARDS[name] = {}

        # Standard
        CARDS[name]["std"] = {}
        CARDS[name]["std"]["initial"] = present["standard"]
        CARDS[name]["std"]["profit"] = DECRAFT_COST[card_rarity[name]]
        CARDS[name]["std"]["cost"] = CRAFT_COST[card_rarity[name]]

        # Golden
        gold_name = f"{name}_golden"
        CARDS[name]["gold"] = {}
        CARDS[name]["gold"]["initial"] = present["golden"]
        CARDS[name]["gold"]["profit"] = DECRAFT_COST[f"{card_rarity[name]}_gold"]
        CARDS[name]["gold"]["cost"] = CRAFT_COST[f"{card_rarity[name]}_gold"]

        # Decisions - Craft
        CARDS[name]["std"]["craft"] = model.NewIntVar(0, MAX_COPIES, f"{name}_craft")
        CARDS[name]["gold"]["craft"] = model.NewIntVar(
            0, MAX_COPIES, f"{gold_name}_craft"
        )

        # Decisions - Decraft
        CARDS[name]["std"]["decraft"] = model.NewIntVar(
            0, MAX_COPIES, f"{name}_decraft"
        )
        CARDS[name]["gold"]["decraft"] = model.NewIntVar(
            0, MAX_COPIES, f"{gold_name}_decraft"
        )

        # You cannot decraft what you do not have
        CARDS[name]["std"]["final"] = (
            CARDS[name]["std"]["craft"]
            - CARDS[name]["std"]["decraft"]
            + CARDS[name]["std"]["initial"]
        )
        model.Add(CARDS[name]["std"]["final"] >= 0)

        CARDS[name]["gold"]["final"] = (
            CARDS[name]["gold"]["craft"]
            - CARDS[name]["gold"]["decraft"]
            + CARDS[name]["gold"]["initial"]
        )
        model.Add(CARDS[name]["gold"]["final"] >= 0)

        # Bonus limited to only max of 2 golden or 2 standard
        CARDS[name]["std"]["bonus"] = model.NewIntVar(0, MAX_COPIES, f"{name}_bonus")
        CARDS[name]["gold"]["bonus"] = model.NewIntVar(
            0, MAX_COPIES, f"{gold_name}_bonus"
        )
        model.Add(CARDS[name]["gold"]["bonus"] == CARDS[name]["gold"]["final"])
        model.AddAllowedAssignments(
            [CARDS[name]["std"]["bonus"], CARDS[name]["gold"]["bonus"]],
            [(0, 0), (1, 0), (2, 0), (0, 2), (1, 1), (0, 1)],
        )
        model.Add(CARDS[name]["gold"]["bonus"] <= CARDS[name]["gold"]["final"])
        model.Add(CARDS[name]["std"]["bonus"] <= CARDS[name]["std"]["final"])

    # Card Cost
    card_craft_cost = []
    for card in CARDS.keys():
        for rarity in ("std", "gold"):
            # Cost for crafting beyond what's already present
            card_craft_cost.append(
                f"CARDS['{card}']['{rarity}']['craft'] * CARDS['{card}']['{rarity}']['cost']"
            )
            # Profit for de-crafting
            card_craft_cost.append(
                f"-CARDS['{card}']['{rarity}']['decraft'] * CARDS['{card}']['{rarity}']['profit']"
            )

    total_craft_cost = " + ".join(card_craft_cost)

    model.Add(eval(total_craft_cost + "<= budget"))
    model.Add(eval(total_craft_cost + ">= 0"))

    # Card Profits
    objective = []
    for card in CARDS.keys():
        for rarity in ("std", "gold"):
            objective.append(
                f"CARDS['{card}']['{rarity}']['final'] * "
                f"CARDS['{card}']['{rarity}']['profit']"
            )
            # Bonus profit
            objective.append(
                f"CARDS['{card}']['{rarity}']['bonus'] * "
                f"CARDS['{card}']['{rarity}']['cost']"
            )
            # Profit happens for de-crafting
            objective.append(
                f"CARDS['{card}']['{rarity}']['decraft'] * "
                f"CARDS['{card}']['{rarity}']['profit']"
            )
            # Cost for crafting
            objective.append(
                f"-CARDS['{card}']['{rarity}']['craft'] * "
                f"CARDS['{card}']['{rarity}']['cost']"
            )
    obj_str = " + ".join(objective)

    # Doing nothing preserves budget
    obj_str += " + budget"
    model.Maximize(eval(obj_str))

    solver = cp_model.CpSolver()
    status = solver.Solve(model)

    if status == cp_model.OPTIMAL:
        solution = dict()
        solution["cards"] = {}
        dust_cost = 0
        for card in CARDS.keys():
            solution["cards"][card] = {}
            for card_type in ("std", "gold"):
                card_ref = CARDS[card][card_type]

                solution["cards"][card][card_type] = {}
                sol_ref = solution["cards"][card][card_type]
                sol_ref["initial"] = solver.Value(card_ref["initial"])
                sol_ref["craft"] = solver.Value(card_ref["craft"])
                sol_ref["decraft"] = solver.Value(card_ref["decraft"])
                sol_ref["final"] = solver.Value(card_ref["final"])

                dust_cost += solver.Value(card_ref["craft"]) * card_ref["cost"]
                dust_cost -= solver.Value(card_ref["decraft"]) * card_ref["profit"]

        solution["dust"] = {}
        solution["dust"]["budget"] = budget
        solution["dust"]["investment"] = dust_cost
        solution["dust"]["objective"] = solver.ObjectiveValue()
        solution["dust"]["profit"] = solution["dust"]["objective"] - budget

        # Sanity checks
        assert solution["dust"]["investment"] <= solution["dust"]["budget"]
        assert solution["dust"]["profit"] >= 0

        return solution

    elif status == cp_model.INFEASIBLE:
        raise RuntimeError("Infeasible Model!")
