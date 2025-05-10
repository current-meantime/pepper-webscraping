from pathlib import Path

class Config:
    """Configuration class to store paths and settings."""

    def __init__(self):
        self.browser_path = r"C:\Program Files\Google\Chrome\Application\chrome.exe" # change to your browser path
        self.chrome_user_data_dir = r"C:\Users\your-user\AppData\Local\Google\Chrome\User Data" # change to your user data directory
        self.profile_directory_name = "Profile 6" # change to your profile directory name
        self.this_script_file_path = Path(__file__)
        self.this_script_directory = self.this_script_file_path.parent
        self.output_path = self.this_script_directory
        self.json_output_dir = self.output_path / "scraped_data"
        self.json_output_dir.mkdir(parents=True, exist_ok=True)
        self.state_file = self.this_script_directory / "state.json"
        self.saved_deals_page = "https://www.pepper.pl/profile/your-profile/saved-deals" # change to your profile page
        self.mitm_output_dir = Path(self.this_script_directory) / "mitmproxy_output"
        self.mitm_output_dir.mkdir(parents=True, exist_ok=True)