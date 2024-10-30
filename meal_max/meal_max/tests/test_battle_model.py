import unittest
from unittest.mock import patch, MagicMock
from meal_max.models.battle_model import BattleModel
from meal_max.models.kitchen_model import Meal


class TestBattleModel(unittest.TestCase):

    def setUp(self):
        self.battle_model = BattleModel()

    def test_init(self):
        self.assertEqual(self.battle_model.combatants, [])

    def test_prep_combatant(self):
        meal = Meal(id=1, meal="Pizza", cuisine="Italian", price=10.0, difficulty="MED")
        self.battle_model.prep_combatant(meal)
        self.assertEqual(len(self.battle_model.combatants), 1)
        self.assertEqual(self.battle_model.combatants[0], meal)

    def test_prep_combatant_full_list(self):
        meal1 = Meal(id=1, meal="Pizza", cuisine="Italian", price=10.0, difficulty="MED")
        meal2 = Meal(id=2, meal="Sushi", cuisine="Japanese", price=15.0, difficulty="HIGH")
        self.battle_model.prep_combatant(meal1)
        self.battle_model.prep_combatant(meal2)
        with self.assertRaises(ValueError):
            self.battle_model.prep_combatant(Meal(id=3, meal="Burger", cuisine="American", price=8.0, difficulty="LOW"))

    @patch("meal_max.utils.random_utils.get_random", return_value=0.5)
    @patch("meal_max.models.kitchen_model.update_meal_stats")
    def test_battle(self, mock_update_stats, mock_random):
        meal1 = Meal(id=1, meal="Pizza", cuisine="Italian", price=10.0, difficulty="MED")
        meal2 = Meal(id=2, meal="Sushi", cuisine="Japanese", price=15.0, difficulty="HIGH")
        self.battle_model.prep_combatant(meal1)
        self.battle_model.prep_combatant(meal2)
        
        winner_meal = self.battle_model.battle()
        
        self.assertIn(winner_meal, [meal1.meal, meal2.meal])
        mock_update_stats.assert_any_call(meal1.id, 'win')
        mock_update_stats.assert_any_call(meal2.id, 'loss')

    def test_battle_not_enough_combatants(self):
        with self.assertRaises(ValueError):
            self.battle_model.battle()

    def test_clear_combatants(self):
        meal = Meal(id=1, meal="Pizza", cuisine="Italian", price=10.0, difficulty="MED")
        self.battle_model.prep_combatant(meal)
        self.battle_model.clear_combatants()
        self.assertEqual(self.battle_model.combatants, [])

    def test_get_battle_score(self):
        meal = Meal(id=1, meal="Pizza", cuisine="Italian", price=10.0, difficulty="LOW")
        score = self.battle_model.get_battle_score(meal)
        expected_score = (meal.price * len(meal.cuisine)) - 3          self.assertEqual(score, expected_score)


if __name__ == "__main__":
    unittest.main()

