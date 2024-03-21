import logging
import requests
from config import GPT_URL, LOGS_PATH, MAX_MODEL_TOKENS, FOLDER_ID, METADATA_URL, IAM_TOKEN, IM_TOKEN_PATH
import time
import json

logging.basicConfig(
    filename=LOGS_PATH,
    level=logging.DEBUG,
    format="%(asctime)s %(message)s",
    filemode="w",
)


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


# Функция для подсчета токенов в истории сообщений. На вход обязательно принимает список словарей, а не строку!
def count_tokens_in_dialogue(messages: list) -> int:
    folder_id = FOLDER_ID
    # token = get_aim_token()
    token = IAM_TOKEN
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    data = {
        "modelUri": f"gpt://{folder_id}/yandexgpt/latest",
        "maxTokens": MAX_MODEL_TOKENS,
        "messages": []
    }

    for row in messages:  # Меняет ключ "content" на "text" в словарях списка для корректного запроса
        data["messages"].append(
            {
                "role": row["role"],
                "text": row["content"]
            }
        )

    return len(
        requests.post(
            "https://llm.api.cloud.yandex.net/foundationModels/v1/tokenizeCompletion",
            json=data,
            headers=headers
        ).json()["tokens"]
    )


def get_system_content(subject, level):  # Собирает строку для system_content
    return f"Ты учитель по предмету {subject}. Формулируй ответы уровня {level}"


def ask_gpt_helper(messages: list) -> str:
    """
    Отправляет запрос к модели GPT с задачей и предыдущим ответом
    для получения ответа или следующего шага
    """
    temperature = 1

    response = requests.post(
        GPT_URL,
        headers={"Content-Type": "application/json"},
        json={
            "messages": messages,
            "temperature": temperature,
            "max_tokens": MAX_MODEL_TOKENS,
        },
    )
    if response.status_code == 200:
        result = response.json()["choices"][0]["message"]["content"]
        print("Ответ получен!")
        return result
    else:
        print("Не удалось получить ответ :(")
