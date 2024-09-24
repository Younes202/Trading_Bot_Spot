import os

class Settings:
    # Class-level attributes for settings
    RedisUrl = 'redis://localhost:6379/0'  # Example Redis URL
    trained_models = './app/predictions/trained_models/'  # Example directory for trained models

    # Define the base directory as the root of the project
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    # Define other directories relative to BASE_DIR
    NOW_DIR = os.path.join(BASE_DIR, 'app', 'now')
    PREDICTIONS_DIR = os.path.join(BASE_DIR, 'app', 'predictions')

    # Path to the config file itself
    CONFIG_FILE_PATH = os.path.abspath(__file__)

    # Other configuration settings
    DATABASE_URL = 'sqlite:///{}'.format(os.path.join(BASE_DIR, 'db.sqlite3'))

    @classmethod
    def get(cls, key):
        """
        Retrieve the value of a setting by key.

        Parameters
        ----------
        key : str
            The name of the setting to retrieve.

        Returns
        -------
        value : str
            The value of the requested setting.
        """
        return getattr(cls, key, None)

    @classmethod
    def set(cls, key, value):
        """
        Set the value of a setting.

        Parameters
        ----------
        key : str
            The name of the setting to update.
        value : str
            The new value for the setting.
        """
        setattr(cls, key, value)

    def __repr__(self):
        """
        String representation of the settings for debugging purposes.
        """
        return (f"Settings(RedisUrl={self.RedisUrl}, trained_models={self.trained_models}, "
                f"BASE_DIR={self.BASE_DIR}, NOW_DIR={self.NOW_DIR}, "
                f"PREDICTIONS_DIR={self.PREDICTIONS_DIR}, CONFIG_FILE_PATH={self.CONFIG_FILE_PATH}, "
                f"DATABASE_URL={self.DATABASE_URL})")

# Create an instance of Settings to use in imports
settings = Settings()