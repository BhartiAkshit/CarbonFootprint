from django.core.mail import send_mail
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.utils.crypto import get_random_string
from django.conf import settings
from django.core.cache import cache
from django.utils import timezone
from datetime import timedelta
import json
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import generics, status,viewsets
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from adminapp.models import EmissionReductionTip
from adminapp.serializers import EmissionReductionTipSerializer
from .models import Profile,Fuel_used,DailyFoodChoice, DailyStreak, Favorite, EmissionGoal
from .serializers import (ProfileSerializer, Fuel_usedSerializer,DailyFoodChoiceSerializer, DailyStreakSerializer, 
                          FavoriteSerializer, EmissionGoalSerializer, LeaderboardSerializer, TotalEmissionAndGoalDifferenceSerializer)
from django.contrib.auth.models import User
from django.db import IntegrityError, transaction
from django.core.exceptions import ObjectDoesNotExist
import calendar
from rest_framework import serializers

# @csrf_exempt
# @require_POST
# def register(request):
#     data = json.loads(request.body.decode('utf-8'))

#     if 'email' not in data:
#         return JsonResponse({'error': 'Email address is required'}, status=400)

#     email = data['email']
#     otp = get_random_string(length=6, allowed_chars='0123456789')

#     cache.set(email, otp, timeout=300)
#     username = email.split('@')[0]
#     user = User(username=username, email=email)

#     subject = 'Registration OTP'
#     message = f'Your OTP for registration is: {otp}'
#     from_email = settings.DEFAULT_FROM_EMAIL
#     recipient_list = [email]

#     try:
#         user.save()
#         send_mail(subject, message, from_email, recipient_list)
#         return JsonResponse({'message': 'OTP sent successfully'}, status=200)
#     except IntegrityError:
#         return JsonResponse({'error': 'Username or email already exists. Please try again.'}, status=400)
#     except Exception as e:
#         return JsonResponse({'error': f'Error saving user or sending email: {str(e)}'}, status=500)

    

# User = get_user_model()

# @csrf_exempt
# @require_POST
# def verify_otp(request):
#     data = json.loads(request.body.decode('utf-8'))

#     if 'email' not in data or 'otp' not in data:
#         return JsonResponse({'error': 'Email and OTP are required'}, status=400)

#     email = data['email']
#     user_entered_otp = data['otp']
#     stored_otp = cache.get(email)

#     if stored_otp is None:
#         return JsonResponse({'error': 'OTP expired or not found. Please request a new OTP.'}, status=400)
#     if user_entered_otp == stored_otp:
#         user, created = User.objects.get_or_create(email=email)
#         refresh = RefreshToken.for_user(user)
#         access_token = str(refresh.access_token)
#         return JsonResponse({'message': 'OTP verified successfully', 'access_token': access_token}, status=200)
#     else:
#         return JsonResponse({'error': 'Invalid OTP'}, status=400)


User = get_user_model()

@csrf_exempt
@require_POST
def register(request):
    try:
        with transaction.atomic():
            data = json.loads(request.body.decode('utf-8'))

            if 'email' not in data:
                return JsonResponse({'error': 'Email address is required'}, status=400)

            email = data['email']
            otp = get_random_string(length=6, allowed_chars='0123456789')

            cache.set(email, otp, timeout=300)
            username = email.split('@')[0]
            user = User(username=username, email=email)

            subject = 'Registration OTP'
            message = f'Your OTP for registration is: {otp}'
            from_email = settings.DEFAULT_FROM_EMAIL
            recipient_list = [email]

            user.save()
            send_mail(subject, message, from_email, recipient_list)

            return JsonResponse({'message': 'OTP sent successfully'}, status=200)

    except IntegrityError:
        return JsonResponse({'error': 'Username or email already exists. Please try again.'}, status=400)
    except Exception as e:
        return JsonResponse({'error': f'Error saving user or sending email: {str(e)}'}, status=500)

