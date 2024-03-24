
import requests

from data import get_user_data
from config import GPT_URL, LOGS_PATH, MAX_MODEL_TOKENS, FOLDER_ID, METADATA_URL, IAM_TOKEN, IM_TOKEN_PATH
import time
import json




def create_new_token():
    try:
        headers = {"Metadata-Flavor": "Google"}
        response = requests.get(METADATA_URL, headers=headers)
        if response.status_code == 200:
            token_data = response.json()
            token_data['expires_at'] = time.time() + token_data['expires_in']
            with open(IM_TOKEN_PATH, 'w') as token_file:
                json.dump(token_data)
        return response.json()
    except Exception:
        pass


def get_aim_token():
    try:
        with open(IM_TOKEN_PATH, 'r') as file:
            data = json.load(file)
            expiration = data['expires_at']

        if expiration < time.time():
            return
    except Exception:
        pass


def gen_promt(user_id):
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
        "Authorization": f"Bearer {IAM_TOKEN}",
        "x-folder-id": f"{FOLDER_ID}",
    }

    response = requests.post(
        url=GPT_URL,
        headers=headers,
        json=data
    )
    result = response.json()['result']['alternatives'][0]['message']['text']
    tokens = response.json()['result']['usage']['totalTokens']
    print(tokens)
    return {'result': result, 'tokens': tokens}


def gpt_end(text, user_id):
    promt = gen_promt(user_id)
    story = get_user_data(user_id)[8]
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
        "Authorization": f"Bearer {IAM_TOKEN}",
        "x-folder-id": f"{FOLDER_ID}",
    }

    response = requests.post(
        url=GPT_URL,
        headers=headers,
        json=data
    )
    result = response.json()['result']['alternatives'][0]['message']['text']
    tokens = response.json()['result']['usage']['totalTokens']

    return {'result': result, 'tokens': tokens}


def gpt_ask(text, user_id):
    promt = gen_promt(user_id)
    story = get_user_data(user_id)[8]
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
        "Authorization": f"Bearer {IAM_TOKEN}",
        "x-folder-id": f"{FOLDER_ID}",
    }

    response = requests.post(
        url=GPT_URL,
        headers=headers,
        json=data
    )
    result = response.json()['result']['alternatives'][0]['message']['text']

    return result
