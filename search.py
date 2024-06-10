import time
import argparse

from playwright.sync_api import sync_playwright, Page


def wait(duration: float = 1.0) -> None:
    """Waits for a specified duration in seconds."""
    time.sleep(duration)


def wait_for_element(page: Page, selector: str) -> None:
    """Waits for a specific element to be visible on the page."""
    page.wait_for_selector(selector, state="visible")


def handle_consent(page: Page, delay: float) -> None:
    """
    Handles the Google consent screen if it appears.

    Args:
        page (Page): The current page instance.
        delay (float): The delay duration between actions in seconds.
    """
    if "consent.google.com" in page.url:
        consent_button = page.query_selector('.lssxud')
        if consent_button:
            consent_button.click()
            wait(delay)


def search_flights(page: Page, from_city: str, to_city: str, departure_date: str, return_date: str,
                   delay: float) -> Page:
    """
    Searches for flights on Google Flights.

    Args:
        page (Page): The flights search page.
        from_city (str): The departure city.
        to_city (str): The destination city.
        departure_date (str): The departure date in MM-DD-YYYY format.
        return_date (str): The return date in MM-DD-YYYY format.
        delay (float): The delay duration between actions in seconds.
    """

    # Enter departure city
    from_field = page.query_selector_all('.e5F5td')[0]
    from_field.click()
    wait(delay)
    from_field.type(from_city)
    wait(delay)
    page.keyboard.press('Enter')

    # Enter destination city
    to_field = page.query_selector_all('.e5F5td')[1]
    to_field.click()
    wait(delay)
    to_field.type(to_city)
    wait(delay)
    page.keyboard.press('Enter')

    # Enter departure date
    departure_field = page.query_selector_all('[jscontroller="OKD1oe"] [aria-label="Departure"]')[0]
    departure_field.click()
    wait(delay)
    departure_field.type(departure_date)
    wait(delay)
    page.query_selector('.WXaAwc .VfPpkd-LgbsSe').click()
    wait(delay)

    # Enter return date
    return_field = page.query_selector_all('[jscontroller="ViZxZe"] [aria-label="Return"]')[0]
    return_field.click()
    wait(delay)
    return_field.type(return_date)
    wait(delay)
    page.query_selector('.WXaAwc .VfPpkd-LgbsSe').click()
    wait(delay)

    # Perform the flight search
    page.query_selector('.MXvFbd .VfPpkd-LgbsSe').click()
    wait_for_element(page, '.zISZ5c button')  # Wait for the results page to load

    # Expand the results
    page.query_selector('.zISZ5c button').click()

    return page


def main() -> None:
    """
    Main function to initiate flight search using command-line arguments.
    """
    parser = argparse.ArgumentParser(description='Search for flights on Google Flights.')
    parser.add_argument('from_city', type=str, help='The departure city.')
    parser.add_argument('to_city', type=str, help='The destination city.')
    parser.add_argument('departure_date', type=str, help='The departure date in MM-DD-YYYY format.')
    parser.add_argument('return_date', type=str, help='The return date in MM-DD-YYYY format.')
    parser.add_argument('--delay', type=float, default=1.0, help='The delay duration between actions in seconds.')

    args = parser.parse_args()

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=False)
        page = browser.new_page()
        page.goto('https://www.google.com/travel/flights?hl=en-US&curr=USD')

        handle_consent(page, args.delay)

        page = search_flights(page, args.from_city, args.to_city, args.departure_date, args.return_date, args.delay)
        time.sleep(10)
        page.close()


if __name__ == '__main__':
    main()
