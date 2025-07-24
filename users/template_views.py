import os

from django.shortcuts import render, redirect
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
import requests

from .models import User
from django.contrib.auth import login
from django.contrib import messages
import jwt
from dotenv import load_dotenv

load_dotenv()


# Базовый url для API запросов
BASE_URL = os.getenv('API_BASE_URL', 'http://localhost:8000/api/')



# Страница для ввода номера телефона
class LoginPhoneView(View):

    def get(self, request):
        return render(request, 'login_phone.html')

    def post(self, request):
        phone = request.POST.get('phone')

        # Запрос к API для отправки кода
        response = requests.post(f"{BASE_URL}request-code/", json={'phone': phone})
        data = response.json()

        if response.status_code == 200:
            # Сохраняем телефон в сессии для следующего шага
            request.session['phone'] = phone

            # Отображаем код
            messages.success(request, f"Код отправлен. Демо-код: {data.get('debug_code')}")

            return redirect('verify_code')
        else:
            messages.error(request, data.get('detail', 'Произошла ошибка'))
            return render(request, 'login_phone.html')

# Страница для ввода проверочного кода
class VerifyCodeView(View):

    def get(self, request):
        if 'phone' not in request.session:
            messages.error(request, "Сначала введите номер телефона")
            return redirect('login_phone')

        return render(request, 'verify_code.html')

    def post(self, request):
        code = request.POST.get('code')
        phone = request.session.get('phone')

        if not phone:
            messages.error(request, "Сессия истекла. Пожалуйста, введите номер телефона снова")
            return redirect('login_phone')

        # Запрос к API для проверки кода
        response = requests.post(f"{BASE_URL}verify-code/", json={'phone': phone, 'code': code})

        if response.status_code == 200:
            data = response.json()

            # Сохраняем токены в сессии
            request.session['access_token'] = data.get('access')
            request.session['refresh_token'] = data.get('refresh')

            # Декодируем токен, чтобы получить айди пользователя
            try:
                token_data = jwt.decode(data.get('access'), options={"verify_signature": False})
                user_id = token_data.get('user_id')

                # Логиним пользователя
                user = User.objects.get(id=user_id)
                login(request, user)

                messages.success(request, "Вы успешно авторизовались")
                return redirect('profile')

            except Exception as e:
                messages.error(request, f"Ошибка авторизации: {str(e)}")
                return redirect('login_phone')
        else:
            try:
                data = response.json()
                messages.error(request, data.get('detail', 'Неверный код'))
            except:
                messages.error(request, "Произошла ошибка при проверке кода")

            return render(request, 'verify_code.html')

# Страница профиля пользователя
class ProfileView(LoginRequiredMixin, View):
    login_url = '/login-phone/'

    def get(self, request):
        # Получаем текущего пользователя
        user = request.user

        # Получаем список рефералов
        referrals = User.objects.filter(activated_invite_code=user.invite_code)

        context = {
            'user': user,
            'referrals': referrals
        }

        return render(request, 'profile.html', context)

# Страница активации инвайт-кода
class ActivateInviteCodeView(LoginRequiredMixin, View):
    login_url = '/login-phone/'

    def get(self, request):
        return render(request, 'activate_code.html')

    def post(self, request):
        invite_code = request.POST.get('invite_code')

        # Проверяем, не активировал ли пользователь уже инвайт-код
        if request.user.activated_invite_code:
            messages.error(request, "Вы уже активировали инвайт-код")
            return redirect('profile')

        # Запрос к API для активации инвайт-кода
        headers = {'Authorization': f'Bearer {request.session.get("access_token")}'}
        response = requests.post(
            f"{BASE_URL}activate-invite-code/",
            json={'invite_code': invite_code},
            headers=headers
        )

        if response.status_code == 200:
            messages.success(request, "Инвайт-код успешно активирован")
            # Обновляем пользователя, чтобы изменения сразу отразились
            request.user.activated_invite_code = invite_code
            request.user.save()
            return redirect('profile')
        else:
            try:
                data = response.json()
                messages.error(request, data.get('detail', 'Ошибка при активации инвайт-кода'))
            except:
                messages.error(request, "Произошла ошибка при активации инвайт-кода")

            return render(request, 'activate_code.html')
