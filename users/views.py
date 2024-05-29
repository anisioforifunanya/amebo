from rest_framework.response import Response
from django.contrib.auth import authenticate, login, logout
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.throttling import AnonRateThrottle, UserRateThrottle
from .serializers import *
from events.serializers import EventsSerializer
from events.models import Events
from jobs.serializers import JobsSerializer
from jobs.models import Jobs
from posts.serializers import PostsSerializer
from posts.models import Posts
from store.serializers import StoreSerializer
from store.models import Store
from .models import *
from rest_framework import permissions, status
from rest_framework.generics import GenericAPIView
from ameboConfig.permissions import Registration, IsAdminOrReadOnly
from ameboConfig.common import ResponseModelViewSet, CustomResponse, error_handler, CustomValidationError
from django.db.models import Max, Q
from rest_framework.views import APIView
import django.contrib.auth.password_validation as validators
import hashlib
from cloudinary.uploader import upload, destroy
from rest_framework.parsers import MultiPartParser, JSONParser
from django_filters.rest_framework import DjangoFilterBackend
from django.http import HttpResponse
from django.db.models import Q


class LoginView(GenericAPIView):
    """Login view for accessing the app"""
    serializer_class = LoginSerializer
    permission_classes = [permissions.AllowAny]
    throttle_classes = [AnonRateThrottle, UserRateThrottle]

    def post(self, request, *args, **kwargs):
        try:
            self.serializer = self.get_serializer(data=request.data)
            self.serializer.is_valid(raise_exception=True)
            # generate a token for that user, and login
            self.user = self.serializer.validated_data['user']
            refresh = RefreshToken.for_user(self.user)
            login(request, self.user)
            # get the user details of the logged in user
            user = AppUsers.objects.filter(owner=self.user)
            user_info = AppUsersSerializer(user.first()).data if user.exists() else []
            return Response({
                "status": "success",
                "refresh": str(refresh),
                "access": str(refresh.access_token),
                "data": user_info,
                "message": "Login successful",
            }, status=status.HTTP_200_OK)
        except Exception as e:
            print("Error: %s" % e)
            return CustomResponse.failed([], "Invalid login credentials")

class RegistrationView(GenericAPIView):
    """Registration view to signup a user"""
    serializer_class = RegistrationSerializer
    permission_classes = [permissions.AllowAny]
    throttle_classes = [AnonRateThrottle, UserRateThrottle]

    def post(self, request, *args, **kwargs):
        try:
            self.serializer = self.get_serializer(data=request.data)
            self.serializer.is_valid(raise_exception=True)
            # Create the user object
            email = self.serializer.validated_data.get('email')
            password = self.serializer.validated_data.get('password')
            username = self.serializer.validated_data.get('username')
            # try to see if that user already exists
            user_ = User.objects.filter(email=email)
            if user_.exists():
                raise Exception("A user with this email address already exists")

            # check if that username exists too
            username = AppUsers.objects.filter(username=username)
            if username.exists():
                raise Exception("A user with this username already exists")

            # create the user instance
            user = User.objects.create_user(email=email, password=password)

            # encode the user password and save it
            encode_current_password = password.encode()
            hash_current_password = hashlib.sha256(encode_current_password).hexdigest()
            user.recent_passwords.append(hash_current_password)
            user.save()

            # Create the related app user object
            user_data = {
                'owner': user,
                'username': self.serializer.validated_data.get('username'),
                'display_name': self.serializer.validated_data.get('display_name'),
                'gender': self.serializer.validated_data.get('gender'),
                'phone_number': self.serializer.validated_data.get('phone_number'),
            }
            app_user = AppUsers.objects.create(**user_data)
            user_info = AppUsersSerializer(app_user).data
            return Response({
                "status": "success",
                "data": user_info,
                "message": "Registration successful",
            }, status=status.HTTP_201_CREATED)
        except Exception as e:
            print("Error: %s" % str(e))
            return CustomResponse.failed([], error_handler(e))

