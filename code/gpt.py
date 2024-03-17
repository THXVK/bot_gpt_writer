import requests
from config import MAX_TOKENS, FOLDER_ID, IAM_TOKEN
import requests

# todo: переделать


data = {
    "modelUri": f"gpt://{FOLDER_ID}/yandexgpt-lite",
    "completionOptions": {
        "stream": False,
        "temperature": 0.6,
        "maxTokens": f"{MAX_TOKENS}"
    },
    "messages": [
        {
            "role": "system",
            "text": "Ты - Владимир Владимирович Маяковский русский и советский поэт. Пример его стихов ты можешь посмотреть в интернете"
        },
        {
            "role": "user",
            "text": "Напиши стихотворение про то, как нейросеть DevIn забрала работу у программистов"
        },
    ]
}

headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {IAM_TOKEN}",
    "x-folder-id": f"{FOLDER_ID}",
}

url = "https://llm.api.cloud.yandex.net/foundationModels/v1/completion"



def count_tokens(text: str) -> int:
    data = {
        "modelUri": f"gpt://{FOLDER_ID}/yandexgpt-lite/latest",
        "text": text,
    }
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {IAM_TOKEN}",
        "x-folder-id": f"{FOLDER_ID}",
    }
    url = "https://llm.api.cloud.yandex.net/foundationModels/v1/tokenize"

    response = requests.post(
        url=url,
        headers=headers,
        json=data
    )

    return len(response.json()['tokens'])


# def count_tokens_in_dialogue(message: list[dict]) -> int:
