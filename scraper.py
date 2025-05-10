import time
import os
import json
import re
from pathlib import Path
from config import Config
from state import StateManager
from save_data import DataSaver
from playwright.sync_api import sync_playwright
from urllib.parse import urljoin


class PepperScraper:
    def __init__(self, config=None, state_manager=None):
        self.config = config or Config()
        self.state_manager = state_manager or StateManager(self.config.state_file)

    def get_saved_deals(self, page):
        """Collects links and titles of saved deals."""
        page.goto(self.config.saved_deals_page)
        print("Navigated to saved deals page.")
        time.sleep(4)

        saved_deals = {}
        strong_elements = page.locator('strong.thread-title')
        div_parent = strong_elements.locator('xpath=..')
        for i in range(strong_elements.count()):
            div = div_parent.nth(i)
            first_a = div.locator('a').nth(0)
            href = first_a.get_attribute('href')
            title = first_a.text_content()
            comment_count = int(page.locator('a[title="Comments"]').nth(i).text_content())
            saved_deals[href] = {"Title": title, "Comment count": comment_count}
        return saved_deals

    def scroll_to_bottom(self, page):
        """Scrolls to the bottom of the page."""
        page.evaluate("""
        () => {
            return new Promise((resolve) => {
                let totalHeight = 0;
                const distance = 90;
                const timer = setInterval(() => {
                    const scrollHeight = document.body.scrollHeight;
                    window.scrollBy(0, distance);
                    totalHeight += distance;
                    if (totalHeight >= scrollHeight) {
                        clearInterval(timer);
                        resolve();
                    }
                }, 100);
            });
        }
        """)
        
    def get_total_pages(self, page):
        """Extracts total number of pages for the deals."""
        last_page_button = page.query_selector('button[aria-label="Ostatnia strona"]')
        if last_page_button:
            return int(last_page_button.inner_text().strip())
        return 1
    
    def get_graphql_files(self):
        """Returns a list of GraphQL response files."""
        return list(self.config.mitm_output_dir.glob("response_*.json"))

    def load_graphql_data(self, file_path):
        """Loads JSON data from a file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            print(f"Error loading file: {file_path}")
            return None

    def save_comment_data(self, deal_data, title):
        """Saves comment data to a JSON file in the scraped_data directory with a sanitized filename."""
        # Sanitize the title to create a valid filename
        sanitized_title = re.sub(r'[<>:"/\\|?*]', '_', title)
        self.config.json_output_dir.mkdir(exist_ok=True)
        json_file_path = Path(self.config.json_output_dir) / f"{sanitized_title}.json"
        
        # Save the data using the DataSaver utility
        DataSaver.save_data_to_json(deal_data, json_file_path)

    def process_replies(self, page, deal_data):
        """Handles loading and processing replies."""
        self.click_more_replies(page)
        time.sleep(1)
        scraped_replies_count = 0
        reply_files = self.get_graphql_files()
        print(f"Found {len(reply_files)} reply files.")
        for file in reply_files:
            reply_file_name = str(file)[-41:] 
            print(f"Processing '{reply_file_name}' reply file.")
            graphql_data = self.load_graphql_data(file)
            if not graphql_data or isinstance(graphql_data, list):
                print(f"No data or invalid data in the current reply file.")
                continue

            reply_data = graphql_data.get('data', {}).get('comments', {}).get('items', [])
            print(f"Found {len(reply_data)} replies in the current reply file.")
            for reply in reply_data:
                # Handle cases where parentReply is null
                parent_reply_user = None
                if reply.get("parentReply"):
                    parent_reply_user = reply["parentReply"].get("user", {}).get("username")

                # Find the main comment using mainCommentId
                main_comment_id = reply.get("mainCommentId")
                if main_comment_id:
                    main_comment = next(
                        (comment for comment in deal_data["replies"] if comment.get("commentId") == main_comment_id),
                        None
                    )
                    if main_comment:
                        # Add the reply to the main comment's "replies" field
                        if "replies" not in main_comment:
                            main_comment["replies"] = []
                        main_comment["replies"].append({
                            "author": reply.get("user", {}).get("username"),
                            "created_at": reply.get("createdAt"),
                            "comment_body": reply.get("preparedHtmlContent"),
                            "reaction_count": reply.get("reactionCounts"),
                            "replies_to": parent_reply_user
                        })
                        scraped_replies_count += 1

        print(f"Scraped replies count for all reply files: {scraped_replies_count}.")
        return deal_data, scraped_replies_count

    def click_more_replies(self, page):
        """Clicks 'See more replies' buttons."""
        while True:
            buttons = page.locator('button[data-t="moreReplies"]')
            if buttons.count() == 0:
                break
            try:
                buttons.nth(0).click()
                time.sleep(2)
            except Exception as e:
                print(f"Error clicking 'See more replies': {e}")
                break

    def click_next_page(self, page):
        """Clicks the 'Next page' button if it's not disabled."""
        try:
            next_button = page.locator('button[aria-label="Następna strona"]')
            is_disabled = next_button.get_attribute('disabled')
            
            if not is_disabled:
                next_button.click()
                print("Clicked 'Next page'.")
                page.wait_for_load_state('networkidle')
                return True
            else:
                print("'Next page' is disabled.")
                return False
        except:
            print("There is only one page.")
            return False
        
    def get_number_of_comment_pages(self, page):
        try:
            # Wait for pagination nav to be visible
            page.wait_for_selector('nav[aria-label="Numeracja"]', timeout=5000)

            # Locate the "last page" button
            last_page_button = page.locator('button[aria-label="Ostatnia strona"]')

            if last_page_button.count() > 0:
                text = last_page_button.inner_text().strip()
                number_of_pages = int(text)
                print(f"Found {number_of_pages} pages of comments.")
                return number_of_pages
            else:
                return 1  # Fallback if "Ostatnia strona" not found
        except Exception as e:
            print(f"Error getting number of comment pages: {e}")
            return 1

    def scrape_data(self):
        """Main scraping logic."""
        comments_count = self.state_manager.get_comment_count()

        with sync_playwright() as p:
            browser = p.chromium.launch_persistent_context(
                user_data_dir=self.config.chrome_user_data_dir,
                executable_path=self.config.browser_path,
                headless=False,
                proxy={"server": "http://localhost:8080"},
                args=["--no-sandbox", "--disable-dev-shm-usage"]
            )
            page = browser.new_page()
            saved_deals = self.get_saved_deals(page)

            print(f"Found {len(saved_deals)} deals to scrape.")

            for deal_url, deal_info in saved_deals.items():
                print(f"Scraping: '{deal_url}'")
                print(f"Declared comment count for all comments and replies of this deal: {deal_info['Comment count']}")
                if comments_count.get(deal_url, 0) >= deal_info["Comment count"]:
                    print("This deal has been already scraped + no new comments found. Skipping.")
                    continue
                
                # Clear old GraphQL files
                for file in self.get_graphql_files():
                    os.remove(file)

                deal_data = {}
                deal_data["Title"] = deal_info["Title"]
                deal_data["Comment count"] = 0
                deal_data["replies"] = []

                page.goto(deal_url)
                self.scroll_to_bottom(page)

                number_of_comment_pages = self.get_number_of_comment_pages(page)
                comment_page_urls = [urljoin(deal_url, f"?page={num}#comments") for num in range(1, number_of_comment_pages+1)]

                scraped_comments_and_replies_count = 0

                for comment_page_url in comment_page_urls:
                    print(f"Processing {comment_page_url}")
                    page.goto(comment_page_url)
                    self.scroll_to_bottom(page)

                    graphql_files = self.get_graphql_files()
                    if not graphql_files:
                        print("No graphql files found")
                        continue

                    earliest_file = min(graphql_files, key=os.path.getctime)
                    graphql_data = self.load_graphql_data(earliest_file)
                    if not graphql_data:
                        print("No graphql data found")
                        continue

                    comments = graphql_data[0].get('data', {}).get('comments', {}).get('items', [])
                    scraped_comments_count = 0
                    print(f"Found {len(comments)} main comments to be scraped on this page.\n")

                    for comment in comments:
                        deal_data["replies"].append({
                            "commentId": comment.get("commentId"),
                            "author": comment.get("user", {}).get("username"),
                            "created_at": comment.get("createdAt"),
                            "comment_body": comment.get("preparedHtmlContent"),
                            "reaction_count": comment.get("reactionCounts"),
                            "replies": []  # Initialize an empty list for replies
                        })
                        scraped_comments_count += 1

                    print(f"Main comments scraped so far: {scraped_comments_count}.\n")

                    deal_data, scraped_replies_count = self.process_replies(page, deal_data)
                    
                    scraped_comments_and_replies_count += scraped_comments_count
                    scraped_comments_and_replies_count += scraped_replies_count
                    deal_data["Comment count"] = scraped_comments_and_replies_count
                    print(f'\ndeal_data["Comment count"]: {deal_data["Comment count"]}')
                    print(f'deal_info["Comment count"]: {deal_info["Comment count"]}')

                    if deal_data["Comment count"] < deal_info["Comment count"]:
                        print(f"\nWARNING. Comments/replies present in the deal: {deal_info['Comment count']}. Actual scraped comments/replies count: {deal_data['Comment count']}.")

                    self.save_comment_data(deal_data, deal_data["Title"])

                    # Update state
                    comments_count[deal_url] = deal_data["Comment count"]
                    self.state_manager.save_data_to_state_file(comments_count)

                    # Clear old GraphQL files
                    for file in self.get_graphql_files():
                        os.remove(file)

        browser.close()