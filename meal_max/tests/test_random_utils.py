import pytest
from unittest.mock import patch
from meal_max.utils.random_utils import get_random
import requests


@patch("meal_max.utils.random_utils.requests.get")
def test_get_random_success(mock_get):
    mock_response = mock_get.return_value
    mock_response.status_code = 200
    mock_response.text = "0.42\n"
    
    random_number = get_random()
    assert random_number == 0.42


@patch("meal_max.utils.random_utils.requests.get")
def test_get_random_invalid_response(mock_get):
    mock_response = mock_get.return_value
    mock_response.status_code = 200
    mock_response.text = "invalid_number\n"
    
    with pytest.raises(ValueError):
        get_random()


@patch("meal_max.utils.random_utils.requests.get")
def test_get_random_timeout(mock_get):
    mock_get.side_effect = requests.exceptions.Timeout
    with pytest.raises(RuntimeError):
        get_random()


@patch("meal_max.utils.random_utils.requests.get")
def test_get_random_request_error(mock_get):
    mock_get.side_effect = requests.exceptions.RequestException("Error")
    with pytest.raises(RuntimeError):
        get_random()

