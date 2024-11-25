from django.shortcuts import render

# Create your views here.
from django.urls import path
from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Profile
from .serializers import ProfileSerializer


class ProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self,request):
        profile = Profile.objects.filter(user=request.user.id)

        serializer = ProfileSerializer(profile, many=True)

        return Response({'profile': serializer.data}, status=status.HTTP_200_OK)

    def post(self,request):
        dataprofile = request.data.copy()
        dataprofile['user'] = request.user.id
        serializer = ProfileSerializer(data=dataprofile)
        if serializer.is_valid():
            serializer.save()
            return Response({'message': 'Profile created successfully!'}, status=status.HTTP_200_OK)

        return Response({'message': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)