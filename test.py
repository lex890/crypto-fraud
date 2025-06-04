import configparser
import os

cfg_path='./keys/settings.cfg'

# Your functions here...
def save_api_key(identifier, api_key, cfg_path='settings.cfg', key_name="CMCKEY"):
    config = configparser.ConfigParser()

    # Read existing config if it exists
    if os.path.exists(cfg_path):
        config.read(cfg_path)

    # Ensure "Main" and the identifier sections exist
    if not config.has_section("Main"):
        config.add_section("Main")
    if not config.has_section(identifier):
        config.add_section(identifier)
    else:
        # Clear any other keys under this identifier section
        for key in config[identifier]:
            config.remove_option(identifier, key)

    # Set the new default and API key
    config.set("Main", "DefaultAPI", identifier)
    config.set(identifier, key_name, api_key)

    # Save to file
    with open(cfg_path, 'w') as configfile:
        config.write(configfile)

    print(f"API key saved to '{cfg_path}' under section [{identifier}] with only one key.")

def load_api_key(identifier, cfg_path=cfg_path, key_name="KEY"):  # 🔧 fixed default to match save
    config = configparser.ConfigParser()
    if not os.path.exists(cfg_path):
        print(f"No config file found at {cfg_path}. Please save an API key first.")
        return None

    config.read(cfg_path)
    if config.has_section("Main") and config.has_option("Main", "DefaultAPI"):
        identifier = config.get("Main", "DefaultAPI")
        if config.has_section(identifier) and config.has_option(identifier, key_name):
            return config.get(identifier, key_name)
        else:
            print(f"No API key found in section [{identifier}] under key '{key_name}'.")
            return None
    else:
        print("No default API set in [Main] section.")
        return None

# ✅ Test values
identifier = "CoinGecko"
api_key = "abc123geckotest"

# 🔧 Run test
save_api_key(identifier, api_key)
retrieved_key = load_api_key()
print(type(retrieved_key))

print("\n--- Test Result ---")
print(f"Retrieved key: {retrieved_key}")