class TokenRefreshView(GenericAPIView):
    """A view to refresh the access token, by using the refresh token"""
    serializer_class = TokenRefreshSerializer
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        try:
            self.serializer = self.get_serializer_class()
            self.serializer = self.serializer(data=request.data)
            self.serializer.is_valid(raise_exception=True)
            access_token = self.serializer.save()
            return CustomResponse.success(data=access_token, message="Token refresh successful")
        except Exception as e:
            return CustomResponse.failed(data=error_handler(e), message="Token refresh unsuccessful")

class LogoutView(GenericAPIView):
    """Logout view"""
    def post(self, request, *args, **kwargs):
        logout(request)
        return CustomResponse.success(message="Log out successful")

class UserViewSet(ResponseModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAdminOrReadOnly]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['email']

class AppUsersViewSet(ResponseModelViewSet):
    queryset = AppUsers.objects.all()
    permission_classes = [permissions.AllowAny]
    serializer_class = AppUsersSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['username', 'display_name', 'user_type', 'gender', 'is_verified', 'filled_all_info']

class ForgetPasswordView(GenericAPIView):
    serializer_class = ForgetPasswordSerializer
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        try:
            self.serializer = self.get_serializer_class()
            self.serializer = self.serializer(data=request.data)
            self.serializer.is_valid(raise_exception=True)
            self.serializer.save()
            return CustomResponse.success(message="Kindly check your mailbox, a password reset link has been sent")
        except Exception as e:
            error_message = error_handler(e)
            return CustomResponse.failed(data=error_message, message="Forget password reset link not sent")

class PasswordForgetView(GenericAPIView):
    serializer_class = PasswordForgetSerializer
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        try:
            self.serializer = self.get_serializer_class()
            self.serializer = self.serializer(data=request.data)
            self.serializer.is_valid(raise_exception=True)
            self.serializer.save()
            return CustomResponse.success(data=[], message="Password reset successfull")
        except Exception as e:
            error_message = error_handler(e)
            return CustomResponse.failed(data=error_message, message="Password reset unsuccessfull")

class ResetPasswordView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        current_password = request.data.get('current_password')
        new_password = request.data.get('new_password')
        confirm_password = request.data.get('confirm_password')

        user = request.user
        if not check_password(current_password, user.password):
            return CustomResponse.failed(message='The inputted current password is incorrect')

        # check if the new password meets the requirements
        try:
            validators.validate_password(password=new_password)
        # check if new_password and confirm_password are the same
        except Exception as e:
            error = CustomValidationError(e)
            return CustomResponse.failed(message=error)
        if new_password != confirm_password:
            return CustomResponse.failed(message='The new password and confirm password do not match')

        # encode new password
        encode_new_password = new_password.encode()
        # hash new password
        hash_new_password = hashlib.sha256(encode_new_password).hexdigest()
        # Check if new password is different from the last three passwords
        if hash_new_password in user.recent_passwords:
            return CustomResponse.failed(message='Kindly change the new password, as it has been previously used.')
        else:
            # Remove redundant password if the password list contains more than three passwords
            if len(user.recent_passwords) == 3:
                user.recent_passwords.pop(0)
            user.recent_passwords.append(hash_new_password)  # add the new password to the list of recent passwords
        user.set_password(new_password)  # Set new password for the user
        user.save()
        return CustomResponse.success(message='Password reset successful.')

