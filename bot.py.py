import vt
import telebot

# Инициализация бота с помощью токена бота
bot = telebot.TeleBot("Токен из телеграмма")
API_KEY = "код из вирус тотал"
client = vt.Client(API_KEY)

# Функция проверки ссылки на вирусы с помощью VirusTotal API
def check_link(link):
    try:
        url_id = vt.url_id(link)
        # Получить отчет по URL-адресу из VirusTotal
        url_report = client.get_object("/urls/{}", url_id)
        # Проверьте, не является ли URL вредоносным
        if url_report.last_analysis_stats["malicious"] > 0:
            return "☠️ Эта ссылка является вредоносной! ☠️"
        else:
            return "✅ Эта ссылка не является вредоносной."
    except vt.error.APIError as e:
        print("Ошибка VirusTotal API:", e)
        return None
    except Exception as e:
        print("Ссылка для проверки ошибок:", e)
        return None
# Обработчик для команды /check
@bot.message_handler(commands=['check'])
def check_command(message):
    # Разделите сообщение пользователя на слова
    words = message.text.split(' ')
    print(words)
    # Убедитесь, что пользователь включил ссылку после команды /check
    if len(words) < 2:
        bot.reply_to(message, "Пожалуйста, укажите ссылку для проверки после команды /check.")
        return
    # Получить ссылку из сообщения пользователя
    link = words[1]
    # Проверьте ссылку на наличие вирусов
    result = check_link(link)
    # Если результат равен None, произошла ошибка при проверке ссылки
    if result is None:
        bot.reply_to(message, "❌ Ошибка проверки сылки. Пожалуйста, попробуйте еще раз позже.")
    else:
        # Отправьте результат обратно пользователю
        bot.reply_to(message, result)
# Функция обработки ошибок для бота
def handle_error(exception):
    print("TeleBot error:", exception)
# Запустите бота с обработкой ошибок
bot.polling()