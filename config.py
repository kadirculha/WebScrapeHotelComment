import json

import yaml


class Configurator:
    def __init__(self):
        self.cfg = self.load_config()

    @staticmethod
    def load_config():
        try:
            with open("data/config.yaml", "r", encoding="utf-8") as file:
                return yaml.safe_load(file)
        except FileNotFoundError as err:
            raise FileNotFoundError(f"Configuration file not found: {err}")
        except yaml.YAMLError as err:
            raise ValueError(f"Error parsing YAML file: {err}")

    def get_user_agents_path(self):
        return self.cfg["USER_AGENTS_PATH"]

    def get_hotel_df_path(self):
        return self.cfg["HOTEL_DF_PATH"]

    def get_out_path(self):
        return self.cfg["REVIEWS_OUTPUT_PATH"]

