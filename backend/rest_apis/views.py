import requests
from django.http import Http404
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import User
from .serializer import UserSerializer


class UserListView(APIView):
    def get(self, request, format=None):
        users = User.objects.all()
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data)

    def post(self, request, format=None):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserDetailView(APIView):
    def get_object(self, pk):
        try:
            return User.objects.get(pk=pk)
        except User.DoesNotExist:
            raise Http404

    def get(self, request, pk, format=None):
        user = self.get_object(pk)
        serializer = UserSerializer(user)
        return Response(serializer.data)

    def put(self, request, pk, format=None):
        user = self.get_object(pk)
        serializer = UserSerializer(user, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, format=None):
        user = self.get_object(pk)
        user.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class UserSearchView(APIView):
    def get(self, request, name, format=None):
        users = User.objects.filter(name__icontains=name)
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data)


class WeatherView(APIView):
    def get(self, request, format=None):
        zipcode = request.GET.get('zip', '')
        country = request.GET.get('country', '')
        if not zipcode:
            return Response({'error': 'Both zip and country code are required'}, status=status.HTTP_400_BAD_REQUEST)
        geocode_url = (
            f"https://us1.locationiq.com/v1/search/postalcode?postalcode={zipcode}&country={country}&key=pk"
            f".<key>&format=json")
        geo_data = None
        try:
            response = requests.get(geocode_url)
            response.raise_for_status()
            geo_data = response.json()
        except requests.exceptions.RequestException as e:
            return Response({"error": f"Error fetching location data: Not a valid Pin Code"}, status=404)
        longitude = geo_data[0]['lon']
        latitude = geo_data[0]['lat']

        if not longitude or not latitude:
            return Response({'error': 'Longitude and latitude are required'}, status=status.HTTP_400_BAD_REQUEST)

        weather_url = (
            f"https://api.openweathermap.org/data/3.0/onecall?"
            f"lat={latitude}&lon={longitude}&exclude=minutely,hourly&units=metric"
            f"&appid=<APP_ID>")
        weather_data = None
        try:
            response = requests.get(weather_url)
            response.raise_for_status()
            weather_data = response.json()

        except requests.exceptions.RequestException as e:
            return Response({"error": f"Error fetching weather data: {str(e)}"}, status=500)

        return Response({
            "current": weather_data['current'],
            "daily": weather_data['daily'],
            "location_info": geo_data[0]
        })
