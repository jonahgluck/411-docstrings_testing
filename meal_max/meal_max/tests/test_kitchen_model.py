import unittest
from unittest.mock import patch, MagicMock
from meal_max.models.kitchen_model import Meal, create_meal, delete_meal, get_meal_by_id, get_meal_by_name, update_meal_stats, get_leaderboard


class TestKitchenModel(unittest.TestCase):

    def test_meal_initialization(self):
        meal = Meal(id=1, meal="Pizza", cuisine="Italian", price=10.0, difficulty="MED")
        self.assertEqual(meal.meal, "Pizza")
        self.assertEqual(meal.price, 10.0)

    def test_meal_invalid_price(self):
        with self.assertRaises(ValueError):
            Meal(id=1, meal="Pizza", cuisine="Italian", price=-5.0, difficulty="MED")

    def test_meal_invalid_difficulty(self):
        with self.assertRaises(ValueError):
            Meal(id=1, meal="Pizza", cuisine="Italian", price=10.0, difficulty="INVALID")

    @patch("meal_max.utils.sql_utils.get_db_connection")
    def test_create_meal(self, mock_get_db_connection):
        mock_conn = MagicMock()
        mock_get_db_connection.return_value = mock_conn
        create_meal("Pizza", "Italian", 10.0, "MED")
        mock_conn.commit.assert_called_once()

    @patch("meal_max.utils.sql_utils.get_db_connection")
    def test_create_meal_duplicate_error(self, mock_get_db_connection):
        mock_conn = MagicMock()
        mock_get_db_connection.return_value = mock_conn
        mock_conn.cursor.return_value.execute.side_effect = sqlite3.IntegrityError
        with self.assertRaises(ValueError):
            create_meal("Pizza", "Italian", 10.0, "MED")

    @patch("meal_max.utils.sql_utils.get_db_connection")
    def test_delete_meal(self, mock_get_db_connection):
        mock_conn = MagicMock()
        mock_get_db_connection.return_value = mock_conn
        delete_meal(1)
        mock_conn.commit.assert_called_once()

    @patch("meal_max.utils.sql_utils.get_db_connection")
    def test_get_leaderboard(self, mock_get_db_connection):
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_get_db_connection.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.fetchall.return_value = [(1, "Pizza", "Italian", 10.0, "MED", 5, 3, 60.0)]
        leaderboard = get_leaderboard()
        self.assertEqual(len(leaderboard), 1)
        self.assertEqual(leaderboard[0]['meal'], "Pizza")

    @patch("meal_max.utils.sql_utils.get_db_connection")
    def test_update_meal_stats(self, mock_get_db_connection):
        mock_conn = MagicMock()
        mock_get_db_connection.return_value = mock_conn
        update_meal_stats(1, 'win')
        mock_conn.commit.assert_called_once()


if __name__ == "__main__":
    unittest.main()

