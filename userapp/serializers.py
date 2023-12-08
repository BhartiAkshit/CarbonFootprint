from rest_framework import serializers
from django.contrib.auth.models import User
from django.utils import timezone
from .models import Fuel_used, Profile,DailyFoodChoice, DailyStreak, Favorite, EmissionGoal

class UserTotalEmissionsSerializer(serializers.Serializer):
    user_id = serializers.IntegerField()
    total_emissions = serializers.FloatField()

class Fuel_usedSerializer(serializers.ModelSerializer):
    entry_date = serializers.DateField()
    class Meta:
        model = Fuel_used
        fields = '__all__'
        read_only_fields = ('owner',)
    
    def validate_entry_date(self, value):
        today = timezone.now().date()

        if value < today:
            raise serializers.ValidationError("Cannot add fuel used data for a past date.")

        if value > today:
            raise serializers.ValidationError("Cannot add fuel used data for a future date.")

        return value

class UserSerializers(serializers.ModelSerializer):
    class Meta:
        model=User
        fields = ('id','username', 'email','password','is_active')
        extra_kwargs={'email':{'required':True,'write_only':True},'password':{'write_only':True}}

    def create(self,validate_data):
        user=User(
            email=validate_data['email'],
            username=validate_data['username']
        )

        user.set_password(validate_data['password'])
        user.save()
        return user 

class ProfileSerializer(serializers.ModelSerializer):
    owner = serializers.ReadOnlyField(source='owner.username')
    total_carbon_emissions = serializers.FloatField(source='get_total_emissions', read_only=True)
    class Meta:
        model = Profile
        fields = '__all__'

class DailyFoodChoiceSerializer(serializers.ModelSerializer): 
    class Meta: 
        model = DailyFoodChoice 

        fields = '__all__' 

        read_only_fields = ('owner', 'total_food_emission')


class DailyStreakSerializer(serializers.ModelSerializer):
    class Meta:
        model = DailyStreak
        fields = ['current_streak']


class FavoriteSerializer(serializers.ModelSerializer):
    user_username = serializers.ReadOnlyField(source='user.username')
    tip_text = serializers.ReadOnlyField(source='tip.tip_text')

    class Meta:
        model = Favorite
        fields = ['id', 'user', 'user_username', 'tip', 'tip_text', 'created_at']


class EmissionGoalSerializer(serializers.ModelSerializer): 
    class Meta: 
        model = EmissionGoal 
        fields = ('petrol_goal', 'diesel_goal', 'electricity_goal', 'food_goal', 'total_goal') 
        read_only_fields = ('total_goal',) 


class LeaderboardSerializer(serializers.Serializer): 
    username = serializers.CharField(source='owner.username', read_only=True) 
    total_emissions = serializers.FloatField(source='owner.profile_data.total_carbon_emissions', read_only=True) 


class TotalEmissionAndGoalDifferenceSerializer(serializers.Serializer):
    total_emission = serializers.FloatField(source='get_total_emissions', read_only=True)
    total_goal = serializers.FloatField(source='owner.emission_goal.total_goal', read_only=True)
    difference = serializers.FloatField(read_only=True)

