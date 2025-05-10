from config import Config
from state import StateManager
from scraper import PepperScraper

def main():

    print("Starting the Pepper scraper...")
    config = Config()
    state_manager = StateManager(config.state_file)
    scraper = PepperScraper(config, state_manager)
    scraper.scrape_data()
    print("Scraping completed.")


if __name__ == "__main__":
    main()
