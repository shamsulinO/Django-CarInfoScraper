# import time
#
# from celery import Celery, shared_task
# from celery.app import task
# from django.core.mail import EmailMessage, EmailMultiAlternatives
# from django.db.models import Q
#
# from django.template.loader import render_to_string
# from django.template import Context
#
#
# import undetected_chromedriver as uc
# from selenium.webdriver.common.by import By
# import selenium.common.exceptions
#
# from datetime import datetime
#
# from .models import *
#
# app = Celery('acars')
#
# @app.task(ignore_result=True)
# def search_cars():
#
#     options = uc.ChromeOptions()
#     options.add_experimental_option(
#         'prefs',
#         {
#             'profile.managed_default_content_settings.javascript': 2,
#             'profile.managed_default_content_settings.images': 2,
#             'profile.managed_default_content_settings.mixed_script': 2,
#             'profile.managed_default_content_settings.media_stream': 2,
#             'profile.managed_default_content_settings.stylesheets': 2
#         }
#     )
#     driver = uc.Chrome(options=options, version_main=94)
#
#     while True:
#         try:
#             for user in Cars.objects.filter(~Q(search_link=None)):
#                 #driver.get('https://www.avito.ru/samara/avtomobili?cd=1&radius=100&searchRadius=100&s=104&localPriority=1')
#                 #driver.get('https://www.avito.ru/samara/avtomobili?cd=1&radius=100&searchRadius=100&s=104&localPriority=1')
#                 # https://www.avito.ru/orenburg/avtomobili?radius=100&s=104&searchRadius=100&s=104&localPriority=0
#                 if 's=104' in user.search_link:
#                     driver.get(f'{user.search_link}&localPriority=1')
#                 else:
#                     driver.get(f'{user.search_link}&s=104&localPriority=1')
#
#                 car_name_link = driver.find_elements(By.XPATH,"//div[@data-marker='item']//a[@data-marker='item-title']")
#                 car_price = driver.find_elements(By.XPATH,"//div[@data-marker='item']//strong[@class='styles-module-root-LIAav']")  # print(i.get_attribute('content'))
#                 car_specific_params = driver.find_elements(By.XPATH,"//div[@data-marker='item']//p[@data-marker='item-specific-params']")
#                 car_description = driver.find_elements(By.XPATH,"//div[@data-marker='item']//div[@class='iva-item-descriptionStep-C0ty1']")
#                 car_geo = driver.find_elements(By.XPATH, "//div[@data-marker='item']//div[@class='geo-root-zPwRk']")
#                 car_date = driver.find_elements(By.XPATH, "//div[@data-marker='item']//p[@data-marker='item-date']")
#                 car_pushed, car_dealer, car_image = [], [], ""
#
#                 car_link = [link.get_attribute('href') for link in car_name_link]
#                 car_name = [name.text for name in car_name_link]
#                 car_price = [price.text for price in car_price]
#                 car_date = [date.text for date in car_date]
#
#                 for image in driver.find_elements(By.XPATH, "//div[@data-marker='item']"):
#                     try:
#                         image = image.find_element(By.XPATH,".//ul[@class='photo-slider-list-OqwtT']//li[@class='photo-slider-list-item-h3A51']")
#                         car_image += image.get_attribute("data-marker").lstrip('slider-image/image-') + " "
#                     except selenium.common.exceptions.NoSuchElementException:
#                         car_image += 'none '
#
#                 for item in driver.find_elements(By.XPATH,"//div[@data-marker='item']//div[@class='iva-item-dateInfoStep-_acjp']"):
#                     if len(item.find_elements(By.TAG_NAME, 'i')) == 1:
#                         car_pushed.append('1')
#                     else:
#                         car_pushed.append('0')
#                 if user.status == 1:
#                     try:
#                         count = car_link.index(user.car_link.split(" ")[0])
#                         if count != 0 and count != 50 and len(user.car_link) > 5:
#                             summ = count if count <= 5 else 5
#                             data = [[car_link[:summ][i], car_name[:summ][i], car_price[:summ][i],
#                                      car_image.split(" ")[:summ][i], car_date[:summ][i]] for i in range(summ)]
#                             html_template = render_to_string('acars/send_car_mail.html', {'data': data, 'count': count})
#                             email = EmailMultiAlternatives(f'Новых автомобилей: {count}', '', 'kinzolmail@gmail.com', [user.email],
#                                                  headers={'X-Entity-Ref-ID': f'{datetime.now()}'})
#                             email.attach_alternative(html_template, 'text/html')
#                             email.send()
#                     except:
#                         count = 50
#                         if len(user.car_link) > 5:
#                             data = [[car_link[:5][i], car_name[:5][i], car_price[:5][i],
#                                      car_image.split(" ")[:5][i], car_date[:5][i]] for i in range(5)]
#                             html_template = render_to_string('acars/send_car_mail.html', {'data': data, 'count': count})
#                             email = EmailMultiAlternatives(f'Новых автомобилей: {count}', '', 'kinzolmail@gmail.com', [user.email],
#                                       headers={'X-Entity-Ref-ID': f'{datetime.now()}'})
#                             email.attach_alternative(html_template, 'text/html')
#                             email.send()
#
#                 if count != 0:
#                     user.car_image = car_image.strip()
#                     user.car_link = " ".join(car_link)
#                     user.car_name = "&^".join(car_name)
#                     user.car_price = "&^".join(car_price)
#                     user.car_specific_params = "&^".join([specific_params.text for specific_params in car_specific_params])
#                     user.car_description = "&^".join([description.text for description in car_description])
#                     user.car_geo = "&^".join([geo.text for geo in car_geo])
#                     user.car_date = "&^".join(car_date)
#                     user.car_pushed = " ".join(car_pushed)
#                     user.save()
#         except Exception as _ex:
#             print(f"{_ex}\n[{datetime.now()}] SEARCH ERROR")
#             time.sleep(5)
#             return