import sqlite3
import smtplib
import time
from email.mime.text import MIMEText
from jinja2 import Environment, FileSystemLoader
from datetime import datetime

import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
import selenium.common.exceptions

options = uc.ChromeOptions()
options.add_experimental_option(
    'prefs',
    {
        'profile.managed_default_content_settings.javascript': 2,
        'profile.managed_default_content_settings.images': 2,
        'profile.managed_default_content_settings.mixed_script': 2,
        'profile.managed_default_content_settings.media_stream': 2,
        'profile.managed_default_content_settings.stylesheets':2
    }
)
driver = uc.Chrome(options=options, version_main=94)

def search_cars():
    while True:
        try:
            for user in sqlite3_query("SELECT user_id, status, search_link, car_link, email FROM acars_cars WHERE search_link IS NOT NULL"):
                #driver.get('https://www.avito.ru/samara/avtomobili?cd=1&radius=100&searchRadius=100&s=104&localPriority=1')
                #driver.get('https://www.avito.ru/samara/avtomobili?cd=1&radius=100&searchRadius=100&s=104&localPriority=1')
                # https://www.avito.ru/orenburg/avtomobili?radius=100&s=104&searchRadius=100&s=104&localPriority=0
                if 's=104' in user[2]:
                    driver.get(f'{user[2]}&localPriority=1')
                else:
                    driver.get(f'{user[2]}&s=104&localPriority=1')

                car_name_link = driver.find_elements(By.XPATH,"//div[@data-marker='item']//a[@data-marker='item-title']")
                car_price = driver.find_elements(By.XPATH,"//div[@data-marker='item']//strong[@class='styles-module-root-LIAav']")  # print(i.get_attribute('content'))
                car_specific_params = driver.find_elements(By.XPATH,"//div[@data-marker='item']//p[@data-marker='item-specific-params']")
                car_description = driver.find_elements(By.XPATH,"//div[@data-marker='item']//div[@class='iva-item-descriptionStep-C0ty1']")
                car_geo = driver.find_elements(By.XPATH, "//div[@data-marker='item']//div[@class='geo-root-zPwRk']")
                car_date = driver.find_elements(By.XPATH, "//div[@data-marker='item']//p[@data-marker='item-date']")
                car_pushed, car_dealer, car_image = [], [], ""
                elements_error = driver.find_elements(By.XPATH,"//*[contains(text(), 'Доступ ограничен:')]")
                if elements_error:
                    raise Exception('Доступ ограничен')

                car_link = [link.get_attribute('href') for link in car_name_link]
                car_name = [name.text for name in car_name_link]
                car_price = [price.text for price in car_price]
                car_date = [date.text for date in car_date]

                for image in driver.find_elements(By.XPATH, "//div[@data-marker='item']"):
                    try:
                        image = image.find_element(By.XPATH,".//ul[@class='photo-slider-list-OqwtT']//li[@class='photo-slider-list-item-h3A51']")
                        car_image += image.get_attribute("data-marker").lstrip('slider-image/image-') + " "
                    except selenium.common.exceptions.NoSuchElementException:
                        car_image += 'none '

                for item in driver.find_elements(By.XPATH,"//div[@data-marker='item']//div[@class='iva-item-dateInfoStep-_acjp']"):
                    if len(item.find_elements(By.TAG_NAME, 'i')) == 1:
                        car_pushed.append('1')
                    else:
                        car_pushed.append('0')

                if user[1] == 1:
                    try:
                        count = car_link.index(user[3].split(" ")[0])
                        if count != 0 and count != 50 and len(user[3]) > 5:
                            summ = count if count <= 5 else 5
                            send_mail(car_link[:summ], car_name[:summ], car_price[:summ],
                                      car_image.split(" ")[:summ], car_date[:summ], user[4], count)
                    except:
                        count = 50
                        if len(user[3]) > 5:
                            send_mail(car_link[:5], car_name[:5], car_price[:5],
                                      car_image.split(" ")[:5], car_date[:5], user[4], count)

                    if count != 0:
                        query = """UPDATE acars_cars SET
                                   car_image = ?,
                                   car_link = ?, 
                                   car_name = ?, 
                                   car_price = ?,
                                   car_specific_params = ?,
                                   car_description = ?,
                                   car_geo = ?,
                                   car_date = ?,
                                   car_pushed = ?
                                   WHERE user_id = ?;"""

                        params = (car_image.strip(),
                                  " ".join(car_link),
                                  "&^".join(car_name),
                                  "&^".join(car_price),
                                  "&^".join([specific_params.text for specific_params in car_specific_params]),
                                  "&^".join([description.text for description in car_description]),
                                  "&^".join([geo.text for geo in car_geo]),
                                  "&^".join(car_date),
                                  ' '.join(car_pushed),
                                  user[0])

                        sqlite3_query(query, params)
        except KeyboardInterrupt:
            print("KONEC")
            break
        except Exception as _ex:
            print(f"{_ex}\n[{datetime.now()}] SEARCH ERROR")
            break


def send_mail(links, names, prices, images, date, email, count):
    sender = #email host
    password = #EMAIL PASSWORD
    server = smtplib.SMTP("smtp.gmail.com", 587)
    server.starttls()

    data = [[links[i], names[i], prices[i], images[i], date[i]] for i in range(len(links))]

    try:
        server.login(sender, password)
        file_loader = FileSystemLoader(r'..\..\templates\acars')
        env = Environment(loader=file_loader)
        tm = env.get_template('send_car_mail.html')
        msg = tm.render(data=data, email=email, count=count)
        msg = MIMEText(msg, 'html')
        msg["Subject"] = f"Новых автомобилей: {count}"
        msg["X-Entity-Ref-ID"] = f'{datetime.now()}'
        server.sendmail(sender, email, msg.as_string())
    except Exception as _ex:
        print(f"{_ex}\n[{datetime.now()}] MAIL ERROR")

def sqlite3_query(query, *args):
    try:
        connect_to_DataBase = sqlite3.connect(r"..\..\..\db.sqlite3")
        cursor = connect_to_DataBase.cursor()
        if args:
            cursor.execute(query, args[0])
        else:
            cursor.execute(query)
        connect_to_DataBase.commit()
        result = cursor.fetchall()
        connect_to_DataBase.close()
        return result
    except Exception as _ex:
        print(f"{_ex}\n[{datetime.now()}] DATABASE ERROR")

if __name__ == '__main__':
    search_cars()