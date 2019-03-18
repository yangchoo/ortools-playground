# Simple Sanity Checks
from sat_examples.hearthstone_hof_dust import solve, CRAFT_COST, DECRAFT_COST
from itertools import permutations

import pytest


@pytest.fixture
def single_common():
    return {"naturalize": "common"}


@pytest.fixture
def full_set():
    return {"naturalize": "common", "doomguard": "rare"}


class TestSingleRarity(object):
    @staticmethod
    def test_no_invest(single_common):
        budget = 10
        for p1, p2 in permutations([0, 1, 2], 2):
            cards_in_collection = {"naturalize": {"standard": p1, "golden": p2}}

            solution = solve(budget, cards_in_collection, single_common)

            assert solution["cards"]["naturalize"]["std"] == dict(
                initial=p1, craft=0, decraft=0, final=p1
            )
            assert solution["cards"]["naturalize"]["gold"] == dict(
                initial=p2, craft=0, decraft=0, final=p2
            )

            assert solution["dust"]["budget"] == budget
            assert solution["dust"]["investment"] == 0

            # Custom checks for bonuses
            if (p1, p2) == (1, 1) or (p1, p2) == (2, 1):
                assert solution["dust"]["objective"] == (
                    budget
                    + CRAFT_COST["common"]
                    + (DECRAFT_COST["common"]) * p1
                    + (CRAFT_COST["common_gold"] + DECRAFT_COST["common_gold"]) * p2
                )
            elif (p1, p2) == (1, 2) or (p1, p2) == (2, 2):
                assert solution["dust"]["objective"] == (
                    budget
                    + (DECRAFT_COST["common"]) * p1
                    + (CRAFT_COST["common_gold"] + DECRAFT_COST["common_gold"]) * p2
                )
            else:
                assert solution["dust"]["objective"] == (
                    budget
                    + (CRAFT_COST["common"] + DECRAFT_COST["common"]) * p1
                    + (CRAFT_COST["common_gold"] + DECRAFT_COST["common_gold"]) * p2
                )

    @staticmethod
    def test_craft_std(single_common):
        budget = 40
        cards_in_collection = {"naturalize": {"standard": 0, "golden": 0}}

        solution = solve(budget, cards_in_collection, single_common)

        assert solution["cards"]["naturalize"]["std"] == dict(
            initial=0, craft=1, decraft=0, final=1
        )
        assert solution["cards"]["naturalize"]["gold"] == dict(
            initial=0, craft=0, decraft=0, final=0
        )
        assert solution["dust"] == dict(
            budget=40, investment=40, objective=45, profit=5
        )

    @staticmethod
    def test_craft_gold(single_common):
        budget = 400
        cards_in_collection = {"naturalize": {"standard": 0, "golden": 0}}

        solution = solve(budget, cards_in_collection, single_common)

        assert solution["cards"]["naturalize"]["std"] == dict(
            initial=0, craft=0, decraft=0, final=0
        )
        assert solution["cards"]["naturalize"]["gold"] == dict(
            initial=0, craft=1, decraft=0, final=1
        )

        assert solution["dust"] == dict(
            budget=400, investment=400, objective=450, profit=50
        )

    @staticmethod
    def test_craft_decraft(single_common):
        budget = 395
        cards_in_collection = {"naturalize": {"standard": 1, "golden": 0}}

        solution = solve(budget, cards_in_collection, single_common)

        assert solution["cards"]["naturalize"]["std"] == dict(
            initial=1, craft=0, decraft=1, final=0
        )
        assert solution["cards"]["naturalize"]["gold"] == dict(
            initial=0, craft=1, decraft=0, final=1
        )
        assert solution["dust"] == dict(
            budget=395, investment=395, objective=450, profit=55
        )


class TestMultipleRarity(object):
    @staticmethod
    def test_no_invest(full_set):
        budget = 10
        cards_in_collection = {
            "naturalize": {"standard": 1, "golden": 0},
            "doomguard": {"standard": 1, "golden": 0},
        }

        solution = solve(budget, cards_in_collection, full_set)

        assert solution["cards"]["naturalize"]["std"] == dict(
            initial=1, craft=0, decraft=0, final=1
        )
        assert solution["cards"]["naturalize"]["gold"] == dict(
            initial=0, craft=0, decraft=0, final=0
        )
        assert solution["cards"]["doomguard"]["std"] == dict(
            initial=1, craft=0, decraft=0, final=1
        )
        assert solution["cards"]["doomguard"]["gold"] == dict(
            initial=0, craft=0, decraft=0, final=0
        )
        assert solution["dust"] == dict(
            budget=10, investment=0, objective=175, profit=165
        )

    @staticmethod
    def test_craft_rare(full_set):
        budget = 100
        cards_in_collection = {
            "naturalize": {"standard": 0, "golden": 0},
            "doomguard": {"standard": 1, "golden": 0},
        }

        solution = solve(budget, cards_in_collection, full_set)

        assert solution["cards"]["naturalize"]["std"] == dict(
            initial=0, craft=0, decraft=0, final=0
        )
        assert solution["cards"]["naturalize"]["gold"] == dict(
            initial=0, craft=0, decraft=0, final=0
        )
        assert solution["cards"]["doomguard"]["std"] == dict(
            initial=1, craft=1, decraft=0, final=2
        )
        assert solution["cards"]["doomguard"]["gold"] == dict(
            initial=0, craft=0, decraft=0, final=0
        )
        assert solution["dust"] == dict(
            budget=100, investment=100, objective=240, profit=140
        )


#
# def test_invariants():
