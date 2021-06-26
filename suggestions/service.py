import abc
import logging

from mailjet_rest import Client

from .model import Suggestion


class SuggestionServiceInterface(abc.ABC):
    """
    Service to send a suggestion
    """

    @abc.abstractmethod
    def add_suggestion(self, suggestion: Suggestion):
        """
        Method to send a suggestion
        """


class MailjetSuggestionService(SuggestionServiceInterface):
    def __init__(
        self,
        mailjet_client: Client,
        suggestion_sender_name: str,
        suggestion_sender_email: str,
        suggestion_recipient_name: str,
        suggestion_recipient_email: str,
        suggestion_mailjet_custom_id: str,
    ):
        self.mailjet_client = mailjet_client
        self.suggestion_sender_name = suggestion_sender_name
        self.suggestion_sender_email = suggestion_sender_email
        self.suggestion_recipient_name = suggestion_recipient_name
        self.suggestion_recipient_email = suggestion_recipient_email
        self.suggestion_mailjet_custom_id = suggestion_mailjet_custom_id
        self.logger = logging.getLogger(__name__)

    def add_suggestion(self, suggestion: Suggestion):
        data = {
            "Messages": [
                {
                    "From": {
                        "Name": self.suggestion_sender_name,
                        "Email": self.suggestion_sender_email,
                    },
                    "To": [
                        {
                            "Name": self.suggestion_recipient_name,
                            "Email": self.suggestion_recipient_email,
                        }
                    ],
                    "Subject": "Querido Diário, hoje recebi uma sugestão",
                    "TextPart": f"From {suggestion.name} <{suggestion.email_address}>:\n\n{suggestion.content}",
                    "CustomID": self.suggestion_mailjet_custom_id,
                }
            ]
        }
        result = self.mailjet_client.send.create(data=data)

        self.logger.debug(f"Suggestion body response {result.json()}")
        if 200 <= result.status_code <= 299:
            self.logger.info(f"Suggestion created for {suggestion.email_address}")
            return True
        else:
            self.logger.error(
                f"Error on send email {suggestion.email_address}. Status code response: {result.status_code}"
            )
            return False


def create_suggestion_service(
    suggestion_mailjet_rest_api_key: str,
    suggestion_mailjet_rest_api_secret: str,
    suggestion_sender_name: str,
    suggestion_sender_email: str,
    suggestion_recipient_name: str,
    suggestion_recipient_email: str,
    suggestion_mailjet_custom_id: str,
) -> SuggestionServiceInterface:
    return MailjetSuggestionService(
        mailjet_client=Client(
            auth=(suggestion_mailjet_rest_api_key, suggestion_mailjet_rest_api_secret),
            version="v3.1",
        ),
        suggestion_sender_name=suggestion_sender_name,
        suggestion_sender_email=suggestion_sender_email,
        suggestion_recipient_name=suggestion_recipient_name,
        suggestion_recipient_email=suggestion_recipient_email,
        suggestion_mailjet_custom_id=suggestion_mailjet_custom_id,
    )
