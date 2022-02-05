from django.contrib.auth import get_user_model
from rest_framework import status, permissions, pagination
from rest_framework.generics import ListAPIView
from rest_framework.views import APIView
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from users.serializers import ListFollowSerializer
from users.models import Follow

User = get_user_model()


class FollowApiView(APIView):
    def post(self, request, pk):
        user = request.user
        following = get_object_or_404(User, id=pk)
        if user == following:
            return Response(
                {'error': "You can't sunscribe on yourself"},
                status=status.HTTP_400_BAD_REQUEST
            )
        if Follow.objects.filter(user=user, following=following).exists():
            return Response(
                {'error': 'You already subscribed on this user'},
                status=status.HTTP_400_BAD_REQUEST
            )
        create_follow = Follow.objects.create(user=user, following=following)
        serializer = ListFollowSerializer(
            create_follow, context={'request': request}
        )
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete(self, request, pk):
        user = request.user
        following = get_object_or_404(User, id=pk)
        delete_follow = Follow.objects.filter(user=user, following=following)
        if delete_follow.exists():
            delete_follow.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(status=status.HTTP_400_BAD_REQUEST)


class FollowListViewSet(ListAPIView):
    queryset = Follow.objects.all()
    permission_classes = [permissions.IsAuthenticated,]
    serializer_class = ListFollowSerializer
    pagination_class = pagination.PageNumberPagination

    def get_queryset(self):
        return Follow.objects.filter(user=self.request.user)