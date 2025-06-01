from rest_framework.serializers import (
    Serializer,
    CharField,
    ChoiceField,
    IntegerField,
)
from app.translators.enums import TranslatorType


class DraftSerializer(Serializer):

    content = CharField(required=True)
    translator = ChoiceField(
        required=True,
        choices=TranslatorType.CHOICES
    )
    elapsed = IntegerField(
        required=False,
        default=0,
        min_value=0
    )