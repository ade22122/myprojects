import psycopg2
import telebot
from telebot import types

# Параметры подключения к базе данных PostgreSQL
dbname = 'MAIN'
user = 'postgres'
password = '1234'
host = 'localhost'
port = '5432'

# Инициализация бота с токеном
bot = telebot.TeleBot("7399868327:AAEvd77fXbahP2Gnwr05Dwx6gUl0-WdZklo")

# Состояния для пользователей
states = {}
user_data = {}  # Для хранения промежуточных данных пользователя

# Максимальная длина для ввода данных
MAX_LENGTH = 20
MIN_PASSWORD_LENGTH = 8

# Функция для проверки длины введённого текста
def is_valid_length(text):
    return len(text) <= MAX_LENGTH

# Функция для отправки сообщения с выбором действия
def send_action_choice(user_id):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    reg_button = types.KeyboardButton('/register')
    auth_button = types.KeyboardButton('/authorize')
    markup.add(reg_button, auth_button)
    bot.send_message(user_id, "Выберите действие:", reply_markup=markup)

# Функция для отправки меню пользователя после авторизации
def send_user_menu(user_id):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    profile_button = types.KeyboardButton('/profile')
    subscription_button = types.KeyboardButton('/buy_subscription')
    logout_button = types.KeyboardButton('/logout')
    markup.add(profile_button, subscription_button, logout_button)
    bot.send_message(user_id, "Добро пожаловать! Выберите действие:", reply_markup=markup)

# Обработчик команды /start
@bot.message_handler(commands=['start'])
def handle_start(message):
    user_id = str(message.from_user.id)  # Приведение user_id к строке
    send_action_choice(user_id)

# Обработчик команды /register
@bot.message_handler(commands=['register'])
def handle_register(message):
    user_id = str(message.from_user.id)  # Приведение user_id к строке
    states[user_id] = 'register_first_name'
    bot.send_message(user_id, "Введите ваше имя (не более 20 символов):")

# Обработчик команды /authorize
@bot.message_handler(commands=['authorize'])
def handle_authorize(message):
    user_id = str(message.from_user.id)  # Приведение user_id к строке
    states[user_id] = 'authorize_phone'
    bot.send_message(user_id, "Введите ваш номер телефона для авторизации (не более 20 символов):")

# Обработчик команды /profile

@bot.message_handler(commands=['profile'])
def handle_profile(message):
    user_id = str(message.from_user.id)  # Приведение user_id к строке

    try:
        conn = psycopg2.connect(dbname=dbname, user=user, password=password, host=host, port=port)
        cursor = conn.cursor()

        cursor.execute(
            "SELECT first_name, last_name, middle_name, phone, active_subscription FROM Clients WHERE client_id = %s",
            (user_id,))
        user_profile = cursor.fetchone()

        if user_profile:
            first_name, last_name, middle_name, phone, active_subscription = user_profile
            subscription_status = "активна" if active_subscription else "не активна"
            bot.send_message(user_id,
                             f"Ваш профиль:\nИмя: {first_name}\nФамилия: {last_name}\nОтчество: {middle_name}\nТелефон: {phone}\nПодписка: {subscription_status}")
        else:
            bot.send_message(user_id, "Профиль не найден.")

    except psycopg2.Error as e:
        bot.send_message(user_id, f'Произошла ошибка при работе с базой данных: {e}')
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()






# Обработчик команды /admin_menu
@bot.message_handler(commands=['admin_menu'])
def handle_admin_menu(message):
    user_id = str(message.from_user.id)  # Приведение user_id к строке

    try:
        # Проверяем статус администратора
        if not is_user_admin(user_id):
            bot.send_message(user_id, "У вас нет доступа к этой функции.")
            return

        # Создаем клавиатуру с кнопками для выбора действия
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        profile_button = types.KeyboardButton('/profile')
        view_by_phone_button = types.KeyboardButton('/view_profile_by_phone')
        logout_button = types.KeyboardButton('/logout')
        markup.add(profile_button, view_by_phone_button, logout_button)

        bot.send_message(user_id, "Выберите действие:", reply_markup=markup)

    except psycopg2.Error as e:
        bot.send_message(user_id, f'Произошла ошибка при работе с базой данных: {e}')

# Обработчик команды /logout (для выхода из аккаунта)
@bot.message_handler(commands=['logout'])
def handle_logout(message):
    user_id = str(message.from_user.id)  # Приведение user_id к строке

    try:
        # Сбрасываем все состояния пользователя
        states.pop(user_id, None)

        # Создаем обычную клавиатуру
        markup = types.ReplyKeyboardRemove()

        bot.send_message(user_id, "Вы вышли из аккаунта.", reply_markup=markup)

    except Exception as e:
        bot.send_message(user_id, f'Произошла ошибка: {e}')



