## Preamble

Playground for programs using [Google OR-Tools](https://developers.google.com/optimization/). Python-focused for now.

## Installation
```
pip install pipenv
pipenv install --dev
```

## Test
```
pipenv run pytest
```

## Examples - Hearthstone HoF Dust
### Context
[Hearthstone](https://playhearthstone.com/en-us/) is a popular online card game by Blizzard Entertainment with over [100 million players](https://variety.com/2018/gaming/news/hearthstone-has-over-100-million-players-1203019919/).

One of the key currencies of the game's economy is dust, which can be used for crafting collectible cards. One usually earns dust by playing the game and completing quests.

Other dust events include a semi-frequent event when cards are moved to Hall Of Fame (HoF). When that occurs, players get dust for what they already have in their card collection. Players can choose to craft from/invest in a variety of cards to earn extra dust.

## Problem
This is a classic optimization/investment problem, with quite a number of interesting constraints. While there are some simple heuristics out there (such as [craft the highest gold cards you can afford](https://www.reddit.com/r/wildhearthstone/comments/avta57/hall_of_fame_craftdust_guide/), they are sub-optimal, especially in cases with limited budget.

The goal here is to maximize investment (dust) returns.

## Usage
See `example.py` and tests. The current setup is based off the Year of the Dragon event, where a large number of cards are moving which makes the problem especially interesting.

