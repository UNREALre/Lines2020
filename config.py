import os
import confuse
from logger import get_logger

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))

os.environ["LINES2020DIR"] = PROJECT_ROOT

app_logger = get_logger(__name__)

app_config = confuse.Configuration('Lines2020')


def reload_config():
    global app_config
    app_config = confuse.Configuration('Lines2020')
    return app_config


