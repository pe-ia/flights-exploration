import time
import argparse
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


def main() -> None:
    """
    Main function to initiate flight search and scraping using command-line arguments.
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

        departing_flight_data, returning_flight_data = search_and_scrape_flights(
            page, args.from_city, args.to_city, args.departure_date, args.return_date, args.delay
        )

        # Output the flight details
        print("Flights:")
        for index in range(len(departing_flight_data)):
            print("\nDeparting flight:")
            print(departing_flight_data[index])
            print("Returning flights: ")
            for flight in returning_flight_data[index]:
                print(flight)

        page.close()


if __name__ == '__main__':
    main()
