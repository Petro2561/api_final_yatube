from django.shortcuts import get_object_or_404
from posts.models import Group, Post
from rest_framework import filters, mixins, viewsets
from rest_framework.pagination import LimitOffsetPagination

from .permissions import IsAuthOnly, IsAuthorOrReadOnly
from .serializers import (CommentSerializer, FollowSerializer, GroupSerializer,
                          PostSerializer)


class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = (IsAuthorOrReadOnly,)
    pagination_class = LimitOffsetPagination

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class GroupViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Group.objects.all()
    serializer_class = GroupSerializer


class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    permission_classes = (IsAuthorOrReadOnly,)

    def get_post(self):
        return get_object_or_404(Post, id=self.kwargs['post_id'])

    def perform_create(self, serializer):
        serializer.save(author=self.request.user, post=self.get_post())

    def get_queryset(self):
        post = self.get_post()
        return post.comments.all()


class CreateRetrieveViewSet(mixins.CreateModelMixin, mixins.RetrieveModelMixin,
                            mixins.ListModelMixin, viewsets.GenericViewSet):
    pass


class FollowViewSet(CreateRetrieveViewSet):
    permission_classes = (IsAuthOnly,)
    serializer_class = FollowSerializer
    filter_backends = (filters.SearchFilter,)
    search_fields = ('following__username',)

    def get_queryset(self):
        return self.request.user.follower

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
