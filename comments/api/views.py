from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response

from comments.api.permissions import IsObjectOwner
from comments.models import Comment
from comments.api.serializers import (
    CommentSerializer,
    CommentSerializerForCreate, CommentSerializerForUpdate,
)
from inbox.services import NotificationService
from utils.decorators import required_params

class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializerForCreate
    queryset = Comment.objects.all()
    filter_fields = ('tweet_id',)

    """
    POST /api/comments/ -> create
    GET /api/comments/ -> list
    GET /api/comments/1/ -> retrieve 
    DELETE /api/comments/1/ -> destroy
    PATCH /api/comments/1/ -> partial_update
    PUT /api/comments/1/ -> update
    """

    def get_permissions(self):
        if self.action == 'create':
            return [IsAuthenticated()]
        if self.action in ['update', 'destroy']:
            return [IsAuthenticated(), IsObjectOwner()]
        return [AllowAny()]

    @required_params(params=['tweet_id'])
    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        comments = self.filter_queryset(queryset).order_by('created_at')
        serializer = CommentSerializer(
            comments,
            context={'request': request},
            many=True,
        )
        return Response(
            {'comments': serializer.data},
            status=status.HTTP_200_OK,
        )

    def create(self, request, *args, **kwargs):
        data = {
            'user_id': request.user.id,
            'tweet_id': request.data.get('tweet_id'),
            'content': request.data.get('content')
        }

        serializer = CommentSerializerForCreate(data=data)
        if not serializer.is_valid():
            return Response({
                'message': 'Please check input',
                'errors': serializer.errors,
            }, status=status.HTTP_400_BAD_REQUEST)

        comment = serializer.save()
        NotificationService.send_comment_notification(comment)
        return Response(
            CommentSerializer(comment, context={"request": request}).data,
            status=status.HTTP_201_CREATED,
        )

    def update(self, request, *arg, **kwargs):
        # get_object ??? DRF ???????????????????????????????????????????????? raise 404 error
        # ?????????????????????????????????
        serializer = CommentSerializerForUpdate(
            instance=self.get_object(),
            data=request.data,
        )
        if not serializer.is_valid():
            return Response({
                'message': 'Please check input',
                'errors': serializer.errors,
            }, status=status.HTTP_400_BAD_REQUEST)
        # save ??????????????? serializer ?????? update ??????????????? save ??????????????????????????????
        # save ????????? instance ???????????????????????????????????? create ?????? update
        comment = serializer.save()
        return Response(
            CommentSerializer(comment, context={'request': request}).data,
            status=status.HTTP_200_OK,
        )

    def destroy(self, request, *args, **kwargs):
        comment = self.get_object()
        comment.delete()
        # DRF ????????? destroy ???????????? status code = 204 no content
        # ?????? return ??? success=True ?????????????????????????????????????????? return 200 ?????????
        return Response({'success': True}, status=status.HTTP_200_OK)

