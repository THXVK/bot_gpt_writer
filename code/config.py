from dotenv import load_dotenv
from os import getenv

# ssh -i ~/.ssh/ssh_p student@158.160.134.86
# curl -H Metadata-Flavor:Google 169.254.169.254/computeMetadata/v1/instance/service-accounts/default/token

GPT_URL = "https://llm.api.cloud.yandex.net/foundationModels/v1/completion"
MAX_USERS = 3
MAX_TOKENS = 75
MAX_SESSIONS = 3
MAX_TOKENS_PER_SESSION = 800
MAX_MODEL_TOKENS = 100
ADMINS_ID = [1999763430]
LOGS_PATH = 'other/logConfig.log'
METADATA_URL = "http://169.254.169.254/computeMetadata/v1/instance/service-accounts/default/token"
IM_TOKEN_PATH = 'other/token.json'
load_dotenv()

IAM_TOKEN = getenv('IAM_TOKEN')
FOLDER_ID = getenv('FOLDER_ID')
TOKEN = getenv('TOKEN')

DB_NAME = 'sqlite3.db'
