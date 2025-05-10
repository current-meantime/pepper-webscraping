import json
from config import Config

class StateManager:
    """Manages the state file used for tracking comment counts."""

    def __init__(self, state_file=None):
        if state_file:
            self.state_file = state_file
        else:
            # use the default state file from the config
            self.state_file = Config().state_file

    def create_state_file(self):
        """Creates a new empty state file and returns an empty dictionary."""
        self.state_file.parent.mkdir(parents=True, exist_ok=True)
        # create an empty JSON file
        with open(self.state_file, "w", encoding='utf-8') as f:
            json.dump({}, f)
        print(f"Creating a new state file at '{self.state_file}'.")
        return {}

    def get_comment_count(self):
        """Retrieves the comment count for each deal from the state file."""
        if self.state_file.exists():
            try:
                with open(self.state_file, "r") as f:
                    return json.load(f)
            except json.JSONDecodeError:
                print(f"The state file contains invalid JSON.")
                return self.create_state_file()
        else:
            print(f"\nThe state file does not exist.")
            return self.create_state_file()

    def save_data_to_state_file(self, comments_count):
        """Updates the state file with the current comment count."""
        with open(self.state_file, "w", encoding='utf-8') as f:
            json.dump(comments_count, f)
        print(f"Saving the new state file at '{self.state_file}'.")