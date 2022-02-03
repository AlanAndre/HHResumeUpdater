import requests

from utils import config


def send_telegram_message(message: str):
    responses = []
    for chat_id in config.CHAT_IDS:
        bot_api_token = config.BOT_API_TOKEN
        url = config.telegram_url

        params = {'chat_id': chat_id, 'text': message}
        responses.append(requests.get(url + bot_api_token + '/sendMessage', params=params))
    return responses[0]
