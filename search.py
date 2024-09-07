import time
import argparse
from datetime import datetime
import re
from typing import Optional, Tuple

from playwright.sync_api import sync_playwright, Page, TimeoutError


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


def scrape_flight_details(page: Page, section: str) -> list:
    """
    Scrapes flight details from the current section of the page.

    Args:
        page (Page): The current page instance.
        section (str): The section identifier (e.g., departing or returning).

    Returns:
        list: A list of dictionaries containing flight details.
    """
    flight_details = []
    flights = page.query_selector_all('.pIav2d')  # Generic selector for each flight

    for flight in flights:
        try:
            # Extract elements using the specified selectors
            time_element = flight.query_selector('#mv1WYe')
            airline_element = flight.query_selector('.sSHqwe.tPgKwe.ogfYpf')
            duration_element = flight.query_selector('.gvkrdb.AdWm1c.tPgKwe.ogfYpf')
            price_element = flight.query_selector('.BVAVmf.I11szd.POX3ye')

            # Extract text or set to "N/A" if element is not found
            time = time_element.get_attribute('aria-label') if time_element else "N/A"
            airline = airline_element.inner_text() if airline_element else "N/A"
            duration = duration_element.inner_text() if duration_element else "N/A"
            price = price_element.inner_text() if price_element else "N/A"

            flight_details.append({
                'time': time,
                'airline': airline,
                'duration': duration,
                'price': price,
            })

        except Exception as e:
            print(f"Error scraping {section} flight details: {e}")

    return flight_details


def search_and_scrape_flights(page: Page, from_city: str, to_city: str, departure_date: str, return_date: str,
                              delay: float) -> tuple:
    """
    Searches for flights on Google Flights and scrapes the flight details.

    Args:
        page (Page): The flights search page.
        from_city (str): The departure city.
        to_city (str): The destination city.
        departure_date (str): The departure date in MM-DD-YYYY format.
        return_date (str): The return date in MM-DD-YYYY format.
        delay (float): The delay duration between actions in seconds.

    Returns:
        tuple: Two lists containing departing and returning flight details.
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
    wait_for_element(page, '[jsname="Ud7fr"]')  # Wait for the Top Departing Flights section to load

    # Scrape departing flights details
    departing_flight_data = scrape_flight_details(page, "departing")

    # Iterate over each departing flight
    departing_flights = page.query_selector_all('.pIav2d')  # Selector for each departing flight
    returning_flight_data = []

    for index in range(len(departing_flights)):
        departing_flights = page.query_selector_all('.pIav2d')
        try:
            departing_flights[index].click()  # Click on each departing flight
            wait_for_element(page, '[jsname="Ud7fr"]')  # Wait for the Top Returning Flights section to load

            # Scrape returning flights details without clicking
            returning_flight_data.append(scrape_flight_details(page, "returning"))

            # Click the button to go to the next departing flight
            next_button = page.query_selector('.pkGNSd')
            if next_button:
                next_button.click()
                wait(delay)
        except TimeoutError as e:
            print(f"Timeout error while clicking: {e}")
        except Exception as e:
            print(f"Error during clicking departing flight: {e}")

    return departing_flight_data, returning_flight_data


def parse_query(query: str) -> Optional[Tuple[str, str, str, Optional[str]]]:
    """
    Parses a query string to extract departure and return flight details.

    Args:
        query (str): The input string in the format "<from> <to> <departure_date> [return_date]".

    Returns:
        Optional[Tuple[str, str, str, Optional[str]]]: A tuple containing from_city, to_city, departure_date,
        and optionally return_date. Returns None if the input format is invalid or dates are in the wrong format.
    """
    # Regex pattern to match the query format
    pattern = r"(\w+) (\w+) (\d{2}-\d{2}-\d{4})(?: (\d{2}-\d{2}-\d{4}))?"
    match = re.match(pattern, query)

    if not match:
        return None

    from_city: str = match.group(1)
    to_city: str = match.group(2)
    departure_date: str = match.group(3)
    return_date: Optional[str] = match.group(4) if match.group(4) else None

    # Validate date format
    try:
        datetime.strptime(departure_date, '%d-%m-%Y')
        if return_date:
            datetime.strptime(return_date, '%d-%m-%Y')
    except ValueError:
        return None

    return from_city, to_city, departure_date, return_date

def main() -> None:
    """
    Main function to initiate flight search and scraping using command-line input.
    """
    parser = argparse.ArgumentParser(description='Search for flights on Google Flights. Type exit to exit.')
    parser.add_argument('--delay', type=float, default=1.0, help='The delay duration between actions in seconds.')

    args = parser.parse_args()

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=False)
        page = browser.new_page()
        page.goto('https://www.google.com/travel/flights?hl=en-US&curr=USD')

        handle_consent(page, args.delay)

        while True:
            query = input("<from> <to> <departure_date> [return_date] > ")

            if query == "exit":
                break

            parsed_query = parse_query(query)

            if parsed_query:
                # TODO: Only search one-way flights if no return date
                from_city, to_city, departure_date, return_date = parsed_query
                departing_flight_data, returning_flight_data = search_and_scrape_flights(
                    page, from_city, to_city, departure_date, return_date, args.delay
                )
            else:
                print(
                    "Invalid query format. Please use <from> <to> <departure_date> [return_date]. Date should be in "
                    "DD-MM-YYYY format.")

            # Output the flight details
            print("Flights:")
            for index in range(len(departing_flight_data)):
                print("\nDeparting flight:")
                print(departing_flight_data[index])
                # TODO: Skip if no return date
                print("Returning flights: ")
                for flight in returning_flight_data[index]:
                    print(flight)

            # TODO: Click "Flights" button instead to avoid refresh - google flights is single-page
            page.goto('https://www.google.com/travel/flights?hl=en-US&curr=USD')

        page.close()


if __name__ == '__main__':
    main()
