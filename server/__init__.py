import os
import json

from django.core.management.utils import get_random_secret_key

POSTGRES = "POSTGRES"


def read_config(config_path):
    config_data = {}
    if os.path.exists(config_path):
        with open(config_path, 'r') as file:
            config_data = json.load(file)
    return config_data


def get_db_configs(config_data=None):
    if config_data:
        db_name = config_data.get("WFIT_POSTGRES_DATABASE", None)
        db_user = config_data.get("WFIT_POSTGRES_USERNAME", None)
        db_password = config_data.get("WFIT_POSTGRES_PASSWORD", None)
        db_host = config_data.get("WFIT_POSTGRES_PASSWORD", None)
        db_port = config_data.get("WFIT_POSTGRES_PORT", None)
    else:
        db_name = os.environ.get("WFIT_POSTGRES_DATABASE", None)
        db_user = os.environ.get("WFIT_POSTGRES_USERNAME", None)
        db_password = os.environ.get("WFIT_POSTGRES_PASSWORD", None)
        db_host = os.environ.get("WFIT_POSTGRES_PASSWORD", None)
        db_port = os.environ.get("WFIT_POSTGRES_PORT", None)

    if db_name and db_user and db_password and db_host and db_port:
        return db_name, db_user, db_password, db_host, db_port

    return None


def get_django_secret_key(config_data, config_path):
    updated_config = config_data
    django_secret_key = os.environ.get("WFIT_DJANGO_SECRET_KEY", None)
    if django_secret_key:
        print("WFIT_DJANGO_SECRET_KEY found from environment variable")
    else:
        print("WFIT_DJANGO_SECRET_KEY not found from environment variable")
        django_secret_key = config_data.get("WFIT_DJANGO_SECRET_KEY", None)
        if django_secret_key:
            print("WFIT_DJANGO_SECRET_KEY found from config.json")
        else:
            django_secret_key = get_random_secret_key()
            print("Generated  WFIT_DJANGO_SECRET_KEY")
            new_config = config_data.copy()
            new_config.update({"WFIT_DJANGO_SECRET_KEY": "django-insecure-g=" + django_secret_key})
            with open(config_path, 'w') as file:
                print("Adding WFIT_DJANGO_SECRET_KEY to config.json")
                json.dump(new_config, file, indent=4)
                print("Added WFIT_DJANGO_SECRET_KEY to config.json")
            updated_config = updated_config
    return django_secret_key, updated_config


def delete_log_file(base_dir):
    log_file_path = os.path.join(base_dir, 'wfit.log')
    if os.path.exists(log_file_path):
        os.remove(log_file_path)
        print(f"{log_file_path} has been deleted.")


def get_wfit_configs(base_dir):
    config_path = os.path.join(base_dir, 'config.json')
    config_data = read_config(config_path)
    missing_configs = []
    database = {}

    django_secret_key, config_data = get_django_secret_key(config_data, config_path)

    trello_api_key = os.environ.get("MY_TRELLO_API_KEY", None)
    trello_api_token = os.environ.get("MY_TRELLO_API_TOKEN", None)
    youtube_api_key = os.environ.get("MY_YOUTUBE_API_KEY")

    if not trello_api_key:
        trello_api_key = config_data.get("MY_TRELLO_API_KEY", None)
    if not trello_api_token:
        trello_api_token = config_data.get("MY_TRELLO_API_TOKEN", None)

    if not trello_api_key:
        missing_configs.append("MY_TRELLO_API_KEY not found.")
    if not trello_api_token:
        missing_configs.append("MY_TRELLO_API_TOKEN not found.")

    if not youtube_api_key:
        youtube_api_key = config_data.get("YOUTUBE_API_KEY", None)

    db_engine = config_data.get("DB_ENGINE")
    if db_engine:
        if db_engine == "POSTGRES":
            db_configs = get_db_configs()
            if not db_configs:
                db_configs = get_db_configs(config_data)
                if not db_configs:
                    missing_configs.append(
                        "POSTGRES database configurations are not found in the environment variables" +
                        " or in the configuration JSON file.")

            if db_configs:
                db_name, db_user, db_password, db_host, db_port = db_configs
                database = {
                    'ENGINE': 'django.db.backends.postgresql',
                    'NAME': db_name,
                    'USER': db_user,
                    'PASSWORD': db_password,
                    'HOST': db_host,
                    'PORT': int(db_port)
                }

        else:
            missing_configs.append("Invalid DB_ENGINE found in config.json")
    else:
        database = {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": base_dir / "db.sqlite3",
        }
    if missing_configs:
        print("Missing configurations found:")
        for message in missing_configs:
            print('\t', message)
        exit(0)
    print(f"Database Engine: {database['ENGINE']}")
    return django_secret_key, database, trello_api_key, trello_api_token, youtube_api_key, config_data
