from django.contrib.auth import get_user_model, authenticate, login
from django.db.models import Q
from django.utils import timezone
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.decorators import api_view, permission_classes
from .models import FriendRequest, Friendship, User
from .serializers import UserSerializer, FriendRequestSerializer, FriendshipSerializer



# User = get_user_model()

class UserSignup(APIView):
    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')
        first_name = request.data.get('first_name')
        last_name = request.data.get('last_name')

        if User.objects.filter(email=email).exists():
            return Response({"error": "User with this email already exists."}, status=status.HTTP_400_BAD_REQUEST)
        user = User.objects.create_user(first_name=first_name,last_name=last_name,username=email.split('@')[0], email=email, password=password)
        return Response(UserSerializer(user).data)



class UserLogin(APIView):
    def post(self, request):
        email = request.data.get('email', '').lower().strip()
        password = request.data.get('password', '').strip()

        try:
            user = User.objects.get(email__iexact=email)
        except User.DoesNotExist:
            return Response({"error": "Invalid credentials."}, status=status.HTTP_400_BAD_REQUEST)
        user = authenticate(email=user.email, password=password)
        if user is not None:
            login(request, user)
            return Response(UserSerializer(user).data)
        return Response({"error": "Invalid credentials."}, status=status.HTTP_400_BAD_REQUEST)

class UserSearch(generics.ListAPIView):
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        keyword = self.request.query_params.get('q', '').strip()
        if '@' in keyword:
            return User.objects.filter(email__iexact=keyword)
        return User.objects.filter(Q(username__icontains=keyword) | Q(first_name__icontains=keyword) | Q(last_name__icontains=keyword)).distinct()

class FriendRequestCreate(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        to_user_id = request.data.get('to_user')
        from_user_id = request.user.id

        try:
            to_user = User.objects.get(pk=int(to_user_id))
            from_user = User.objects.get(pk=int(from_user_id))
        except User.DoesNotExist:
            return Response({'error': 'User does not exists.'}, status=status.HTTP_404_NOT_FOUND)

        if FriendRequest.objects.filter(from_user=from_user, to_user=to_user).exists():
            return Response({"error": "Friend request already sent."}, status=status.HTTP_400_BAD_REQUEST)

        FriendRequest.objects.create(from_user=from_user, to_user=to_user)
        return Response({"success": "Friend request sent."}, status=status.HTTP_201_CREATED)

class FriendRequestManage(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, request_id):
        action = request.data.get('action')
        try:
            friend_request = FriendRequest.objects.get(id=request_id)
        except FriendRequest.DoesNotExist:
            return Response({"error": "Friend request not found."}, status=status.HTTP_404_NOT_FOUND)

        if action == 'accept':
            Friendship.objects.create(user1=friend_request.from_user, user2=friend_request.to_user)
            Friendship.objects.create(user1=friend_request.to_user, user2=friend_request.from_user)
            friend_request.delete()
            return Response({"success": "Friend request accepted."})
        elif action == 'reject':
            friend_request.delete()
            return Response({"success": "Friend request rejected."})
        return Response({"error": "Invalid action."}, status=status.HTTP_400_BAD_REQUEST)

class ListFriends(generics.ListAPIView):
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        friendships = Friendship.objects.filter(user1=self.request.user)
        friends_ids = [friendship.user2.id for friendship in friendships]
        return User.objects.filter(id__in=friends_ids)

class ListPendingRequests(generics.ListAPIView):
    serializer_class = FriendRequestSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return FriendRequest.objects.filter(to_user=self.request.user)

