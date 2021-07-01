from .model import (
    Suggestion,
    SuggestionSent,
)

from .service import (
    SuggestionServiceInterface,
    MailjetSuggestionService,  # only for test
    create_suggestion_service,
)
