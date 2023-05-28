from rest_framework import mixins
from rest_framework.viewsets import GenericViewSet


class CreateListRetrieveModelViewSet(mixins.CreateModelMixin,
                                     mixins.ListModelMixin,
                                     mixins.RetrieveModelMixin,
                                     GenericViewSet):
    """"""
