from rest_framework.serializers import (
    Serializer,
    CharField,
    BooleanField,
    IntegerField,
)


class TestSerializer(Serializer):

    ok = BooleanField(read_only=True)
    id = IntegerField(read_only=True)
    result = CharField(read_only=True)
    error = CharField(read_only=True)


class TestingSerializer(Serializer):

    code = CharField(write_only=True)
    ok = BooleanField(read_only=True)
    tests = TestSerializer(many=True, read_only=True)


class CreateSolutionSerializer(Serializer):

    code = CharField(write_only=True)
    elapsed = IntegerField(
        write_only=True,
        required=False,
        default=0,
        min_value=0
    )