import requests

from .abstract import AbstractPublisher


class TelegramPublisher(AbstractPublisher):
    def post(self) -> bool:
        chat_id = self.credentials["chat_id"]
        text = self.event["text"]
        token = self.credentials["token"]
        post_params_kwargs = self.event.get("post_params_kwargs")
        res = requests.post(
            url=f"https://api.telegram.org/bot{token}/sendMessage",
            params=dict(chat_id=chat_id, text=text, **post_params_kwargs),
        )
        return self._validate_response(res)

    def _log_error_and_raise(self, message):
        self.log_error(message)
        raise ValueError(message)

    def validate_credentials(self) -> bool:
        chat_id = self.credentials.get("chat_id")
        token = self.credentials.get("token")
        username = self.credentials.get("username")
        if all([chat_id, token, username]):
            # TODO: add composable errors to highlight which credentials are missing
            self._log_error_and_raise("Some credentials are missing")

        res = requests.get(f"https://api.telegram.org/bot{token}/getMe")
        data = self._validate_response(res)

        if not username == data.get("result", {}).get("username"):
            self._log_error_and_raise("Found a different bot than the expected one")
        return data

    def validate_event(self) -> bool:
        text = self.event.get("text")
        if not (text and text.strip()):
            self._log_error_and_raise("No text was found. Invalid event")

    def _validate_response(self, res):
        res.raise_for_status()

        try:
            data = res.json()
        except ValueError as e:
            self.log_error("Server returned invalid json data")
            raise ValueError from e

        if not data.get("ok"):
            raise ValueError(f"Invalid request (response: {data})")

        return data
