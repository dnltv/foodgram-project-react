from typing import Optional

from django.contrib.auth import get_user_model
from django.db.models.query import QuerySet
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response

from .models import Follow
from .serializers import SubscribeSerializer


User = get_user_model()


class SubscribeCreateDelete:
    def __init__(
            self,
            request: Request,
            user_queryset: QuerySet,
            following_user_id: Optional[int]
    ) -> None:
        self.request: Request = request
        self.user: User = request.user
        self.user_queryset: QuerySet = user_queryset
        self.following_user_id: Optional[int] = following_user_id

    def get_subscription_serializer(self) -> SubscribeSerializer:
        queryset = self.user_queryset.prefetch_related('recipes')
        following = self._get_following_or_404(queryset)
        return SubscribeSerializer(instance=following)

    def create_subscribe(self) -> Response:
        following = self._get_following_or_404()
        if self.user == following:
            return Response(
                {"Can't subscribe to yourself"},
                status.HTTP_400_BAD_REQUEST,
            )
        if self._is_follow_exists(following):
            return Response(
                {"Can't subscribe twice"},
                status.HTTP_400_BAD_REQUEST,
            )

        Follow.objects.create(user=self.user, following=following)
        serializer = self.get_subscription_serializer()
        return Response(serializer.data, status.HTTP_201_CREATED)

    def delete_subscribe(self) -> Response:
        following = self._get_following_or_404()
        if not self._is_follow_exists(following):
            return Response(
                {"Cant' unsubscribed, if you're not subscribed"},
                status.HTTP_400_BAD_REQUEST,
            )
        Follow.objects.get(user=self.user, following=following).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    def _is_follow_exists(self, following: User) -> bool:
        return Follow.objects.filter(
            user=self.user,
            following=following
        ).exists()

    def _get_following_or_404(
            self,
            queryset: QuerySet = User.objects.all()
    ) -> User:
        return get_object_or_404(
            queryset,
            id=self.following_user_id,
        )