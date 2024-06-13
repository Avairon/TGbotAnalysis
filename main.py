import telebot
from docx import Document
from telebot import types
import openai
import requests

bot = telebot.TeleBot('7496545493:AAEMOr9ak97liOIh4KIe1fOnNBFwiVt_eIE')
api_key = "chad-be83d0793f814fef926e24efa4cf49262pmgpr7w"


def read_docx(file_path):
    doc = Document(file_path)

    doc_text = "\n".join([paragraph.text for paragraph in doc.paragraphs])
    return doc_text

def check_compliance(reglament, protocol):
    file1_content = read_docx(reglament)
    file2_content = read_docx(protocol)

    request_json = {
        "message": f"Выдели только запреты из: {file1_content}", # только 'нет' если нарушены или 'да'"
        "api_key": "chad-a04df3ff651f49d1baa51c2cac804efabxtt550p"
    }
    response_reg = requests.post(url="https://ask.chadgpt.ru/api/public/gpt-4o", json=request_json)
    resp_reg_raw = response_reg.json()
    
    if resp_reg_raw['is_success']:
        resp_reg = resp_reg_raw['response']
        print(resp_reg)
        print()

        request_json = {
            "message": f"Вот протокол: {file2_content}. Выдели только принятые решения", # только 'нет' если нарушены или 'да'"
            "api_key": "chad-a04df3ff651f49d1baa51c2cac804efabxtt550p"
        }
        response_prot = requests.post(url="https://ask.chadgpt.ru/api/public/gpt-4o", json=request_json)
        resp_prot_raw = response_prot.json()
        resp_prot = resp_prot_raw['response']
        print(resp_prot)
        print()

        request_json = {
            "message": f"В вымышленом мире есть только эти правила: {resp_reg}; В этом же мире было совбрание, на котором приняли: {resp_prot}; Нарушают ли принятые рещения правила того мира? В ответе напиши только 'да' или 'нет' и обьясни почему", # только 'нет' если нарушены или 'да'",
            "api_key": "chad-a04df3ff651f49d1baa51c2cac804efabxtt550p"
        }

        response = requests.post(url="https://ask.chadgpt.ru/api/public/gpt-4o", json=request_json)

        resp_json  = response.json()
        return resp_json['response']
    
    else:
        return "Произошла ошибка"

def save_file(file_id, file_path):
    file_info = bot.get_file(file_id)
    file = bot.download_file(file_info.file_path)
    with open(file_path, 'wb') as f:
        f.write(file)

# Обработчик сообщений с файлами
@bot.message_handler(content_types=['text'])
def handle_text(message):
    global choise
    if message.text == 'регламент':
        bot.send_message(message.from_user.id, "Отлично! А теперь, прикрепите регламент")
        choise = 1
        
    elif message.text == 'протокол':
        bot.send_message(message.from_user.id, "Отлично! А теперь, прикрепите протокол")
        choise = 2
        
    elif message.text == 'результат':
        bot.send_message(message.from_user.id, str(check_compliance('reglament.docx', 'protocol.docx')))

    else:
        bot.send_message(message.from_user.id, "Чтобы использовать бота, напишите пожалуйста 'регламент' или 'протокол', а затем прикрепите файл")
        choise = 0


@bot.message_handler(content_types=['document'])
def handle_document(message):
    if choise == 1:
        file_id = message.document.file_id
        file_path = 'reglament.docx'
        save_file(file_id, file_path)
        bot.send_message(message.from_user.id, "Регламент сохранён!")
    elif choise == 2:
        file_id = message.document.file_id
        file_path = 'protocol.docx'
        save_file(file_id, file_path)
        bot.send_message(message.from_user.id, "Протокол сохранён!")
    else:
        bot.send_message(message.from_user.id, "Чтобы использовать бота, напишите пожалуйста 'регламент' или 'протокол', а затем прикрепите файл")

bot.polling()
