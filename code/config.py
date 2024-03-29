from dotenv import load_dotenv
from os import getenv

# ssh -i ~/.ssh/ssh_p student@158.160.134.86
# curl -H Metadata-Flavor:Google 169.254.169.254/computeMetadata/v1/instance/service-accounts/default/token

GPT_URL = "https://llm.api.cloud.yandex.net/foundationModels/v1/completion"
MAX_USERS = 3
MAX_SESSIONS = 3
MAX_TOKENS_PER_SESSION = 400
MAX_MODEL_TOKENS = 40
ADMINS_ID = [1999763430]
IAM_TOKEN_PATH = 'other/token.json'
IAM_TOKEN_ENDPOINT = "http://169.254.169.254/computeMetadata/v1/instance/service-accounts/default/token"
load_dotenv()

FOLDER_ID = getenv('FOLDER_ID')
TOKEN = getenv('TOKEN')

DB_NAME = 'sqlite3.db'
