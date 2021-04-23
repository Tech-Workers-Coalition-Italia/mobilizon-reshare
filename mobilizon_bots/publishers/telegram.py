import requests

from .abstract import AbstractPublisher


class TelegramPublisher(AbstractPublisher):

    def post(self) -> bool:
        chat_id = self.credentials['chat_id']
        text = self.event['text']
        token = self.credentials['token']
        post_params_kwargs = self.event.get('post_params_kwargs')
        res = requests.post(
            url=f'https://api.telegram.org/bot{token}/sendMessage',
            params=dict(chat_id=chat_id, text=text, **post_params_kwargs)
        )
        data = self.__validate_response(res)
        if data.get('__error'):
            self.log_error(data['__error'])
            return False

        return True

    def validate_credentials(self) -> bool:
        chat_id = self.credentials.get('chat_id')
        token = self.credentials.get('token')
        username = self.credentials.get('username')
        if any(a is None for a in (chat_id, token, username)):
            self.log_error("Required info is missing")
            return False

        res = requests.get(f'https://api.telegram.org/bot{token}/getMe')
        data = self.__validate_response(res)
        if data.get('__error'):
            self.log_error(data['__error'])
            return False

        if not username == data.get('result', {}).get('username'):
            self.log_error("Found a different bot than the expected one!")
            return False

        return True

    def validate_event(self) -> bool:
        text = self.event.get('text')
        if not (text and text.strip()):
            self.log_error(f"No text was found!")
            return False
        return True

    @staticmethod
    def __validate_response(res):
        try:
            res.raise_for_status()
        except requests.exceptions.HTTPError as e:
            return {'__error': str(e)}

        try:
            data = res.json()
        except ValueError:
            return {'__error': "Server returned invalid json data"}

        if not data.get('ok'):
            data['__error'] = f"Invalid request (response: {data})"

        return data
