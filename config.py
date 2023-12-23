import json


with open("config.json") as f:
    config = json.load(f)
    TOKEN = config["bot_token"].strip()
    BASE_API_URL = config["base_api_url"]
    TEST_GUILD_ID = config["test_guild_id"]
