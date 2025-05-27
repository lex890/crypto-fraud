import configparser
import os

def save_api_key(identifier,api_key, cfg_path='settings.cfg', key_name="KEY"):
    config = configparser.ConfigParser()
    if not config.has_section("Main"):
        config.add_section("Main")
    # Create section if not present
    if not config.has_section(identifier):
        config.add_section(identifier)
    # Save API key
    config.set("Main","DefaultAPI",identifier)
    config.set(identifier, key_name, api_key)

    # Write to file
    with open(cfg_path, 'w') as configfile:
        config.write(configfile)
    
    print(f"API key saved to '{cfg_path}' under section [{identifier}].")

def load_api_key(cfg_path='settings.cfg', key_name="key"):
    config = configparser.ConfigParser()
    
    if not os.path.exists(cfg_path):
        print(f"No config file found at {cfg_path}. Please save an API key first.")
        return None

    config.read(cfg_path)
    if config.has_section("Main") and config.has_option("defaultapi"):
        identifier = config.get("Main","DefaultAPI")
        if config.has_section(identifier) and config.has_option(identifier, key_name):
            return config.get(key_name)
        else:
            print(f"No API key found in section [{identifier}] under key '{key_name}'.")
            return None