import requests
import ast
from datetime import datetime

from . import Gibdd_Types

def gibdd(vin, captcha, token):
    result = [{}, {}, [], {}, [], []]
    report_of_car = {}
    data_diagnostic_card = []
    mileage_diagnostic_card = []
    all_dict = {}

    try:
        history = requests.post('https://xn--b1afk4ade.xn--90adear.xn--p1ai/proxy/check/auto/history', data={'vin': vin, 'checkType': 'history', 'captchaWord': captcha,'captchaToken': token})
        history = ast.literal_eval(history.text)

        if str(history['message']) == "Проверка CAPTCHA не была пройдена из-за неверного введенного значения.":
            return f"Проверка CAPTCHA не была пройдена из-за неверного введенного значения. Повторите попытку ввода!"
        elif str(history['message']) == "Проверка CAPTCHA не была пройдена, поскольку не был передан ее код.":
            return f"Проверка CAPTCHA не была пройдена, поскольку не был передан ее код. Отправте VIN заново!"
        elif str(history['message']) == "Срок действия кода CAPTCHA устарел, попробуйте снова.":
            return f"Срок действия кода CAPTCHA устарел! Отправте VIN заново!"


        dtp = requests.post('https://xn--b1afk4ade.xn--90adear.xn--p1ai/proxy/check/auto/dtp',data={'vin': vin, 'checkType': 'aiusdtp', 'captchaWord': captcha,'captchaToken': token})
        dtp = ast.literal_eval(dtp.text)

        wanted = requests.post('https://xn--b1afk4ade.xn--90adear.xn--p1ai/proxy/check/auto/wanted',data={'vin': vin, 'checkType': 'wanted', 'captchaWord': captcha,'captchaToken': token})
        wanted = ast.literal_eval(wanted.text)

        restrict = requests.post('https://xn--b1afk4ade.xn--90adear.xn--p1ai/proxy/check/auto/restrict',data={'vin': vin, 'checkType': 'restricted', 'captchaWord': captcha,'captchaToken': token})
        restrict = ast.literal_eval(restrict.text)

        company_reviews = requests.post('https://easy.gost.ru/', data={'vin': vin}).text

        diagnostic = requests.post('https://xn--b1afk4ade.xn--90adear.xn--p1ai/proxy/check/auto/diagnostic',data={'vin': vin, 'checkType': 'diagnostic', 'captchaWord': captcha,'captchaToken': token})
        diagnostic = diagnostic.text
        diagnostic = ast.literal_eval(diagnostic.replace("null","'null'").replace("true","'true'").replace("false", "'false'"))

        if history["status"] == 404:
            return 'Ошибка'
        else:
            car_keys = ["Модель", "Цвет", "Тип ТС", "Год", "Объем двигателя",
                        "Номер двигателя", "Мощность двигателя", "Категория", "VIN номер",
                        "Номер кузова", "Кем выдан ПТС", "Номер ПТС", "Владельцев по ПТС", "Пробег",
                        "Количество ДТП"]
            car_values = [(lambda: history["RequestResult"]["vehicle"]["model"]),
                          (lambda: history["RequestResult"]["vehicle"]["color"]),
                          (lambda: Gibdd_Types.typeAuto[history["RequestResult"]["vehicle"]["type"]]),
                          (lambda: history["RequestResult"]["vehicle"]["year"]),
                          (lambda: history["RequestResult"]["vehicle"]["engineVolume"]),
                          (lambda: history["RequestResult"]["vehicle"]["engineNumber"]),
                          (lambda: history["RequestResult"]["vehicle"]["powerHp"]),
                          (lambda: history["RequestResult"]["vehicle"]["category"]),
                          (lambda: history["RequestResult"]["vehicle"]["vin"]),
                          (lambda: history["RequestResult"]["vehicle"]["bodyNumber"]),
                          (lambda: history["RequestResult"]["vehiclePassport"]["issue"]),
                          (lambda: history["RequestResult"]["vehiclePassport"]["number"]),
                          (lambda: len(history["RequestResult"]["ownershipPeriods"]["ownershipPeriod"])),
                          (lambda: f'{diagnostic["RequestResult"]["diagnosticCards"][0]["odometerValue"]}км ({diagnostic["RequestResult"]["diagnosticCards"][0]["dcDate"]})'),
                          (lambda: len(dtp["RequestResult"]["Accidents"]))]

            for i in range(len(car_keys)):
                try:
                    result[0][car_keys[i]] = car_values[i]()
                except Exception:
                    pass


            for i in range(len(history["RequestResult"]["ownershipPeriods"]["ownershipPeriod"])):
                persontype = "Физ. лицо" if history["RequestResult"]["ownershipPeriods"]["ownershipPeriod"][i]["simplePersonType"] == "Natural" else "Юр. лицо"
                try:
                    result[1][f'{history["RequestResult"]["ownershipPeriods"]["ownershipPeriod"][i]["from"]} по {history["RequestResult"]["ownershipPeriods"]["ownershipPeriod"][i]["to"]} - {persontype}'] = f'Основания: {Gibdd_Types.typeOperation[history["RequestResult"]["ownershipPeriods"]["ownershipPeriod"][i]["lastOperation"]]}'
                except Exception:
                    result[1][f'{history["RequestResult"]["ownershipPeriods"]["ownershipPeriod"][i]["from"]} по Н.В. - {persontype}'] = f'Владеет: {duration_days((datetime.now() - datetime.strptime(history["RequestResult"]["ownershipPeriods"]["ownershipPeriod"][i]["from"], "%Y-%m-%d")).days)}'


            try:
                if str(wanted["RequestResult"]) == "{'records':, 'count': 0, 'error': 0}" or str(wanted["RequestResult"]) == "{'records': [], 'count': 0, 'error': 0}":
                    report_of_car['wanted'] = "Авто не числилось в розыске"
                else:
                    report_of_car['wanted'] = "Авто числится в розыске!!! Подробно можете узнать на сайте ГИБДД."
            except Exception:
                report_of_car['wanted'] = 'Ошибка при получении данных о розыске!'


            result[2].append(company_reviews)


            try:
                if restrict["RequestResult"]["records"] == []:
                    report_of_car['restrict'] = "На авто не накладывались ограничения"
                else:
                    len_restrict = len(restrict['RequestResult']['records'])
                    text_len_restrict = "записи" if len_restrict >= 2 and len_restrict <=4 else "запись" if len_restrict == 1 else "записей"
                    text_find = "Найдена" if len_restrict == 1 else "Найдено"
                    report_of_car['restrict'] = f"{text_find} {len_restrict} {text_len_restrict} об ограничениях!"
            except Exception:
                report_of_car['restrict'] = 'Ошибка при получении данных об ограничениях!'


            try:
                result[3]['Номер'] = diagnostic['RequestResult']['diagnosticCards'][0]['dcNumber']
                result[3]['Осмотр проведен'] = diagnostic['RequestResult']['diagnosticCards'][0]['dcDate']
                result[3]['Действует до'] = diagnostic['RequestResult']['diagnosticCards'][0]['dcExpirationDate']
                result[3]['Пробег'] = f"{diagnostic['RequestResult']['diagnosticCards'][0]['odometerValue']}км"
                result[3]['Адрес'] = diagnostic['RequestResult']['diagnosticCards'][0]['pointAddress']

                data_diagnostic_card.append(diagnostic['RequestResult']['diagnosticCards'][0]['dcDate'])
                mileage_diagnostic_card.append(int(diagnostic['RequestResult']['diagnosticCards'][0]['odometerValue']))
            except Exception:
                pass


            try:
                for i in range(len(diagnostic['RequestResult']['diagnosticCards'][0]['previousDcs'])):
                    dict_new = {}
                    dict_new['Номер'] = diagnostic['RequestResult']['diagnosticCards'][0]['previousDcs'][i]['dcNumber']
                    dict_new['Осмотр проведен'] = diagnostic['RequestResult']['diagnosticCards'][0]['previousDcs'][i]['dcDate']
                    dict_new['Истек'] = diagnostic['RequestResult']['diagnosticCards'][0]['previousDcs'][i]['dcExpirationDate']
                    dict_new['Пробег'] = f"{diagnostic['RequestResult']['diagnosticCards'][0]['previousDcs'][i]['odometerValue']}км"
                    result[4].append(dict_new)
                    data_diagnostic_card.append(diagnostic['RequestResult']['diagnosticCards'][0]['previousDcs'][i]['dcDate'])
                    mileage_diagnostic_card.append(int(diagnostic['RequestResult']['diagnosticCards'][0]['previousDcs'][i]['odometerValue']))

                if len(data_diagnostic_card) >= 3:
                    twisted_mileage = False
                    data_sorted = list(sorted(data_diagnostic_card))
                    all_dict = {tuple(map(int, item.split('-'))): mileage_diagnostic_card[data_diagnostic_card.index(item)] for item in data_sorted}
                    data_sorted = [tuple(map(int, i.split('-'))) for i in data_sorted]
                    for mil in range(1, len(data_sorted)):
                        if int(all_dict[data_sorted[mil - 1]]) > int(all_dict[data_sorted[mil]]):
                            twisted_mileage = True

                    report_of_car['mileage'] = f"Пробег на авто не скручивали" if not twisted_mileage else f"Скручивали пробег на авто!"
            except Exception as e:
                report_of_car['mileage'] = f"Мало информации о пробеге"


            if dtp["RequestResult"]["Accidents"] == []:
                report_of_car['dtp'] = f"Нет зафиксированных ДТП"
            else:
                report_of_car['dtp'] = f'Зафиксированных ДТП: {len(dtp["RequestResult"]["Accidents"])}'
                dtp_id = 1
                for i in range(len(dtp["RequestResult"]["Accidents"])):
                    dict_new = {}
                    points = str(dtp['RequestResult']["Accidents"][i]['DamagePoints']).replace("'","").replace("[","").replace("]","").replace(" ", "")
                    dict_new['image'] = fr"https://vin01.ru/images/s.php?map={points}"
                    dtp_keys = ["Дата", "Номер", "Тип", "Состояние", "Участников", "Место", 'id']
                    dtp_values = [(lambda: dtp['RequestResult']["Accidents"][i]["AccidentDateTime"]),
                                  (lambda: dtp['RequestResult']["Accidents"][i]["AccidentNumber"]),
                                  (lambda: dtp['RequestResult']["Accidents"][i]["AccidentType"]),
                                  (lambda: dtp['RequestResult']["Accidents"][i]["VehicleDamageState"]),
                                  (lambda: dtp['RequestResult']["Accidents"][i]["VehicleAmount"]),
                                  (lambda: dtp['RequestResult']["Accidents"][i]["AccidentPlace"]),
                                  (lambda: dtp_id)]
                    for y in range(len(dtp_keys)):
                        try:
                            dict_new[dtp_keys[y]] = dtp_values[y]()
                        except KeyError:
                            pass
                    dtp_id += 1
                    result[5].append(dict_new)
    except Exception:
        pass

    return [result, report_of_car, all_dict]


def duration_days(count_days):
    years = count_days // 365
    months = (count_days % 365) // 30
    weeks = ((count_days % 365) % 30) // 7
    days = ((count_days % 365) % 30) % 7 + weeks*7
    duration_list = []
    if years > 0:
        duration_list.append(f"{years} {'год' if years == 1 else 'года' if 2 <= years <= 4 else 'лет'}")
    if months > 0:
        duration_list.append(f"{months} {'месяц' if months == 1 else 'месяца' if 2 <= months <= 4 else 'месяцев'}")
    if days > 0:
        duration_list.append(f"{days} {'день' if days == 1 else 'дня' if 2 <= days <= 4 else 'дней'}")
    return ", ".join(duration_list)