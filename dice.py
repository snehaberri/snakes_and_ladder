import random


def roll_dice() -> int:
    """Simulate one six-sided dice roll for the main game."""
    return random.randint(1, 6)


def dice() -> int:
    """Backward-compatible name for the dice simulation."""
    return roll_dice()
