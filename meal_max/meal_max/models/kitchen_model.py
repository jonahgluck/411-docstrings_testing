from dataclasses import dataclass
import logging
import sqlite3
from typing import Any

from meal_max.utils.sql_utils import get_db_connection
from meal_max.utils.logger import configure_logger


logger = logging.getLogger(__name__)
configure_logger(logger)


@dataclass
class Meal:
    """ This class represents a meal with specific attributes and validation rules.
    
    The attributes are: 
        id (int): Unique ID of the meal.
        meal (str): The meal's name.
        cuisine (str): The type of cuisine for the meal.
        price (float): The cost of the meal, which has to be positive.
        difficulty (str): Preparation difficulty level, expected to be 'LOW', 'MED', or 'HIGH'.
        
    Raises:
        ValueError: If 'price' is neative or 'difficulty' is not one of the valid levels.
    """
    id: int
    meal: str
    cuisine: str
    price: float
    difficulty: str

    def __post_init__(self):
        """ Checks for valid 'price' and 'difficulty' values after initialization.

        Raises:
            ValueError: If 'price' is less than 0 or 'difficulty' is not one of the valid levels.
        """
        if self.price < 0:
            raise ValueError("Price must be a positive value.")
        if self.difficulty not in ['LOW', 'MED', 'HIGH']:
            raise ValueError("Difficulty must be 'LOW', 'MED', or 'HIGH'.")


