import unittest
from unittest.mock import patch
from meal_max.utils.random_utils import get_random


class TestRandomUtils(unittest.TestCase):

    @patch("meal_max.utils.random_utils.requests.get")
    def test_get_random_success(self, mock_get):
        mock_response = mock_get.return_value
        mock_response.status_code = 200
        mock_response.text = "0.42\n"
        
        random_number = get_random()
        self.assertEqual(random_number, 0.42)

    @patch("meal_max.utils.random_utils.requests.get")
    def test_get_random_invalid_response(self, mock_get):
        mock_response = mock_get.return_value
        mock_response.status_code = 200
        mock_response.text = "invalid_number\n"
        
        with self.assertRaises(ValueError):
            get_random()

    @patch("meal_max.utils.random_utils.requests.get")
    def test_get_random_timeout(self, mock_get):
        mock_get.side_effect = requests.exceptions.Timeout
        with self.assertRaises(RuntimeError):
            get_random()

    @patch("meal_max.utils.random_utils.requests.get")
    def test_get_random_request_error(self, mock_get):
        mock_get.side_effect = requests.exceptions.RequestException("Error")
        with self.assertRaises(RuntimeError):
            get_random()


if __name__ == "__main__":
    unittest.main()

