import configparser
import telebot
import Extensions


config = configparser.ConfigParser()
config.read('Settings.ini')
TOKEN = config['TELEGRAM']['TOKEN']

bot = telebot.TeleBot(TOKEN)

conf_cur = configparser.ConfigParser()
conf_cur.read('currency.ini', encoding='UTF-8')
CURRENCY = dict(conf_cur['currency'])  # Перечень валюты, словарь


@bot.message_handler(commands=['start', 'help'])
def greeting(message):
    bot.send_message(message.chat.id, f"Приветствую!!! Я пересчитываю денежные единицы.")
    bot.send_message(message.chat.id, f"Перечень пересчитываемых денежных единиц можно получить, \
отправив сообщение-команду /values")
    bot.send_message(message.chat.id, f"Для пересчета нужно отправить сообщение в виде <имя валюты, цену которой \
нужно узнать> <имя валюты, в которой надо узнать цену первой валюты> <количество первой валюты>\nПример: \
Рубль Юань 100")


@bot.message_handler(commands=['values', ])
def getvalues(message):
    """
    По команде выдает перечень пересчитываемых валют
    """
    n = '\n'
    bot.send_message(message.chat.id, f"{n.join(CURRENCY.keys())}")


@bot.message_handler(content_types=['text', ])
def set_values(message):
    """
    Принимает пользовательское сообщение на пересчет валют
    :param message: пример: "Рубль Юань 100"
    :return: Возвращает пересчет Юаней в Рубли по текущему курсу
    """
    bot.reply_to(message, "Считаем, ждите ...")
    values = Extensions.StringProcessing(message.text, CURRENCY)
    try:
        Extensions.APIException.checking_keys(values.getvalues(), CURRENCY)
    except Extensions.APIException as e:
        bot.send_message(message.chat.id, f"{e}")
    else:
        base, quote, amount = values.getvalues()
        price = Extensions.APIRequest
        bot.send_message(message.chat.id, f"{price.get_price(base, quote, amount)}")


bot.polling(none_stop=True)