@csrf_exempt
@require_POST
def verify_otp(request):
    try:
        with transaction.atomic():
            data = json.loads(request.body.decode('utf-8'))

            if 'email' not in data or 'otp' not in data:
                return JsonResponse({'error': 'Email and OTP are required'}, status=400)

            email = data['email']
            user_entered_otp = data['otp']
            stored_otp = cache.get(email)

            if stored_otp is None:
                return JsonResponse({'error': 'OTP expired or not found. Please request a new OTP.'}, status=400)

            if user_entered_otp == stored_otp:
                user = User.objects.get(email=email)
                refresh = RefreshToken.for_user(user)
                access_token = str(refresh.access_token)
                return JsonResponse({'message': 'OTP verified successfully', 'access_token': access_token}, status=200)
            else:
                return JsonResponse({'error': 'Invalid OTP'}, status=400)

    except ObjectDoesNotExist:
        return JsonResponse({'error': 'User not found. Please register first.'}, status=400)
    except Exception as e:
        return JsonResponse({'error': f'Error verifying OTP: {str(e)}'}, status=500)
    
@csrf_exempt
@require_POST
def resend_otp(request):
    data = json.loads(request.body.decode('utf-8'))

    if 'email' not in data:
        return JsonResponse({'error': 'Email address is required'}, status=400)

    email = data['email']
    user = User.objects.filter(email=email).first()

    if user is None:
        return JsonResponse({'error': 'User not found with the provided email'}, status=404)
    new_otp = get_random_string(length=6, allowed_chars='0123456789')
    cache.set(email, new_otp, timeout=300)
    subject = 'Registration OTP'
    message = f'Your new OTP for registration is: {new_otp}'
    from_email = settings.DEFAULT_FROM_EMAIL
    recipient_list = [email]

    try:
        send_mail(subject, message, from_email, recipient_list)
        return JsonResponse({'message': 'New OTP sent successfully'}, status=200)
    except Exception as e:
        return JsonResponse({'error': f'Error sending email: {str(e)}'}, status=500)



class FuelUsedListView(generics.ListCreateAPIView):
    serializer_class = Fuel_usedSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Fuel_used.objects.filter(owner=self.request.user)

    def perform_create(self, serializer):
        owner = self.request.user
        serializer.save(owner=owner)
        fuel_entry = serializer.instance
        fuel_entry.total_emission = fuel_entry.calculate_total_carbon_emissions()
        fuel_entry.save()

        return Response({"detail": "Fuel used data added successfully for the current month."}, status=status.HTTP_201_CREATED)


