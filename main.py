import telebot
import json
import pathlib
import os
from pathlib import Path
from requests import Request, Session
from datetime import datetime
from telebot import types
from itertools import groupby

dir_path = pathlib.Path.cwd()


token = '5021820418:AAElq_XEuA-96lTFnOOSUE6o0HF8v1Tcphg'
url = 'https://sexy-smm.ru/api/'
session = Session()

auth = None

def max_numbers(nums):
    return max(float(i) for i in nums.replace(',', '.').split())

def max_hash(nums):
    return max(float(i) for i in nums.replace('#', '').split())

def telegram_bot(token):
    bot = telebot.TeleBot(token)
    @bot.message_handler(commands=["start"])
    def checkToken(message):
        bot.send_message(message.chat.id, 'Бот для сервиса SexySMM. \n\nДоступные команды:\n/neworder - создать заказ\n/reset - перезапустить бота/сбросить команду')
        uid = message.chat.id

        if os.path.exists(Path(dir_path, 'users', str(uid) + '_t')):
            print(Path(dir_path, 'users', str(uid) + '_t'), 'Указанный путь существует')
        else:
            os.makedirs(Path(dir_path, 'users', str(uid) + '_t'))
            temp = {'auth': 'false'}
            with open(Path(dir_path, 'users', str(uid) + '_t', "temp.json"), "w", encoding='utf-8') as f:
                json.dump(temp, f, sort_keys=True, indent=2, ensure_ascii=False)

        with open(Path(dir_path, 'users', str(uid) + '_t', "temp.json"), "r", encoding='utf-8') as f:
            temp = json.loads(f.read())
        if temp['auth'] == 'false':
            auth = False
        else:
            auth = True

        if auth == True:
            pass
        else:
            txt = bot.send_message(message.chat.id, 'Ваш аккаунт не подтверждён. Отправьте боту код подтверждения из сервиса для привязки аккаунта к SexySMM')
            bot.register_next_step_handler(txt, checkTeleg)

    @bot.message_handler(commands=["neworder"])
    def start_message(message):
        uid = message.chat.id
        with open(Path(dir_path, 'users', str(uid) + '_t', "temp.json"), "r", encoding='utf-8') as f:
            temp = json.loads(f.read())
        if temp['auth'] == 'false':
            auth = False
        else:
            auth = True


        if auth == True:
            parameters = {
                'r': 'v1/service/index',
                'key': temp["api"]
            }
            req = session.get(url, params=parameters)
            serviceList = req.json()
            catList = []
            for i in serviceList:
                catList.append(i["category"])
            sCatList = set(catList)

            keys = []
            ni = 0
            markup = types.InlineKeyboardMarkup(row_width=3)

            for i in sCatList:
                ni = ni + 1
                if ni >= 3 + 1:
                    ni = 1
                    btn1 = keys[0]
                    btn2 = keys[1]
                    btn3 = keys[2]

                    markup.add(btn1, btn2, btn3)
                    keys = []
                    keys.append(
                        types.InlineKeyboardButton(text=str(i), callback_data=str(i)))
                else:
                    keys.append(
                        types.InlineKeyboardButton(text=str(i), callback_data=str(i)))
            if len(keys) == 1:
                btn1 = keys[0]
                markup.add(btn1)
            elif len(keys) == 2:
                btn1 = keys[0]
                btn2 = keys[1]
                markup.add(btn1, btn2)
            elif len(keys) == 3:
                btn1 = keys[0]
                btn2 = keys[1]
                btn3 = keys[2]
                markup.add(btn1, btn2, btn3)

            bot.send_message(message.chat.id, 'Выберите категорию услуг. \nДля отмены заказа - воспользуйтесь командой /reset', reply_markup=markup)
        else:
            txt = bot.send_message(message.chat.id, 'Ваш аккаунт не подтверждён. Отправьте боту код подтверждения из сервиса для привязки аккаунта к SexySMM')
            bot.register_next_step_handler(txt, checkTeleg)



    @bot.callback_query_handler(func=lambda call: call.data)
    def callback_inline(call):
        uid = call.message.chat.id
        with open(Path(dir_path, 'users', str(uid) + '_t', "temp.json"), "r", encoding='utf-8') as f:
            temp = json.loads(f.read())
        parameters = {
            'r': 'v1/service/index',
            'key': temp["api"]
        }
        req = session.get(url, params=parameters)
        serviceList = req.json()
        catList = []
        for i in serviceList:
            catList.append(i["category"])
        sCatList = set(catList)
        try:
            if call.message:
                if call.data == 'apply':
                    parameters = {
                        'r': 'v1/order/create',
                        'key': temp["api"],
                        'service': temp["service"],
                        'link': temp["link"],
                        'quantity': temp["quantity"]
                    }
                    try:
                        req = session.get(url, params=parameters)
                        data = req.json()
                        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=str(data["error"]))
                    except Exception as e:
                        print(repr(e))

                for i in sCatList:
                    if call.data == str(i):
                        keys = []
                        ni = 0
                        markup = types.InlineKeyboardMarkup(row_width=2)
                        for n in serviceList:
                            if n["category"] == str(call.data):
                                ni = ni + 1
                                if ni >= 2 + 1:
                                    ni = 1
                                    btn1 = keys[0]
                                    btn2 = keys[1]

                                    markup.add(btn1, btn2)
                                    keys = []
                                    keys.append(
                                        types.InlineKeyboardButton(text=str(n["name"]), callback_data=str(n["service"])))
                                else:
                                    keys.append(
                                        types.InlineKeyboardButton(text=str(n["name"]), callback_data=str(n["service"])))
                        if len(keys) == 1:
                            btn1 = keys[0]
                            markup.add(btn1)
                        elif len(keys) == 2:
                            btn1 = keys[0]
                            btn2 = keys[1]
                            markup.add(btn1, btn2)

                        bot.send_message(call.message.chat.id, 'Выберите категорию услуг. \nДля отмены заказа - воспользуйтесь командой /reset', reply_markup=markup)

                if int(call.data):
                    parameters = {
                        'r': 'v1/service/index',
                        'key': temp["api"]
                    }
                    try:
                        req = session.get(url, params=parameters)
                        serviceList = req.json()
                        serviceInfo = next(item for item in serviceList if item["service"] == int(call.data))
                        with open(Path(dir_path, 'users', str(uid) + '_t', "temp.json"), "r", encoding='utf-8') as f:
                            temp = json.loads(f.read())
                        data = {
                            'name': serviceInfo["name"],
                            'category': serviceInfo["category"],
                            'min': serviceInfo["min"],
                            'max': serviceInfo["max"],
                            'service': str(call.data)
                        }
                        temp.update(data)
                        with open(Path(dir_path, 'users', str(uid) + '_t', "temp.json"), "w", encoding='utf-8') as f:
                            json.dump(temp, f, sort_keys=True, indent=2, ensure_ascii=False)

                        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=f'Услуга: {temp["category"]} - {temp["name"]}. \nМинимум к заказу {temp["min"]}, миксимум {temp["max"]}.')
                        txt = bot.send_message(call.message.chat.id, 'Введите необходимое вам кол-во:')
                        bot.register_next_step_handler(txt, updTemp_quan)
                    except Exception as e:
                        print(repr(e))
                else:
                    print('Pass')
        except Exception as e:
                print(repr(e))



    @bot.message_handler(content_types=["text"])
    def checkTeleg(message):
        uid = message.chat.id
        if message.text == '31283:CJ_tyI30GUETd91w6164EQB8IuXEACdy':
            with open(Path(dir_path, 'users', str(uid) + '_t', "temp.json"), "r", encoding='utf-8') as f:
                temp = json.loads(f.read())
            data = {
                "auth": 'true',
                'api': '559d3ffb2cb357555acf9b4c753fd42e'
            }
            temp.update(data)
            with open(Path(dir_path, 'users', str(uid) + '_t', "temp.json"), "w", encoding='utf-8') as f:
                json.dump(temp, f, sort_keys=True, indent=2, ensure_ascii=False)
            bot.send_message(message.chat.id, 'Аккаунт подтверждён')
        else:
            txt = bot.send_message(message.chat.id, 'Неверный токен. Введите корректный:')
            bot.register_next_step_handler(txt, checkTeleg)

    def updTemp_quan(message):
        uid = message.chat.id
        with open(Path(dir_path, 'users', str(uid) + '_t', "temp.json"), "r", encoding='utf-8') as f:
            temp = json.loads(f.read())
        if message.text.isdigit():
            if int(message.text) >= int(temp["min"]) and int(message.text) <= int(temp["max"]):
                data = {
                    'quantity': int(message.text)
                }
                temp.update(data)
                with open(Path(dir_path, 'users', str(uid) + '_t', "temp.json"), "w", encoding='utf-8') as f:
                    json.dump(temp, f, sort_keys=True, indent=2)

                txt = bot.send_message(message.chat.id, 'Вставьте ссылку на пост:')
                bot.register_next_step_handler(txt, updTemp_link)
            else:
                txt = bot.send_message(message.chat.id, f'Неверное значение. \nМинимум к заказу {temp["min"]}, миксимум {temp["max"]}. \nПопробуйте еще раз:')
                bot.register_next_step_handler(txt, updTemp_quan)
        else:
            txt = bot.send_message(message.chat.id, f'Неверное значение. \nМинимум к заказу {temp["min"]}, миксимум {temp["max"]}. \nПопробуйте еще раз:')
            bot.register_next_step_handler(txt, updTemp_quan)

    def updTemp_link(message):
        uid = message.chat.id
        if 'https://' in str(message.text):
            with open(Path(dir_path, 'users', str(uid) + '_t', "temp.json"), "r", encoding='utf-8') as f:
                temp = json.loads(f.read())
            data = {
                'link': str(message.text)
            }
            temp.update(data)
            with open(Path(dir_path, 'users', str(uid) + '_t', "temp.json"), "w", encoding='utf-8') as f:
                json.dump(temp, f, sort_keys=True, indent=2)

            markup = types.InlineKeyboardMarkup(row_width=2)
            btn_apply = types.InlineKeyboardButton(text='Подтвердить', callback_data='apply')
            btn_decline = types.InlineKeyboardButton(text='Отменить', callback_data='decline')
            markup.add(btn_apply, btn_decline)
            bot.send_message(chat_id=message.chat.id, text=f'Услуга: {temp["category"]}. \nКоличество: {temp["quantity"]}. \nСсылка: {temp["link"]}', reply_markup=markup)
        else:
            txt = bot.send_message(message.chat.id, 'Некорректная ссылка. Вставьте ссылку:')
            bot.register_next_step_handler(txt, updTemp_link)


    bot.polling()

if __name__ == '__main__':

    telegram_bot(token)