import pytest
from unittest.mock import patch, MagicMock
from meal_max.models.kitchen_model import Meal, create_meal, delete_meal, get_leaderboard, update_meal_stats


def test_meal_initialization():
    meal = Meal(id=1, meal="Pizza", cuisine="Italian", price=10.0, difficulty="MED")
    assert meal.meal == "Pizza"
    assert meal.price == 10.0


def test_meal_invalid_price():
    with pytest.raises(ValueError):
        Meal(id=1, meal="Pizza", cuisine="Italian", price=-5.0, difficulty="MED")


def test_meal_invalid_difficulty():
    with pytest.raises(ValueError):
        Meal(id=1, meal="Pizza", cuisine="Italian", price=10.0, difficulty="INVALID")


@patch("meal_max.utils.sql_utils.get_db_connection")
def test_create_meal(mock_get_db_connection):
    mock_conn = MagicMock()
    mock_get_db_connection.return_value = mock_conn
    create_meal("Pizza", "Italian", 10.0, "MED")
    mock_conn.commit.assert_called_once()


@patch("meal_max.utils.sql_utils.get_db_connection")
def test_create_meal_duplicate_error(mock_get_db_connection):
    mock_conn = MagicMock()
    mock_get_db_connection.return_value = mock_conn
    mock_conn.cursor.return_value.execute.side_effect = sqlite3.IntegrityError
    with pytest.raises(ValueError):
        create_meal("Pizza", "Italian", 10.0, "MED")


@patch("meal_max.utils.sql_utils.get_db_connection")
def test_delete_meal(mock_get_db_connection):
    mock_conn = MagicMock()
    mock_get_db_connection.return_value = mock_conn
    delete_meal(1)
    mock_conn.commit.assert_called_once()


@patch("meal_max.utils.sql_utils.get_db_connection")
def test_get_leaderboard(mock_get_db_connection):
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_get_db_connection.return_value = mock_conn
    mock_conn.cursor.return_value = mock_cursor
    mock_cursor.fetchall.return_value = [(1, "Pizza", "Italian", 10.0, "MED", 5, 3, 60.0)]
    leaderboard = get_leaderboard()
    assert len(leaderboard) == 1
    assert leaderboard[0]['meal'] == "Pizza"


@patch("meal_max.utils.sql_utils.get_db_connection")
def test_update_meal_stats(mock_get_db_connection):
    mock_conn = MagicMock()
    mock_get_db_connection.return_value = mock_conn
    update_meal_stats(1, 'win')
    mock_conn.commit.assert_called_once()