class FuelUsedDetailView(APIView):
    serializer_class = Fuel_usedSerializer
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user_id = request.data.get('user_id', self.request.user.id)
        month = request.data.get('month', timezone.now().month)

        try:
            fuel_entries = Fuel_used.objects.filter(
                owner=user_id,
                entry_date__month=month
            )
            serializer = Fuel_usedSerializer(fuel_entries, many=True)
            return Response(serializer.data)
        except Fuel_used.DoesNotExist:
            return Response({"detail": "Fuel used detail does not exist for the provided user and month."}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"detail": f"An error occurred: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


    def put(self, request):
        user_id = request.data.get('user_id', self.request.user.id)
        fuel_entry = Fuel_used.objects.get(owner=user_id)
        serializer = Fuel_usedSerializer(fuel_entry, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request):
        user_id = request.data.get('user_id', self.request.user.id)
        fuel_entry = Fuel_used.objects.get(owner=user_id)
        fuel_entry.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

# class ProfileListView(generics.ListCreateAPIView):
#     serializer_class = ProfileSerializer
#     permission_classes = [IsAuthenticated]

#     def get_queryset(self):
#         return Profile.objects.filter(owner=self.request.user)

#     def perform_create(self, serializer):
#         serializer.save(owner=self.request.user)

# class ProfileDetailView(APIView):
#     serializer_class = ProfileSerializer
#     permission_classes = [IsAuthenticated]

#     def get(self, request):
#         user_id = request.data.get('user_id', self.request.user.id)
#         profile = Profile.objects.get(owner=user_id)
#         serializer = ProfileSerializer(profile)
#         return Response(serializer.data)

#     def put(self, request):
#         user_id = request.data.get('user_id', self.request.user.id)
#         profile = Profile.objects.get(owner=user_id)
#         serializer = ProfileSerializer(profile, data=request.data)
#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

#     def delete(self, request):
#         user_id = request.data.get('user_id', self.request.user.id)
#         profile = Profile.objects.get(owner=user_id)
#         profile.delete()
#         return Response(status=status.HTTP_204_NO_CONTENT)

class ProfileListView(generics.ListCreateAPIView):
    serializer_class = ProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Profile.objects.filter(owner=self.request.user)

    def perform_create(self, serializer):
        # Check if the user already has a profile
        existing_profile = Profile.objects.filter(owner=self.request.user).first()
        if existing_profile:
            # If a profile already exists, return an error message
            raise serializers.ValidationError("Profile already created for this user")
        serializer.save(owner=self.request.user)


class ProfileDetailView(APIView):
    serializer_class = ProfileSerializer
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user_id = request.data.get('user_id', self.request.user.id)
        try:
            profile = Profile.objects.get(owner=user_id)
        except Profile.DoesNotExist:
            # If the profile doesn't exist, create a new instance with default values
            user = User.objects.get(id=user_id)
            profile = Profile(owner=user)

        serializer = ProfileSerializer(profile)
        return Response(serializer.data)

    def patch(self, request):
        user_id = request.data.get('user_id', self.request.user.id)
        try:
            profile = Profile.objects.get(owner=user_id)
            serializer = ProfileSerializer(profile, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Profile.DoesNotExist:
            return Response({"detail": "Profile not found"}, status=status.HTTP_404_NOT_FOUND)

    def delete(self, request):
        user_id = request.data.get('user_id', self.request.user.id)
        try:
            profile = Profile.objects.get(owner=user_id)
            profile.delete()
            return Response({"message":"deleted"}, status=status.HTTP_204_NO_CONTENT)
        except Profile.DoesNotExist:
            return Response({"detail": "Profile not found"}, status=status.HTTP_404_NOT_FOUND)

class EmissionRecordView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        current_user = request.user
        current_month_start = timezone.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)

        _, last_day = calendar.monthrange(current_month_start.year, current_month_start.month)
        current_month_end = current_month_start.replace(day=last_day, hour=23, minute=59, second=59, microsecond=999999)

        # Fetch fuel entries for the current month
        current_month_fuel_entries = Fuel_used.objects.filter(
            owner=current_user,
            entry_date__range=[current_month_start, current_month_end]
        )

        # Calculate total fuel emissions for the current month
        current_month_fuel_emissions = sum(entry.calculate_total_carbon_emissions() for entry in current_month_fuel_entries)

        # Fetch food entries for the current month
        current_month_food_entries = DailyFoodChoice.objects.filter(
            owner=current_user,
            entry_date__range=[current_month_start, current_month_end]
        )

        # Calculate total food emissions for the current month
        current_month_food_emissions = sum(entry.total_food_emission for entry in current_month_food_entries)

        # Total emissions for the current month
        current_month_emissions = current_month_fuel_emissions + current_month_food_emissions

        past_months_data = []

        for i in range(1, 6):
            start_date = current_month_start - timedelta(days=current_month_start.day)
            end_date = current_month_start - timedelta(microseconds=1)

            # Fetch fuel entries for the past month
            month_fuel_entries = Fuel_used.objects.filter(
                owner=current_user,
                entry_date__range=[start_date, end_date]
            )

            # Calculate total fuel emissions for the past month
            total_fuel_emissions = sum(entry.calculate_total_carbon_emissions() for entry in month_fuel_entries)

            # Fetch food entries for the past month
            month_food_entries = DailyFoodChoice.objects.filter(
                owner=current_user,
                entry_date__range=[start_date, end_date]
            )

            # Calculate total food emissions for the past month
            total_food_emissions = sum(entry.total_food_emission for entry in month_food_entries)

            # Total emissions for the past month
            total_emissions = total_fuel_emissions + total_food_emissions

            past_months_data.append({
                'month': start_date.strftime('%B %Y'),
                'total_emissions': total_emissions,
            })
            current_month_start = start_date - timedelta(days=1)

        response_data = {
            'current_month_emissions': current_month_emissions,
            'past_months_emissions': past_months_data,
        }

        return Response(response_data, status=status.HTTP_200_OK)



# class DailyFoodChoiceListView(generics.ListCreateAPIView): 
#     serializer_class = DailyFoodChoiceSerializer 
#     permission_classes = [IsAuthenticated] 

#     def get_queryset(self): 
#         return DailyFoodChoice.objects.filter(owner=self.request.user)  
#     def perform_create(self, serializer): 
#         serializer.save(owner=self.request.user) 

# class DailyFoodChoiceDetailView(APIView): 
#     serializer_class = DailyFoodChoiceSerializer 
#     permission_classes = [IsAuthenticated] 
 
#     def get(self, request): 
#         user_id = request.data.get('user_id', self.request.user.id) 
#         entry_date = request.data.get('entry_date', timezone.now().date()) 
#         food_choices = DailyFoodChoice.objects.filter(owner=user_id, entry_date=entry_date) 

#         if not food_choices.exists(): 
#             return Response({"detail": "Daily food choice does not exist for the provided user and date."}, 
#                             status=status.HTTP_404_NOT_FOUND) 

#         serializer = DailyFoodChoiceSerializer(food_choices, many=True) 
#         return Response(serializer.data) 

    # def put(self, request): 
    #     user_id = request.data.get('user_id', self.request.user.id) 
    #     entry_date = request.data.get('entry_date', timezone.now().date())          
    #     food_choices = DailyFoodChoice.objects.filter(owner=user_id, entry_date=entry_date)  

    #     if not food_choices.exists(): 
    #         return Response({"detail": "Daily food choice does not exist for the provided user and date."}, 
    #                         status=status.HTTP_404_NOT_FOUND) 
    #     food_choice = food_choices.first() 
    #     serializer = DailyFoodChoiceSerializer(food_choice, data=request.data) 
    #     if serializer.is_valid(): 
    #         serializer.save() 
    #         return Response(serializer.data) 
    #     return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST) 

class DailyFoodChoiceListView(generics.ListCreateAPIView):
    serializer_class = DailyFoodChoiceSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return DailyFoodChoice.objects.filter(owner=self.request.user)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

class DailyFoodChoiceDetailView(APIView):
    serializer_class = DailyFoodChoiceSerializer
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user_id = request.data.get('user_id', self.request.user.id)
        entry_date = request.data.get('entry_date', timezone.now().date())
        food_choices = DailyFoodChoice.objects.filter(owner=user_id, entry_date=entry_date)

        if not food_choices.exists():
            return Response({"detail": "Daily food choice does not exist for the provided user and date."},
                            status=status.HTTP_404_NOT_FOUND)

        serializer = DailyFoodChoiceSerializer(food_choices, many=True)
        return Response(serializer.data)

    # def patch(self, request):
    #     user_id = request.data.get('user_id', self.request.user.id)
    #     entry_date = request.data.get('entry_date', timezone.now().date())

    #     try:
    #         food_choice = DailyFoodChoice.objects.filter(owner=user_id, entry_date=entry_date)
    #     except DailyFoodChoice.DoesNotExist:
    #         return Response({"detail": "Daily food choice does not exist for the provided user and date."},
    #                         status=status.HTTP_404_NOT_FOUND)

    #     serializer = DailyFoodChoiceSerializer(food_choice, data=request.data, partial=True)
    #     if serializer.is_valid():
    #         serializer.save()
    #         return Response(serializer.data)
    #     return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
   


    


class DailyStreakAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        try:
            daily_streak, created = DailyStreak.objects.get_or_create(user=request.user)
            daily_streak.update_streak()
            serializer = DailyStreakSerializer(daily_streak)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        

class AllEmissionReductionTipsView(generics.ListAPIView):
    queryset = EmissionReductionTip.objects.all()
    serializer_class = EmissionReductionTipSerializer




# class FavoriteCreateView(APIView):
#     permission_classes = [IsAuthenticated]



#     def get(self, request, *args, **kwargs):
#         favorites = Favorite.objects.filter(user=request.user)
#         serializer = FavoriteSerializer(favorites, many=True)
#         return Response(serializer.data)


#     def post(self, request, *args, **kwargs):
#         tip_id = request.data.get('tip_id')

#         try:
#             tip = EmissionReductionTip.objects.get(id=tip_id)
#         except EmissionReductionTip.DoesNotExist:
#             return Response({'error': 'Tip not found'}, status=status.HTTP_404_NOT_FOUND)

#         serializer = FavoriteSerializer(data={'user': request.user.id, 'tip': tip_id})
#         serializer.is_valid(raise_exception=True)
#         serializer.save()

#         return Response(serializer.data, status=status.HTTP_201_CREATED)

class FavoriteCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        favorites = Favorite.objects.filter(user=request.user)
        serializer = FavoriteSerializer(favorites, many=True)
        return Response(serializer.data)

    def post(self, request, *args, **kwargs):
        tip_id = request.data.get('tip_id')

        try:
            tip = EmissionReductionTip.objects.get(id=tip_id)
        except EmissionReductionTip.DoesNotExist:
            return Response({'error': 'Tip not found'}, status=status.HTTP_404_NOT_FOUND)

        # Check if the favorite already exists
        existing_favorite = Favorite.objects.filter(user=request.user, tip=tip)
        if existing_favorite.exists():
            return Response({'error': 'Tip already added to favorites'}, status=status.HTTP_400_BAD_REQUEST)

        serializer = FavoriteSerializer(data={'user': request.user.id, 'tip': tip_id})
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_201_CREATED)
    


