import logging
import requests

from meal_max.utils.logger import configure_logger

logger = logging.getLogger(__name__)
configure_logger(logger)


def get_random() -> float:
    url = "https://www.random.org/decimal-fractions/?num=1&dec=2&col=1&format=plain&rnd=new"

""" Retrieves a random decimal number from random.org
    Sends a GET request to the random.org API to obtain a random decimal fraction. 
    Logs the process and handles any errors that may occur, raising an exception if the 
    request fails or if the response cannot be parsed to a float.

    Returns: 
        float: a random decimal number provided by random.org
    Raises:
        ValueError: Raised if the response from random.org is not a valid float.
        RuntimeError: Raised if the request times out or fails due to a connection issue.
    Ex:
        >>> random_value = get_random()
        >>> print(f"Random value: {random_value}"
"""
    
    try:
        # Log the request to random.org
        logger.info("Fetching random number from %s", url)

        response = requests.get(url, timeout=5)

        # Check if the request was successful
        response.raise_for_status()

        random_number_str = response.text.strip()

        try:
            random_number = float(random_number_str)
        except ValueError:
            raise ValueError("Invalid response from random.org: %s" % random_number_str)

        logger.info("Received random number: %.3f", random_number)
        return random_number

    except requests.exceptions.Timeout:
        logger.error("Request to random.org timed out.")
        raise RuntimeError("Request to random.org timed out.")

    except requests.exceptions.RequestException as e:
        logger.error("Request to random.org failed: %s", e)
        raise RuntimeError("Request to random.org failed: %s" % e)
