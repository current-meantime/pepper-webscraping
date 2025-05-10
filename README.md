# Pepper Scraper

Pepper Scraper is a Python utility designed to extract and organize comments from selected threads on the Pepper.pl platform with the use of `Playwright` and `mitmproxy`.

## Overview

The scraper collects comments, replies, and associated metadata from specified Pepper.pl threads, organizing the information into structured JSON files. These files can then be utilized for further processing, analysis, or as input for AI-powered knowledge extraction.

## Key Features

- Scrapes comments and replies from Pepper.pl threads
- Captures metadata such as usernames and reaction counts
- Organizes scraped data into JSON files for easy processing
- Supports multi-page comment sections
- Handles nested replies and expanded comment threads

Additionally:
- The scraper is adjusted to **Chrome**
- Scraping is done with `Playwright`
- `mitmproxy` is used to intercept responses that Pepper blocks when it detects automated browsing

## Intended Use

The collected information can be used for various purposes, including AI tasks such as:

- Sentiment analysis
- User behavior studies
- Topic modeling
- Content summarization
- Trend identification

Since the reactions to the comments are included in the output and are a valuable source for assessing mood, intent, etc., it may be beneficial to prompt an AI going through the scraped data to take them into consideration.

The scraper is designed in a way that the selection of the treads that are supposed to be scraped is done by **manually adding Pepper deals to the Saved Tab**. If you scroll through the Pepper platform and encounter a deal that may contain an informative discussion, add it to this tab by clicking on a bookmark icon. You may run the scraper after each added deal or after many of them have been added - that's up to you.

## Intended behavior of the script
The program decides to scrape a deal if:
1. It **hasn't been scraped** before.
2. It has been scraped before but **new comments appeared** or some comments simply did not get scraped the previous time.

That's why it creates a `state.json` file on the first run and compares data that is stored there with the deals in the Saved Tab to avoid unneccesary scraping.

## Setup

In order to run this program smoothly, you'll need to:
1. Create a clean Google Chrome profile or choose an existing one.
2. Create an account on `pepper.pl`. (unless you already have one)
3. While using the chosen Chrome profile, log into your account. **Enable the option to stay logged in.**
4. Navigate to your profile's page and then to the "Saved" tab (pl. "Zapisane"). Save the link of this page.
5. In your file system, find out the path to `chrome.exe` and save it.
It's typically: `C:/Program Files/Google/Chrome/Application/chrome.exe`
6. Find out the directory path of the Chrome's user profile that you will use for scraping. Save this path.
7. Choose the directory path that will be the output directory for the program and save it.
8. Update the `config.py` with proper paths.
9. Use `pip` to install `playwright` and `mitmproxy` or run `pip install -r requirements.txt`.
10. Change the proxy settings on your machine to `127.0.0.1`, port `8080`.
11. `cd` into the directory where `mitmproxy_runner.py` is and run `mitmproxy -s mitmproxy_runner.py` in the terminal - it will start the `mitmproxy` response handler needed for intercepting network traffic.
12. Manually open Chrome on the scraping profile to make it the most recently accessed profile. For some reason, it helps preventing unexpected behavior of the script. Then, close Chrome.
13. For the last time make sure there are no open Chrome instances and run `main.py`.

It may be benefictial to ensure there are no extensions installed, as they could disrupt the flow of the program. Feel free to experiment, though. In my case, the script works without issues with uBlockOrigin installed.

Aditionally, **the scraper might not work if there are other Chrome instances open**. It is best to close them all before running the script.

Lastly, sometimes the browser gets flagged as an automatically steered browser and is not let into the website. Cleaning browsing history might help. In my case, it did not. What helped was changing the machine I run code on.

### Advice on finding the chrome user profile's directory path

Paths to non-default profiles are typically:

`C:/Users/YourUsername/AppData/Local/Google/Chrome/User Data/Profile 1` (or any other number after 'Profile')

The default user profile's path is typically:

`C:\Users\alemr\AppData\Local\Google\Chrome\User Data\Default`

You may actually use 'Default' as the scraping profile as well.

If you see many user profile directories and you're not sure which corresponds to the profile that you've just created for the purpose of scraping:
1. Open Chrome's `User Data` directory in your file manager.
2. Look at the modification date of the 'Profile' folders - which one is the latest? Save its directory path.
3. Alternatively, open the 'Profile' folders one by one and look for the `Googe Profile.ico` file. They're going to have a miniature picture of your profile's picture contained within the icon. If it's the one you want to use, save its directory path.
4. Alternatively, in this `User Data` directory, go to the search tab, type `Googe Profile.ico` and look through the results to find this minature picture, then save the directory path.
5. Or just use the `Everything` program to find folders called `Profile {num}`.

## Future plans
1. Sometimes comments do not get scraped. To be fixed.
2. Emojis, images, etc. in comments are not properly handled. Their handling/formatting will be improved in the future.
3. The scrape_data function is rather messy but will be cleaned up soon.
4. Make the scraper more robust. On some machines, the website detects automated browsing.