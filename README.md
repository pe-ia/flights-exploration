# Flight Scraper with Playwright

This script is a simple flight search scraper using Playwright to interact with Google Flights. It allows you to search for flight details like departure time, airline, duration, and price by providing input directly through the console, without needing to reinstantiate the Playwright page for each search.

## Why Console Instead of Argparse?

Originally, we planned to use `argparse` for command-line input; however, we opted to use console input instead to allow multiple flight searches without needing to reinitialize the Playwright page. This makes it more efficient for multiple queries in a single session.

## Disclaimer

This project is intended as a learning exercise to practice web scraping with Playwright. We **did not perform any mass scraping** with this code. Using this script manually for personal flight searches should be fine, but **adapting this for mass scraping violates Google's Terms of Service** and is strictly discouraged. If you are considering modifying this code for large-scale scraping, **do not** proceed as it could result in your IP being blocked or other consequences.

## How to Use

1. Install dependencies:

   `pip install -r requirements.txt`

2. Run the script:

   `python flight_scraper.py`

3. Once running, provide the following details in the console when prompted:

   `<from> <to> <departure_date> [return_date]`

   Example: `CDG JFK 10-10-2024 11-11-2024`

   The `return_date` is optional for one-way trips.

4. To exit, type `exit`.

### Input Format

- `<from>`: Departure city or airport code (e.g., `ORY`).
- `<to>`: Destination city or airport code (e.g., `EWR`).
- `<departure_date>`: Date of departure in `DD-MM-YYYY` format.
- `[return_date]`: (Optional) Date of return in `DD-MM-YYYY` format for round-trip flights.
