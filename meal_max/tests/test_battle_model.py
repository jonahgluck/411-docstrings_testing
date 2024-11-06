import pytest
from unittest.mock import patch, MagicMock
from meal_max.models.battle_model import BattleModel
from meal_max.models.kitchen_model import Meal


@pytest.fixture
def battle_model():
    return BattleModel()


def test_init(battle_model):
    assert battle_model.combatants == []


def test_prep_combatant(battle_model):
    meal = Meal(id=1, meal="Pizza", cuisine="Italian", price=10.0, difficulty="MED")
    battle_model.prep_combatant(meal)
    assert len(battle_model.combatants) == 1
    assert battle_model.combatants[0] == meal


def test_prep_combatant_full_list(battle_model):
    meal1 = Meal(id=1, meal="Pizza", cuisine="Italian", price=10.0, difficulty="MED")
    meal2 = Meal(id=2, meal="Sushi", cuisine="Japanese", price=15.0, difficulty="HIGH")
    battle_model.prep_combatant(meal1)
    battle_model.prep_combatant(meal2)
    with pytest.raises(ValueError):
        battle_model.prep_combatant(Meal(id=3, meal="Burger", cuisine="American", price=8.0, difficulty="LOW"))


@patch("meal_max.utils.random_utils.get_random", return_value=0.5)
@patch("meal_max.models.kitchen_model.update_meal_stats")
def test_battle(mock_update_stats, mock_random, battle_model):
    meal1 = Meal(id=1, meal="Pizza", cuisine="Italian", price=10.0, difficulty="MED")
    meal2 = Meal(id=2, meal="Sushi", cuisine="Japanese", price=15.0, difficulty="HIGH")
    battle_model.prep_combatant(meal1)
    battle_model.prep_combatant(meal2)
    
    winner_meal = battle_model.battle()
    
    assert winner_meal in [meal1.meal, meal2.meal]
    mock_update_stats.assert_any_call(meal1.id, 'win')
    mock_update_stats.assert_any_call(meal2.id, 'loss')


def test_battle_not_enough_combatants(battle_model):
    with pytest.raises(ValueError):
        battle_model.battle()


def test_clear_combatants(battle_model):
    meal = Meal(id=1, meal="Pizza", cuisine="Italian", price=10.0, difficulty="MED")
    battle_model.prep_combatant(meal)
    battle_model.clear_combatants()
    assert battle_model.combatants == []


def test_get_battle_score(battle_model):
    meal = Meal(id=1, meal="Pizza", cuisine="Italian", price=10.0, difficulty="LOW")
    score = battle_model.get_battle_score(meal)
    expected_score = (meal.price * len(meal.cuisine)) - 3
    assert score == expected_score

