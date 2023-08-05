import datetime
import re
import requests
import json

from django.contrib.auth import logout, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView
from django.core.mail import EmailMultiAlternatives
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
from django.template.loader import render_to_string
from django.urls import reverse_lazy
from django.views.generic import ListView, TemplateView
from django.views.generic.edit import FormMixin, CreateView

from .forms import *
from .models import *

from .utils.acars.gibdd import gibdd

import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
import selenium.common.exceptions

profile_options = {
        'profile.managed_default_content_settings.javascript': 2,
        'profile.managed_default_content_settings.images': 2,
        'profile.managed_default_content_settings.mixed_script': 2,
        'profile.managed_default_content_settings.media_stream': 2,
        'profile.managed_default_content_settings.stylesheets': 2
    }


header_menu = [{'title': 'Автомобили', 'url': 'home', 'id': 1},
        {'title': 'Проверка', 'url': 'check', 'id': 2},
        {'title': 'Настройки', 'url': 'settings', 'id': 3},]


class AllCars(LoginRequiredMixin, ListView):
    model = Cars
    template_name = 'acars/index.html'
    context_object_name = 'cars'
    login_url = 'login'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        c_def = {"title": "Главная", "cars": self.get_queryset(), 'header_menu': header_menu, 'header_select': 1}
        return dict(list(context.items()) + list(c_def.items()))

    def get_queryset(self):
        cars = Cars.objects.filter(user_id=self.request.user.id)
        data = [[cars[0].car_link.split(' ')[i].split('_')[-1],
                cars[0].car_image.split(' ')[i],
                cars[0].car_link.split(' ')[i],
                cars[0].car_name.split('&^')[i],
                cars[0].car_price.split('&^')[i],
                cars[0].car_specific_params.split('&^')[i],
                cars[0].car_description.split('&^')[i],
                cars[0].car_pushed.split(' ')[i],
                cars[0].car_geo.split('&^')[i],
                cars[0].car_date.split('&^')[i]]
                for i in range(len(cars[0].car_link.split(' ')))]
        return data


class AvitoCar(LoginRequiredMixin, TemplateView):
    template_name = 'acars/avitocar.html'
    login_url = 'login'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        c_def = {"title": "Информация авто", 'car_id': self.kwargs['car_id'], "car_info": self.get_car_info(self.kwargs['car_id']),
                 'header_menu': header_menu, 'header_select': 2}
        return dict(list(context.items()) + list(c_def.items()))

    def get_car_info(self, car_id):
        options = uc.ChromeOptions()
        options.add_experimental_option('prefs', profile_options)
        options.add_argument('headless')
        driver = uc.Chrome(options=options)

        try:
            driver.set_page_load_timeout(30)
            driver.get(f'https://www.avito.ru/shops/157799769/blockForItem?baseItemId={car_id}')
            information_car = driver.find_element(By.XPATH,f"//pre[@style='word-wrap: break-word; white-space: pre-wrap;']").text
            number = re.search(r'"110427":"(.+?)","110907"', information_car)
            number = number.group(1) if number else "Не найдено"
            vin = re.search(r'"836":"(.+?)"},"', information_car)
            vin = vin.group(1) if vin else "Не найдено"
            return [vin, number]
        except Exception:
            return ['Ошибка', 'Ошибка']
        finally:
            driver.close()


class VinCar(LoginRequiredMixin, TemplateView):
    template_name = 'acars/vincar.html'
    login_url = 'login'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        c_def = {"title": "Проверка по VIN",'vin_num': self.kwargs['vin_num'], 'vin_info': self.get_info(self.kwargs['vin_num']),
                 "captcha": self.request.GET.get('captcha'), 'header_menu': header_menu, 'header_select': 2}
        return dict(list(context.items()) + list(c_def.items()))

    def get_info(self, vin):
        captcha = self.request.GET.get('captcha')
        token = self.request.GET.get('token')

        if captcha == None:
            options = uc.ChromeOptions()
            options.add_experimental_option('prefs', profile_options)
            options.add_argument('headless')
            driver = uc.Chrome(options=options, version_main=108)

            try:
                driver.set_page_load_timeout(20)
                driver.get(f'https://check.gibdd.ru/captcha')
                captcha = driver.find_element(By.XPATH,f"//pre[@style='word-wrap: break-word; white-space: pre-wrap;']").text
                captcha = json.loads(captcha)
                return [f'data:image/png;base64,{captcha["base64jpg"]}', captcha['token']]
            except Exception:
                return self.get_info(vin)
            finally:
                driver.close()
        else:
            result = gibdd(vin, captcha, token)
            return result

class Settings(LoginRequiredMixin, FormMixin, TemplateView):
    template_name = 'acars/settings.html'
    form_class = ChangeUrl
    success_url = reverse_lazy('settings')
    login_url = 'login'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        car_instance = Cars.objects.get(user_id=self.request.user.id)
        kwargs['instance'] = car_instance
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        c_def = {"title": 'Настройки', 'header_menu': header_menu, 'header_select': 3}
        return dict(list(context.items()) + list(c_def.items()))

    def form_valid(self, form):
        form.save()
        return super().form_valid(form)

    def post(self, request, *args, **kwargs):
        form = self.get_form()
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)


class Check(LoginRequiredMixin, TemplateView):
    template_name = 'acars/check.html'
    login_url = 'login'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        c_def = {"title": 'Проверка авто', 'header_menu': header_menu, 'header_select': 2}
        return dict(list(context.items()) + list(c_def.items()))


class LoginUser(LoginView):
    form_class = LoginUserForm
    template_name = "acars/login.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        c_def = {'title': "Вход"}
        return dict(list(context.items()) + list(c_def.items()))

    def get_success_url(self):
        return reverse_lazy('home')

class RegisterUser(CreateView):
    form_class = RegisterUserForm
    template_name = 'acars/register.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        c_def = {'title': "Регистрация"}
        return dict(list(context.items()) + list(c_def.items()))

    def form_valid(self, form):
        user = form.save()
        login(self.request, user)

        new_model = Cars()
        new_model.email = self.request.user.email
        new_model.status = 1
        new_model.user_id = self.request.user.id
        new_model.save()

        html_template = render_to_string('acars/test_email.html')
        email = EmailMultiAlternatives(f'Успешная регистрация', '', 'kinzolmail@gmail.com', [self.request.user.email],
                                       headers={'X-Entity-Ref-ID': f'123'})
        email.attach_alternative(html_template, 'text/html')
        email.send()

        return redirect('home')


@login_required(login_url='login')
def logout_user(request):
    logout(request)
    return redirect("login")