class EmissionGoalView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            user_goal = request.user.emission_goal
        except EmissionGoal.DoesNotExist:
            return Response({"detail": "Emission goal not set"}, status=status.HTTP_404_NOT_FOUND)

        serializer = EmissionGoalSerializer(user_goal)
        response_data = {"id": user_goal.id, **serializer.data}
        return Response(response_data)
    
    def post(self, request):
        if hasattr(request.user, 'emission_goal'):
            return Response({"detail": "You have already set the goal"}, status=status.HTTP_400_BAD_REQUEST)

        serializer = EmissionGoalSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(owner=request.user)
            response_data = {"id": serializer.instance.id, **serializer.data}
            return Response(response_data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


    def patch(self, request):
        user_goal = request.user.emission_goal
        request_data = request.data.copy()
        if 'id' not in request_data:
            return Response({"detail": "ID is required in the request body"}, status=status.HTTP_400_BAD_REQUEST)

        serializer = EmissionGoalSerializer(user_goal, data=request_data)
        if serializer.is_valid():
            serializer.save()
            return Response("message: Baby Your Data is Updated")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


    def delete(self, request):
        request_data = request.data.copy()

        if 'id' not in request_data:
            return Response({"detail": "ID is required in the request body"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user_goal = request.user.emission_goal
        except EmissionGoal.DoesNotExist:
            return Response({"detail": "You have no emission goal"}, status=status.HTTP_404_NOT_FOUND)

        user_goal.delete()
        return Response("Deleted successfully", status=status.HTTP_204_NO_CONTENT)
    



class LeaderboardView(APIView):

    permission_classes = [IsAuthenticated] 
    def get(self, request): 
        top_profiles = Profile.objects.order_by('total_carbon_emissions')[:10] 
        leaderboard_data = LeaderboardSerializer(top_profiles, many=True).data 
        return Response(leaderboard_data, status=status.HTTP_200_OK) 
    



class TotalEmissionAndGoalDifferenceView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user_profile = request.user.profile_data
        emission_goal = EmissionGoal.objects.filter(owner=request.user).first()

        if not emission_goal:
            return Response({"detail": "Emission goal not set"}, status=400)

        total_emission = user_profile.get_total_emissions()
        total_goal = emission_goal.total_goal
        difference = total_goal - total_emission

        data = {
            "total_emission": total_emission,
            "total_goal": total_goal,
            "difference": difference,
        }

        serializer = TotalEmissionAndGoalDifferenceSerializer(data)
        return Response(serializer.data)