# Обработчик команды /view_profile_by_phone
@bot.message_handler(commands=['view_profile_by_phone'])
def handle_view_profile_by_phone(message):
    user_id = str(message.from_user.id)  # Приведение user_id к строке

    try:
        # Проверяем статус администратора
        if not is_user_admin(user_id):
            bot.send_message(user_id, "У вас нет доступа к этой функции.")
            return

        bot.send_message(user_id, "Введите номер телефона пользователя для просмотра его профиля:")

        # Устанавливаем состояние ожидания номера телефона
        states[user_id] = 'view_profile_by_phone'

    except psycopg2.Error as e:
        bot.send_message(user_id, f'Произошла ошибка при работе с базой данных: {e}')


# Обработчик текстовых сообщений (для ввода номера телефона)
@bot.message_handler(func=lambda message: states.get(str(message.from_user.id)) == 'view_profile_by_phone')
def handle_view_profile_by_phone_input(message):
    user_id = str(message.from_user.id)  # Приведение user_id к строке

    try:
        phone_number = message.text

        conn = psycopg2.connect(dbname=dbname, user=user, password=password, host=host, port=port)
        cursor = conn.cursor()

        cursor.execute("SELECT first_name, last_name, middle_name, phone, active_subscription FROM Clients WHERE phone = %s", (phone_number,))
        user_profile = cursor.fetchone()

        if user_profile:
            first_name, last_name, middle_name, phone, active_subscription = user_profile
            subscription_status = "активна" if active_subscription else "не активна"
            bot.send_message(user_id, f"Профиль пользователя с номером телефона {phone_number}:\nИмя: {first_name}\nФамилия: {last_name}\nОтчество: {middle_name}\nТелефон: {phone}\nПодписка: {subscription_status}")
        else:
            bot.send_message(user_id, f"Пользователь с номером телефона {phone_number} не найден.")

    except psycopg2.Error as e:
        bot.send_message(user_id, f'Произошла ошибка при работе с базой данных: {e}')
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

        # Сбрасываем состояние после завершения операции
        states.pop(user_id, None)

# Функция для проверки статуса администратора пользователя
def is_user_admin(user_id):
    try:
        conn = psycopg2.connect(dbname=dbname, user=user, password=password, host=host, port=port)
        cursor = conn.cursor()

        cursor.execute("SELECT is_admin FROM Clients WHERE client_id = %s", (user_id,))
        is_admin = cursor.fetchone()

        return is_admin[0] if is_admin else False

    except psycopg2.Error as e:
        print(f'Произошла ошибка при проверке статуса администратора: {e}')
        return False
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


@bot.message_handler(commands=['buy_subscription'])
def handle_buy_subscription(message):
    user_id = str(message.from_user.id)  # Приведение user_id к строке

    try:
        conn = psycopg2.connect(dbname=dbname, user=user, password=password, host=host, port=port)
        cursor = conn.cursor()

        cursor.execute("UPDATE Clients SET active_subscription = TRUE WHERE client_id = %s", (user_id,))
        conn.commit()
        bot.send_message(user_id, "Подписка успешно активирована!")

    except psycopg2.Error as e:
        bot.send_message(user_id, f'Произошла ошибка при работе с базой данных: {e}')
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

# Обработчик команды /logout
@bot.message_handler(commands=['logout'])
def handle_logout(message):
    user_id = str(message.from_user.id)  # Приведение user_id к строке
    states.pop(user_id, None)
    user_data.pop(user_id, None)
    bot.send_message(user_id, "Вы вышли из аккаунта.")
    send_action_choice(user_id)

