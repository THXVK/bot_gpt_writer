
import requests

from log import logger
from data import get_user_data
from config import GPT_URL, LOGS_PATH, MAX_MODEL_TOKENS, FOLDER_ID, IAM_TOKEN, IAM_TOKEN_PATH, IAM_TOKEN_ENDPOINT
import time
import json


def create_new_iam_token():
    """
    Получает новый IAM-TOKEN и дату истечения его срока годности и записывает полученные данные в json
    """
    headers = {"Metadata-Flavor": "Google"}
    try:
        response = requests.get(IAM_TOKEN_ENDPOINT, headers=headers)

    except Exception as e:
        error_msg = f"Ошибка: {e}"
        logger.error(error_msg)

    else:
        if response.status_code == 200:
            token_data = {
                "access_token": response.json().get("access_token"),
                "expires_at": response.json().get("expires_in") + time.time()
            }
            with open(IAM_TOKEN_PATH, "w") as token_file:
                json.dump(token_data, token_file)
        else:
            error_msg = f"Ошибка: {response.status_code}"
            logger.error(error_msg)


def get_iam_token() -> str:
    """
    Получает действующий IAM-TOKEN и возвращает его
    """
    try:
        with open(IAM_TOKEN_PATH, "r") as token_file:
            token_data = json.load(token_file)

        expires_at = token_data.get("expires_at")

        if expires_at <= time.time():
            create_new_iam_token()

    except FileNotFoundError:
        create_new_iam_token()
    with open(IAM_TOKEN_PATH, "r") as token_file:
        token_data = json.load(token_file)
    return token_data.get("access_token")


def gen_promt(user_id) -> str:
    data = get_user_data(user_id)
    params = {
        'character': data[4],
        'location': data[5],
        'genre': data[6],
        'addition': data[7],
    }

    promt = f'учти, что главный герой - {params['character']}, место действия - {params['location']}, жанр - {params['genre']}'
    if params['addition']:
        promt += f', учти: {params['addition']}'
    return promt


def gpt_start(user_id):
    promt = gen_promt(user_id)
    iam_token = IAM_TOKEN
    data = {
        "modelUri": f"gpt://{FOLDER_ID}/yandexgpt-lite",
        "completionOptions": {
            "stream": False,
            "temperature": 0.9,
            "maxTokens": f"{MAX_MODEL_TOKENS}"
        },
        "messages": [
            {
                "role": "system",
                "text": f'Ты - сценарист, придумай завязку истории, ' + promt + ', не поясняй ответ'
            },
        ]
    }

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {iam_token}",
        "x-folder-id": f"{FOLDER_ID}",
    }

    response = requests.post(
        url=GPT_URL,
        headers=headers,
        json=data
    )
    if response.status_code == 200:
        result = response.json()['result']['alternatives'][0]['message']['text']
        tokens = response.json()['result']['usage']['completionTokens']

        return {'result': result, 'tokens': int(tokens)}
    else:
        error_msg = f"Ошибка: {response.status_code}"
        logger.error(error_msg)
        return {'result': 'что то пошло не так', 'tokens': 0}


def gpt_ask(text, user_id):
    promt = gen_promt(user_id)
    story = get_user_data(user_id)[8]
    iam_token = IAM_TOKEN
    data = {
        "modelUri": f"gpt://{FOLDER_ID}/yandexgpt-lite",
        "completionOptions": {
            "stream": False,
            "temperature": 0.9,
            "maxTokens": f"{MAX_MODEL_TOKENS}"
        },
        "messages": [
            {
                "role": "system",
                "text": 'Ты - сценарист, продолжи сюжет согласно сообщению пользователя и истории ' + promt +
                        ', не поясняй ответ'
            },
            {
                "role": "user",
                "text": text
            },
            {
                "role": "assistant",
                "text": f'история сообщений: {story}'
            },
        ]
    }

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {iam_token}",
        "x-folder-id": f"{FOLDER_ID}",
    }

    response = requests.post(
        url=GPT_URL,
        headers=headers,
        json=data
    )
    if response.status_code == 200:
        result = response.json()['result']['alternatives'][0]['message']['text']
        tokens = response.json()['result']['usage']['completionTokens']

        return {'result': result, 'tokens': int(tokens)}
    else:
        error_msg = f"Ошибка: {response.status_code}"
        logger.error(error_msg)
        return {'result': 'что то пошло не так', 'tokens': 0}


def gpt_end(user_id) -> str:
    promt = gen_promt(user_id)
    story = get_user_data(user_id)[8]
    iam_token = IAM_TOKEN
    data = {
        "modelUri": f"gpt://{FOLDER_ID}/yandexgpt-lite",
        "completionOptions": {
            "stream": False,
            "temperature": 0.9,
            "maxTokens": f"{MAX_MODEL_TOKENS}"
        },
        "messages": [
            {
                "role": "system",
                "text": 'Ты - сценарист, закончи сюжет согласно и истории ' + promt + ', не поясняй ответ'
            },
            {
                "role": "assistant",
                "text": f'история сообщений: {story}'
            }
        ]
    }
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {iam_token}",
        "x-folder-id": f"{FOLDER_ID}",
    }

    response = requests.post(
        url=GPT_URL,
        headers=headers,
        json=data
    )
    if response.status_code == 200:
        result = response.json()['result']['alternatives'][0]['message']['text']
        return result

    else:
        error_msg = f"Ошибка: {response.status_code}"
        logger.error(error_msg)
        return 'что то пошло не так'
