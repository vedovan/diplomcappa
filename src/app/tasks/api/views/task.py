from rest_framework.authentication import TokenAuthentication
from rest_framework.viewsets import GenericViewSet
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from app.tasks.models import (
    Draft,
    Task
)
from app.tasks.api.serializers.draft import (
    DraftSerializer
)


class TaskViewSet(GenericViewSet):

    queryset = Task.objects.all()
    serializer_class = None
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get_serializer_class(self):
        if self.action == 'draft':
            return DraftSerializer

    @action(methods=('POST',), detail=True)
    def draft(self, request, pk):
        slz = self.get_serializer(data=request.data)
        slz.is_valid(raise_exception=True)
        content = slz.validated_data['content']
        translator = slz.validated_data['translator']
        elapsed = slz.validated_data.get('elapsed', 0)
        draft, created = Draft.objects.get_or_create(
            translator=translator,
            user=request.user,
            task_id=pk,
            defaults={"content": content}
        )

        draft.content = content

        if draft.time_spent is None:
            draft.time_spent = 0
        draft.time_spent += elapsed

        from app.tasks.models import Solution
        solution = Solution.objects.filter(task_id=pk, user=request.user).first()
        if solution:
            solution.started_at = timezone.now()
            solution.save(update_fields=["started_at"])

        draft.save(update_fields=('content', 'time_spent'))

        return Response()