# Обработчик текстовых сообщений
@bot.message_handler(func=lambda message: True)
def handle_messages(message):
    user_id = str(message.from_user.id)  # Приведение user_id к строке
    text = message.text

    if len(text) > MAX_LENGTH:
        bot.send_message(user_id, f'Введённый текст слишком длинный. Пожалуйста, введите текст не более {MAX_LENGTH} символов.')
        return

    try:
        conn = psycopg2.connect(dbname=dbname, user=user, password=password, host=host, port=port)
        cursor = conn.cursor()

        if user_id in states:
            current_state = states[user_id]

            if current_state == 'register_first_name':
                if not is_valid_length(text):
                    bot.send_message(user_id, f'Имя слишком длинное. Пожалуйста, введите не более {MAX_LENGTH} символов.')
                    return

                cursor.execute("SELECT client_id FROM Clients WHERE client_id = %s", (user_id,))
                existing_user = cursor.fetchone()

                if not existing_user:
                    cursor.execute("INSERT INTO Clients (client_id, active_subscription) VALUES (%s, %s)", (user_id, False))
                    conn.commit()

                cursor.execute("UPDATE Clients SET first_name = %s WHERE client_id = %s", (text, user_id))
                conn.commit()
                states[user_id] = 'register_last_name'
                bot.send_message(user_id, "Введите вашу фамилию (не более 20 символов):")

            elif current_state == 'register_last_name':
                if not is_valid_length(text):
                    bot.send_message(user_id, f'Фамилия слишком длинная. Пожалуйста, введите не более {MAX_LENGTH} символов.')
                    return

                cursor.execute("UPDATE Clients SET last_name = %s WHERE client_id = %s", (text, user_id))
                conn.commit()
                states[user_id] = 'register_middle_name'
                bot.send_message(user_id, "Введите ваше отчество (не более 20 символов):")

            elif current_state == 'register_middle_name':
                if not is_valid_length(text):
                    bot.send_message(user_id, f'Отчество слишком длинное. Пожалуйста, введите не более {MAX_LENGTH} символов.')
                    return

                cursor.execute("UPDATE Clients SET middle_name = %s WHERE client_id = %s", (text, user_id))
                conn.commit()
                states[user_id] = 'register_phone'
                bot.send_message(user_id, "Введите ваш номер телефона (не более 20 символов):")

            elif current_state == 'register_phone':
                if not is_valid_length(text):
                    bot.send_message(user_id, f'Номер телефона слишком длинный. Пожалуйста, введите не более {MAX_LENGTH} символов.')
                    return

                cursor.execute("UPDATE Clients SET phone = %s WHERE client_id = %s", (text, user_id))
                conn.commit()
                states[user_id] = 'register_password'
                bot.send_message(user_id, "Введите ваш пароль (не более 20 символов):")

            elif current_state == 'register_password':
                if len(text) < MIN_PASSWORD_LENGTH:
                    bot.send_message(user_id, f'Пароль должен содержать не менее {MIN_PASSWORD_LENGTH} символов.')
                    return

                cursor.execute("UPDATE Clients SET password = %s WHERE client_id = %s", (text, user_id))
                conn.commit()

                # Удаляем сообщение с паролем пользователя
                bot.delete_message(user_id, message.message_id)

                # Завершаем регистрацию
                states.pop(user_id)
                bot.send_message(user_id, "Регистрация завершена. Теперь вы можете авторизоваться.")
                send_action_choice(user_id)


            elif current_state == 'authorize_phone':
                if not is_valid_length(text):
                    bot.send_message(user_id, f'Номер телефона слишком длинный. Пожалуйста, введите не более {MAX_LENGTH} символов.')
                    return

                user_data[user_id] = {'phone': text}
                cursor.execute("SELECT client_id FROM Clients WHERE phone = %s", (text,))
                existing_user = cursor.fetchone()

                if existing_user:
                    states[user_id] = 'authorize_password'
                    bot.send_message(user_id, "Введите ваш пароль:")
                else:
                    bot.send_message(user_id, "Пользователь с таким номером телефона не найден.")

            elif current_state == 'authorize_password':
                phone_number = user_data.get(user_id, {}).get('phone')

                if phone_number:
                    cursor.execute("SELECT client_id FROM Clients WHERE phone = %s AND password = %s", (phone_number, text))
                    existing_user = cursor.fetchone()

                    if existing_user:
                        user_data.pop(user_id)
                        bot.send_message(user_id, "Авторизация успешна.")
                        send_user_menu(user_id)
                        bot.delete_message(user_id, message.message_id)
                    else:
                        bot.send_message(user_id, "Пароль неверен. Попробуйте снова.")
                else:
                    bot.send_message(user_id, "Произошла ошибка. Пожалуйста, попробуйте авторизоваться снова.")
                    states.pop(user_id)
                    send_action_choice(user_id)
        else:
            send_action_choice(user_id)

    except psycopg2.Error as e:
        bot.send_message(user_id, f'Произошла ошибка при работе с базой данных: {e}')
    except Exception as e:
        bot.send_message(user_id, f'Произошла ошибка: {e}')
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

# Запуск бота
if __name__ == '__main__':
    bot.polling()
