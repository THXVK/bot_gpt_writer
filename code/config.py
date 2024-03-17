from dotenv import load_dotenv
from os import getenv

load_dotenv()

MAX_USERS = 2
MAX_TOKENS = 75
MAX_SESSIONS = 3
MAX_TOKENS_PER_SESSION = 800

ADMINS_ID = [1999763430]

IAM_TOKEN = getenv('IAM_TOKEN')
FOLDER_ID = getenv('FOLDER_ID')
TOKEN = getenv('TOKEN')

DB_NAME = 'sqlite3.db'
