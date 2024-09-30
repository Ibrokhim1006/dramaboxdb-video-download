import os

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from django.http import JsonResponse


class DownloadVideo(APIView):

    @swagger_auto_schema(
        tags=['Video Downloader'],
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'page_url': openapi.Schema(type=openapi.TYPE_STRING, description='page_url'),

            }
        )
    )
    def post(self, request):
        page_url = request.data.get('page_url', '')

        if not page_url:
            return JsonResponse({'success': False, 'error': 'page_url is required'}, status=400)
    
        # Chrome browserini headless rejimda ochish
        chrome_options = Options()
        chrome_options.add_argument("--headless")  # Brauzerni fon rejimida ochish
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
        driver.get(page_url)

        # Sahifaning yuklanishini kutish
        driver.implicitly_wait(10)  # 10 soniyagacha kutish

        # Play tugmasini topish va ustiga bosish
        try:
            play_button = driver.find_element(By.CSS_SELECTOR, 'img.pcEpisode_videoStart__IcAdF')  # img elementini topish
            play_button.click()  # Play tugmasiga bosish

            # Video tagini topish
            video_tag = driver.find_element(By.ID, 'video_pc_id')  # id orqali video tagini qidirish
            video_url = video_tag.get_attribute('src')  # Video URL'sini olish
            
            # Video faylni yuklab olish
            video_response = requests.get(video_url, stream=True)
            if video_response.status_code == 200:
                video_directory = '/var/www/video'
                video_file_path = os.path.join(video_directory, 'video.mp4')  # Video faylni to'g'ri katalogga saqlash

                with open(video_file_path, 'wb') as f:
                    for chunk in video_response.iter_content(chunk_size=1024):
                        f.write(chunk)
                return JsonResponse({'success': True, 'video_url': video_file_path})
            else:
                return JsonResponse({'success': False, 'error': 'Video yuklab olishda xatolik yuz berdi'})

        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
        finally:
            driver.quit()  # Brauzerni yopish