def create_meal(meal: str, cuisine: str, price: float, difficulty: str) -> None:
    """ Adds a new meal entry to the database.

    Args: 
        meal (str): The meal's name.
        cuisine (str): The type of cuisine for the meal.
        price (float): The cost of the meal, which has to be positive.
        difficulty (str): Preparation difficulty level, expected to be 'LOW', 'MED', or 'HIGH'.

    Raises:
        ValueError: If 'price' is less than 0 or 'difficulty' is not one of the valid levels.
        sqlite3.IntegrityError: If a meal with the same name already exists.
        sqlite3.Error: For any general database-related error.  
    """
    if not isinstance(price, (int, float)) or price <= 0:
        raise ValueError(f"Invalid price: {price}. Price must be a positive number.")
    if difficulty not in ['LOW', 'MED', 'HIGH']:
        raise ValueError(f"Invalid difficulty level: {difficulty}. Must be 'LOW', 'MED', or 'HIGH'.")

    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO meals (meal, cuisine, price, difficulty)
                VALUES (?, ?, ?, ?)
            """, (meal, cuisine, price, difficulty))
            conn.commit()

            logger.info("Meal successfully added to the database: %s", meal)

    except sqlite3.IntegrityError:
        logger.error("Duplicate meal name: %s", meal)
        raise ValueError(f"Meal with name '{meal}' already exists")

    except sqlite3.Error as e:
        logger.error("Database error: %s", str(e))
        raise e


def delete_meal(meal_id: int) -> None:
    """ Marks a meal as deleted in the database by setting its status.

        Args: 
            meal_id (int): The ID of the meal that needs to be deleted.

        Raises:
            ValueError: If the meal doesn't exist or is already marked as deleted.
            sqlite3.Error: For any general database-related error.
    """
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT deleted FROM meals WHERE id = ?", (meal_id,))
            try:
                deleted = cursor.fetchone()[0]
                if deleted:
                    logger.info("Meal with ID %s has already been deleted", meal_id)
                    raise ValueError(f"Meal with ID {meal_id} has been deleted")
            except TypeError:
                logger.info("Meal with ID %s not found", meal_id)
                raise ValueError(f"Meal with ID {meal_id} not found")

            cursor.execute("UPDATE meals SET deleted = TRUE WHERE id = ?", (meal_id,))
            conn.commit()

            logger.info("Meal with ID %s marked as deleted.", meal_id)

    except sqlite3.Error as e:
        logger.error("Database error: %s", str(e))
        raise e

def get_leaderboard(sort_by: str="wins") -> dict[str, Any]:
    """ Retrieves a sorted leaderboard of meals based on either wins or win percentage.

        Args:
            sort_by (str, optional): Specifies the sorting criterion ('wins' or 'win_pct').
                Defaults to 'wins'. 

        Returns:
            List[dict]: A list of dictionaries representing meals on the leaderboard.

        Raises:
            ValueError: If 'sort_by' is neither 'wins' nor 'win_pct'. 
            sqlite3.Error: For any general database-related error.  
    """
    query = """
        SELECT id, meal, cuisine, price, difficulty, battles, wins, (wins * 1.0 / battles) AS win_pct
        FROM meals WHERE deleted = false AND battles > 0
    """

    if sort_by == "win_pct":
        query += " ORDER BY win_pct DESC"
    elif sort_by == "wins":
        query += " ORDER BY wins DESC"
    else:
        logger.error("Invalid sort_by parameter: %s", sort_by)
        raise ValueError("Invalid sort_by parameter: %s" % sort_by)

    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query)
            rows = cursor.fetchall()

        leaderboard = []
        for row in rows:
            meal = {
                'id': row[0],
                'meal': row[1],
                'cuisine': row[2],
                'price': row[3],
                'difficulty': row[4],
                'battles': row[5],
                'wins': row[6],
                'win_pct': round(row[7] * 100, 1)  # Convert to percentage
            }
            leaderboard.append(meal)

        logger.info("Leaderboard retrieved successfully")
        return leaderboard

    except sqlite3.Error as e:
        logger.error("Database error: %s", str(e))
        raise e

def get_meal_by_id(meal_id: int) -> Meal:
    """ Fetches a meal from the database by its ID. 
        Args: 
            meal_id (int): The ID of the meal to retrieve. 
        Returns:
            Meal: An instance of the Meal class representing the meal.
        Raises:
            ValueError: If the meal is marked as deleted or cannot be found.
            sqlite3.Error: For any general database-related error.
    """
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, meal, cuisine, price, difficulty, deleted FROM meals WHERE id = ?", (meal_id,))
            row = cursor.fetchone()

            if row:
                if row[5]:
                    logger.info("Meal with ID %s has been deleted", meal_id)
                    raise ValueError(f"Meal with ID {meal_id} has been deleted")
                return Meal(id=row[0], meal=row[1], cuisine=row[2], price=row[3], difficulty=row[4])
            else:
                logger.info("Meal with ID %s not found", meal_id)
                raise ValueError(f"Meal with ID {meal_id} not found")

    except sqlite3.Error as e:
        logger.error("Database error: %s", str(e))
        raise e


def get_meal_by_name(meal_name: str) -> Meal:
    """ Fetches a meal from the database by its name. 
        Args: 
            meal_id (int): The name of the meal to retrieve. 
        Returns:
            Meal: An instance of the Meal class representing the meal.
        Raises:
            ValueError: If the meal is marked as deleted or cannot be found.
            sqlite3.Error: For any general database-related error.
    """
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, meal, cuisine, price, difficulty, deleted FROM meals WHERE meal = ?", (meal_name,))
            row = cursor.fetchone()

            if row:
                if row[5]:
                    logger.info("Meal with name %s has been deleted", meal_name)
                    raise ValueError(f"Meal with name {meal_name} has been deleted")
                return Meal(id=row[0], meal=row[1], cuisine=row[2], price=row[3], difficulty=row[4])
            else:
                logger.info("Meal with name %s not found", meal_name)
                raise ValueError(f"Meal with name {meal_name} not found")

    except sqlite3.Error as e:
        logger.error("Database error: %s", str(e))
        raise e


def update_meal_stats(meal_id: int, result: str) -> None:
    """ Updates the battle stats for a meal, incrementing battles or wins.
        Args: 
            meal_id (int): The ID of the meal whose stats are being updated.
            result (str): The result/outcome of the battle, either 'win' or 'loss'. 

        Raises: 
            ValueError: If the meal is marked as deleted or cannot be found, or if 'result' is invalid.
            sqlite3.Error: For any general database-related error. 
    """
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT deleted FROM meals WHERE id = ?", (meal_id,))
            try:
                deleted = cursor.fetchone()[0]
                if deleted:
                    logger.info("Meal with ID %s has been deleted", meal_id)
                    raise ValueError(f"Meal with ID {meal_id} has been deleted")
            except TypeError:
                logger.info("Meal with ID %s not found", meal_id)
                raise ValueError(f"Meal with ID {meal_id} not found")

            if result == 'win':
                cursor.execute("UPDATE meals SET battles = battles + 1, wins = wins + 1 WHERE id = ?", (meal_id,))
            elif result == 'loss':
                cursor.execute("UPDATE meals SET battles = battles + 1 WHERE id = ?", (meal_id,))
            else:
                raise ValueError(f"Invalid result: {result}. Expected 'win' or 'loss'.")

            conn.commit()

    except sqlite3.Error as e:
        logger.error("Database error: %s", str(e))
        raise e
