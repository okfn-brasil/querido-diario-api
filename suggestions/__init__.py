from .model import Suggestion

from .service import (
    SuggestionServiceInterface,
    MailjetSuggestionService,  # only for test
    create_suggestion_service,
)