class UploadProfilePictureView(APIView):
    """A view to upload the user's profile picture"""
    parser_classes = (MultiPartParser, JSONParser)

    @staticmethod
    def post(request):
        try:
            file = request.data.get('picture')
            # ensure it's a supported image type
            if file.name.split('.')[-1] not in ['png', 'jpg', 'jpeg', 'gif', 'webp']:
                return CustomResponse.failed(message='Invalid image, file type not supported')
            user = AppUsers.objects.filter(owner=request.user).first() # get the user
            # Check the size of the image
            image_size_bytes = file.size  # Get the size of the image file in bytes
            # Convert bytes to kilobytes
            image_size_kb = image_size_bytes / 1024
            # Ensure the image size is less than 1MB
            if image_size_kb > 1024 * 5: 
                return CustomResponse.failed(message='Image size exceeds 5MB limit')
            # If the image size is within limits, proceed with the upload
            upload_data = upload(file)
            image_url, public_id = upload_data['url'], upload_data['public_id']
            # delete the old profile picture from cloudinary
            if user.profile_pic_url is not None:
                url = user.profile_pic_url
                # get the profile picture id
                image_id = url.split(f'{user.username}/')[-1].split('.')[0]
                # construct the profile picture public_id
                image_public_id = f'{user.username}/{image_id}'
                destroy(image_public_id)
            # replace the former profile picture with the new one
            user.profile_pic_url = image_url
            user.save()
            return Response({
                'status': 'success',
                'data': upload_data,
            }, status=201)
        except Exception as e:
            return Response({
                'status': 'error',
                'message': f'Failed to upload image: {str(e)}',
            }, status=500)

class UploadVerifyPictureView(APIView):
    """A view to upload the user's verification picture"""
    parser_classes = (MultiPartParser, JSONParser)

    @staticmethod
    def post(request):
        try:
            file = request.data.get('picture')
            user = AppUsers.objects.filter(owner=request.user).first() # get the user

            # Check the size of the image
            image_size_bytes = file.size  # Get the size of the image file in bytes

            # Convert bytes to kilobytes
            image_size_kb = image_size_bytes / 1024

            # Ensure the image size is less than 1MB
            if image_size_kb > 1024 * 5:
                return CustomResponse.failed(message='Image size exceeds 5MB limit')

            # If the image size is within limits, proceed with the upload
            upload_data = upload(file)
            image_url, public_id = upload_data['url'], upload_data['public_id']
            user.verify_pic_url = image_url
            user.save()

            return Response({
                'status': 'success',
                'data': upload_data,
            }, status=201)
        except Exception as e:
            return Response({
                'status': 'error',
                'message': f'Failed to upload image: {str(e)}',
                'data': [],
            }, status=500)


class SuggestedPeopleView(APIView):
    """Returns a list of random suggested people"""

    def get_random_users(self, app_user):
        """Get up to 5 random users excluding the logged in user, admin users, and non-verified or removed users."""
        return AppUsers.objects.filter(
            user_type='user',
            is_verified=True,
            is_removed=False
        ).exclude(id=app_user.id).order_by('?')[:5]

    def get(self, request):
        try:
            # get the authenticated user
            app_user = AppUsers.objects.filter(owner=request.user).first()
            suggested_people = self.get_random_users(app_user)
            suggested_people_data = list(set([]))
            for user in suggested_people:
                suggested_people_data.append({
                    "id": user.id,
                    "username": user.username,
                    "display_name": user.display_name,
                    "profile_pic_url": user.profile_pic_url,
                    "is_following": user.username in app_user.following,
                    "followers": AppUsers.objects.filter(
                        following__icontains=user.username,
                        is_verified=True,
                        is_removed=False
                    ).count()
                })
            return CustomResponse.success(data=suggested_people_data, message='success') 
        except Exception as e:
            return CustomResponse.failed(message=str(e))


class UploadOtherPicturesView(APIView):
    """A view to upload other user picture(s)"""
    parser_classes = (MultiPartParser, JSONParser)

    @staticmethod
    def post(request):
        try:
            file = request.data.get('picture')
            # ensure it's a supported image type
            if file.name.split('.')[-1] not in ['png', 'jpg', 'jpeg', 'gif', 'webp']:
                return CustomResponse.failed(message='Invalid image, file type not supported')
            user = AppUsers.objects.filter(owner=request.user).first() # get the user

            # Check the size of the image
            image_size_bytes = file.size  # Get the size of the image file in bytes

            # Convert bytes to kilobytes
            image_size_kb = image_size_bytes / 1024 * 5

            # Ensure the image size is less than 1MB
            if image_size_kb > 1024 * 5: 
                return CustomResponse.failed(message='Image size exceeds 5MB limit')

            # If the image size is within limits, proceed with the upload
            upload_data = upload(file)
            image_url, public_id = upload_data['url'], upload_data['public_id']
            # add the picture url to the list of other pictures
            user.other_pics.append(image_url)
            user.save()
            return Response({
                'status': 'success',
                'data': upload_data,
            }, status=201)
        except Exception as e:
            return Response({
                'status': 'error',
                'message': f'Failed to upload image: {str(e)}',
                'data': [],
            }, status=500)

