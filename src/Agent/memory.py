import sqlite3
from langgraph.checkpoint.sqlite import SqliteSaver
from src.utils.basic_utils import load_yaml_config
#****************** Function to get Memory Saver ******************#
    

def get_memory():
    config = load_yaml_config("configs/db_config.yaml")
    conn = sqlite3.connect(database=config["chatbot_history_db"], check_same_thread=False)
    checkpoint = SqliteSaver(conn)
    return checkpoint