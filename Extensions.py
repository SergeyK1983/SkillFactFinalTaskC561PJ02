import requests
import configparser
import json


class StringProcessing:
    """
    Обрабатывает пользовательскую строку запроса, проверяет первичные ошибки.
    Возвращает список с денежными единицами и количество.
    Пример: запрос "Рубль Юань 100", ответ ['RUB', 'CNY', 100]
    """
    def __init__(self, query_string, currency):
        self.query_string = query_string.strip().lower()  # Строка
        self.currency = currency  # Словарь с перечнем валют
        self.values = []

    def getvalues(self):
        i = 0
        mon = ['', '']
        poz = [0, 0]
        # Сравнение содержимого строки со словарем
        for k in tuple(self.currency.keys()):
            if len(mon[0]) != 0 and len(mon[1]) != 0:
                break
            try:
                if self.query_string.index(k[:3].lower()) >= 0:
                    poz[i] = self.query_string.index(k[:3].lower())
                    mon[i] = self.currency[k]
                    i += 1
            except ValueError:
                pass

        mon = mon if poz[0] < poz[1] else mon[::-1]

        # Извлечение цифр из строки
        d = ''
        for k in self.query_string[max(poz) + 3:]:
            if k.isdigit():
                d += k
            if k.isspace() and len(d) != 0:
                break
        try:
            if float(d) == 0:
                raise ValueError
            mon.append(float(d))
        except ValueError:
            mon.append(d)

        self.values = mon
        return self.values


class APIRequest:
    """
    На вход принимает переменные от списка, полученного от StringProcessing: base, quote, amount = ['RUB', 'CNY', 100].
    Выполняет API запрос для пересчета валют по текущему курсу.
    Возвращает строку от ответа.
    """
    @staticmethod
    def get_price(base, quote, amount):
        config = configparser.ConfigParser()
        config.read('Settings.ini')
        TOKEN_API = config['APILAYER']['TOKEN']
        payload = {}
        headers = {"apikey": TOKEN_API}

        url = f"https://api.apilayer.com/fixer/convert?to={base}&from={quote}&amount={amount}"  # to, from, amount, requests.exceptions.ConnectionError
        # url_symbol = "https://api.apilayer.com/fixer/symbols"  # для запроса всех возможных валют

        response = requests.request("GET", url, headers=headers, data=payload)
        status_code = response.status_code
        # result = response.text

        if 400 <= status_code < 500:
            return f"Ошибка запроса. Что-то пошло не так."
        elif status_code >= 500:
            return f"Ошибка сервера"
        else:
            data = json.loads(response.text)
            try:
                return f"Результат: {round(data['result'], 2)} {base}\n\
Текущий курс: {round(data['info']['rate'], 2)} {base} за 1 {quote}"
            except KeyError:
                return f"Ошибка при отправке запроса"


class APIException(Exception):
    @staticmethod
    def checking_keys(val, currency: dict):  # currency = valuta
        if len(val[0]) == 0 or len(val[1]) == 0:
            raise APIException("Неверно введена валюта")
        if val[0] and val[1] not in currency.values():
            raise APIException("Неверно введён запрос или\nнет в списке валют")
        if not isinstance(val[2], float):
            raise APIException(f"Для пересчета нужно указать количество")


# VALUTA = {
#     'Юань': 'CNY',
#     'Евро': 'EUR',
#     'Фунт': 'GBP',  # Британский
#     'Тенге': 'KZT',
#     'Рубль': 'RUB',
#     'Лира': 'TRY',  # Турецкая
#     'Доллар': 'USD'
# }

# config1 = configparser.ConfigParser()
# config1.read('currency.ini', encoding='UTF-8')
#
# VALUTA = dict(config1['currency'])
# print(VALUTA, '\n', type(VALUTA))
#
# s = 'Рубль Юань 20'
# try:
#     pr = StringProcessing(s, VALUTA)
#     print(pr.getvalues())
#     APIException.checking_keys(pr.getvalues(), VALUTA)
# except APIException as e:
#     print(e)
# else:
#     base, quote, amount = pr.getvalues()
#     print(APIRequest.get_price(base, quote, amount))