class SearchView(APIView):
    """This is used to search for a user, item, job, event, etc in the app"""
    permission_classes = [permissions.AllowAny]

    def get(self, request, *args, **kwargs):
        try:
            # get the category the search is coming from
            category = request.query_params.get('category', None)
            # get what the user is searching for
            query = request.query_params.get('query', None)
            if category == 'users':
                users = AppUsers.objects.filter(Q(username__icontains=query) | Q(display_name__icontains=query), user_type='user', is_verified=True, is_removed=False)
                if users.exists():
                    return Response({
                        'status': 'success',
                        'data': AppUsersSerializer(users, many=True).data,
                        'message': 'success'
                    }, status=200)
                else:
                    return Response({
                        'status': 'success',
                        'data': [],
                        'message': 'No user(s) found'
                    }, status=200)
            elif category == 'events':
                events = Events.objects.filter(Q(title__icontains=query) | Q(category__icontains=query) | Q(location__icontains=query))
                if events.exists():
                    return Response({
                        'status': 'success',
                        'data': EventsSerializer(events, many=True).data,
                        'message': 'success'
                    }, status=200)
                else:
                    return Response({
                        'status': 'success',
                        'data': [],
                        'message': 'No event(s) found'
                    }, status=200)
            elif category == 'jobs':
                jobs = Jobs.objects.filter(Q(title__icontains=query) | Q(description__icontains=query) | Q(location__icontains=query) | Q(employment_type__icontains=query) | Q(job_type__icontains=query))
                if jobs.exists():
                    return Response({
                        'status': 'success',
                        'data': JobsSerializer(jobs, many=True).data,
                        'message': 'success'
                    }, status=200)
                else:
                    return Response({
                        'status': 'success',
                        'data': [],
                        'message': 'No job(s) found'
                    }, status=200)
            elif category == 'posts':
                post = Posts.objects.filter(Q(content__icontains=query))
                if post.exists():
                    return Response({
                        'status': 'success',
                        'data': PostsSerializer(post, many=True).data,
                        'message': 'success'
                    }, status=200)
                else:
                    return Response({
                        'status': 'success',
                        'data': [],
                        'message': 'No post(s) found'
                    }, status=200)
            elif category == 'store':
                products = Store.objects.filter(Q(title__icontains=query) | Q(description__icontains=query) | Q(category__icontains=query) | Q(location__icontains=query))
                if products.exists():
                    return Response({
                        'status': 'success',
                        'data': StoreSerializer(products, many=True).data,
                        'message': 'success'
                    }, status=200)
                else:
                    return Response({
                        'status': 'success',
                        'data': [],
                        'message': 'No product(s) found'
                    }, status=200)
        except Exception as e:
            return Response({
                'status': 'error',
                'data': [],
                'message': str(e),
            }, status=400)


def index(request):
    return HttpResponse("Hello, world. This is the root page!")


class StatsView(APIView):
    """This returns the total number of users,, jobs, events, etc in the app"""
    permission_classes = [IsAdminOrReadOnly]

    def get(self, request, *args, **kwargs):
        try:
            data = {
                "users" : AppUsers.objects.filter(user_type='user', is_verified=True).count(),
                "jobs" : Jobs.objects.count(),
                "events" : Events.objects.count(),
                "products" : Store.objects.count(),
            }
            return Response({
                'status': 'success',
                'data': data,
                'message': 'success'
            }, status=200)
        except Exception as e:
            return Response({
                'status': 'error',
                'data': [],
                'message': str(e),
            }, status=400)

