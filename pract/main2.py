import psycopg2
import telebot
from telebot import types

# Параметры подключения к базе данных PostgreSQL
dbname = 'FitnesClub'
user = 'postgres'
password = '9999'
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
    onas = types.KeyboardButton('/onas')
    reg_button = types.KeyboardButton('/register')
    auth_button = types.KeyboardButton('/authorize')
    markup.add(onas,reg_button, auth_button)
    bot.send_message(user_id, "Выберите действие:", reply_markup=markup)

# Функция для отправки меню пользователя после авторизации
def send_user_menu(user_id):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    profile_button = types.KeyboardButton('/profile')
    my_tren= types.KeyboardButton('/my_tren')
    subscription_button = types.KeyboardButton('/buy_subscription')
    logout_button = types.KeyboardButton('/logout')
    zal_msc = types.KeyboardButton('/zal_msc')
    markup.add(profile_button, my_tren,subscription_button, logout_button,zal_msc)
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

# Обработчик команды /onas
@bot.message_handler(commands=['onas'])
def handle_authorize(message):
    user_id = str(message.from_user.id)  # Приведение user_id к строке
    bot.send_message(user_id, "Добро пожаловать в наш новый фитнес-зал, где мы верим, что каждый может достичь своих целей по здоровью и физической форме! Мы — молодая и динамичная команда, стремящаяся предоставить вам лучшие условия для тренировок и самосовершенствования.")
    bot.send_message(user_id,"Наши цели: \nМы создали это пространство с одной целью — сделать фитнес доступным, удобным и эффективным для каждого. Наша миссия — вдохновлять и поддерживать вас на пути к лучшей версии себя.")
    bot.send_message(user_id,"Что мы предлагаем \nСовременное оборудование: Наш зал оснащён новейшими тренажёрами и оборудованием, чтобы ваши тренировки были максимально эффективными и безопасными. \nПрофессиональные тренеры: Наша команда сертифицированных специалистов поможет вам разработать персональный план тренировок и достигнуть ваших целей. \nШирокий выбор занятий: Мы предлагаем разнообразные групповые занятия, такие как йога, пилатес, кроссфит и другие, чтобы каждый мог найти что-то по душе. \nУдобное расположение: Мы находимся в самом сердце города, и вам будет удобно нас посещать в любое время.\nДоступные цены: Мы предлагаем гибкие тарифы и абонементы, чтобы каждый мог выбрать подходящий для себя вариант")
    bot.send_message(user_id,"Присоединяйтесь к нам! \nЕсли вы ищете место, где можно не только эффективно тренироваться, но и получить поддержку и вдохновение на пути к здоровому образу жизни, мы будем рады видеть вас в нашем зале! Присоединяйтесь к нашему сообществу и начните свой путь к лучшей версии себя уже сегодня.")
# Обработчик команды /zal_msc
@bot.message_handler(commands=['zal_msc'])
def handle_profile(message):
    user_id = str(message.from_user.id)  # Приведение user_id к строке

    try:
        conn = psycopg2.connect(dbname=dbname, user=user, password=password, host=host, port=port)
        cursor = conn.cursor()

        cursor.execute(
            "SELECT name, address, phone FROM fitnessclub WHERE address LIKE '%Москва%'",
            )
        zal_msc = cursor.fetchone()

        if zal_msc:
            name, address,phone = zal_msc

            bot.send_message(user_id,
                             f"Наши спорт залы:\nНазвание клуба: {name}\nадрес: {address}\nномер телефона: {phone}")
        else:
            bot.send_message(user_id, "Спорт зал не найден.")

    except psycopg2.Error as e:
        bot.send_message(user_id, f'Произошла ошибка при работе с базой данных: {e}')
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


@bot.message_handler(commands=['profile'])
def handle_profile(message):
    user_id = str(message.from_user.id)  # Приведение user_id к строке

    try:
        conn = psycopg2.connect(dbname=dbname, user=user, password=password, host=host, port=port)
        cursor = conn.cursor()

        # Запрос профиля пользователя из таблицы Clients
        cursor.execute(
            "SELECT first_name, last_name, middle_name, phone, active_subscription FROM Clients WHERE client_id = %s",
            (user_id,))
        user_profile = cursor.fetchone()

        if user_profile:
            first_name, last_name, middle_name, phone, active_subscription = user_profile
            subscription_status = "активна" if active_subscription else "не активна"

            # Запрос результатов жима лежа из таблицы bench_press_stats
            cursor.execute(
                "SELECT last_weight, last_reps, max_weight, max_reps FROM bench_press_stats WHERE client_id = %s",
                (user_id,))
            bench_press_results = cursor.fetchone()

            # Запрос результатов становой тяги из таблицы deadlift_stats
            cursor.execute(
                "SELECT last_weight, last_reps, max_weight, max_reps FROM deadlift_stats WHERE client_id = %s",
                (user_id,))
            deadlift_results = cursor.fetchone()

            # Запрос результатов приседа из таблицы squat_stats
            cursor.execute(
                "SELECT last_weight, last_reps, max_weight, max_reps FROM squat_stats WHERE client_id = %s",
                (user_id,))
            squat_results = cursor.fetchone()

            # Формирование сообщения с профилем и результатами тренировок
            profile_message = (
                f"Ваш профиль:\nИмя: {first_name}\nФамилия: {last_name}\nОтчество: {middle_name}\nТелефон: {phone}\n"
                f"Подписка: {subscription_status}\n\n"
                "Результаты тренировок:\n"
            )

            if bench_press_results:
                last_weight_bp, last_reps_bp, max_weight_bp, max_reps_bp = bench_press_results
                profile_message += (
                    f"Жим лежа:\n"
                    f"Последний результат: {last_weight_bp} кг на {last_reps_bp} повторений\n"
                    f"Максимальный результат: {max_weight_bp} кг на {max_reps_bp} повторений\n\n"
                )

            if deadlift_results:
                last_weight_dl, last_reps_dl, max_weight_dl, max_reps_dl = deadlift_results
                profile_message += (
                    f"Становая тяга:\n"
                    f"Последний результат: {last_weight_dl} кг на {last_reps_dl} повторений\n"
                    f"Максимальный результат: {max_weight_dl} кг на {max_reps_dl} повторений\n\n"
                )

            if squat_results:
                last_weight_sq, last_reps_sq, max_weight_sq, max_reps_sq = squat_results
                profile_message += (
                    f"Присед:\n"
                    f"Последний результат: {last_weight_sq} кг на {last_reps_sq} повторений\n"
                    f"Максимальный результат: {max_weight_sq} кг на {max_reps_sq} повторений\n"
                )

            bot.send_message(user_id, profile_message)

        else:
            bot.send_message(user_id, "Профиль не найден.")

    except psycopg2.Error as e:
        bot.send_message(user_id, f'Произошла ошибка при работе с базой данных: {e}')

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()





# Обработчик команды /my_tren
@bot.message_handler(commands=['my_tren'])
def handle_my_tren(message):
    user_id = str(message.from_user.id)  # Приведение user_id к строке

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    bench_press_button = types.KeyboardButton('/bench_press')
    squat_button = types.KeyboardButton('/squat')
    deadlift_button = types.KeyboardButton('/deadlift')
    back_button = types.KeyboardButton('/back')
    markup.add(bench_press_button, squat_button, deadlift_button, back_button)
    bot.send_message(user_id, "Выберите упражнение:", reply_markup=markup)

# Обработчик команды /back
@bot.message_handler(commands=['back'])
def handle_back(message):
    user_id = str(message.from_user.id)  # Приведение user_id к строке
    send_user_menu(user_id)


@bot.message_handler(commands=['bench_press'])
def handle_bench_press_command(message):
    user_id = str(message.from_user.id)
    # Проверяем, существует ли пользователь с таким user_id в базе данных
    client_id = get_or_create_user(user_id)
    if client_id:
        # Инициализируем словарь для пользователя, если его еще нет
        if user_id not in user_data:
            user_data[user_id] = {}

        bot.send_message(user_id, "Введите вес (кг) для жима лежа:")
        bot.register_next_step_handler(message, get_weight)
    else:
        bot.send_message(user_id, "Произошла ошибка при сохранении ваших данных. Попробуйте позже.")


def get_weight(message):
    user_id = str(message.from_user.id)
    try:
        weight = float(message.text)
        if weight <= 0:
            raise ValueError("Вес должен быть положительным числом.")

        user_data[user_id]['weight'] = weight
        bot.send_message(user_id, "Введите количество повторений:")

        # Убедитесь, что функция get_reps определена перед ее использованием
        bot.register_next_step_handler(message, get_reps)

    except ValueError:
        bot.send_message(user_id, "Введите корректное число для веса.")
        bot.register_next_step_handler(message, get_weight)


def get_reps(message):
    user_id = str(message.from_user.id)
    try:
        reps = int(message.text)
        if reps <= 0:
            raise ValueError("Количество повторений должно быть положительным числом.")

        user_data[user_id]['reps'] = reps

        weight = user_data[user_id]['weight']

        # Сохранение данных в базу данных
        save_bench_press(user_id, weight, reps)
        bot.send_message(user_id, f"Ваш результат: {weight} кг на {reps} раз(а) успешно сохранен!")

    except ValueError:
        bot.send_message(user_id, "Введите корректное число для количества повторений.")
        bot.register_next_step_handler(message, get_reps)


# Далее следует остальная часть вашего кода, включая функцию save_bench_press и get_or_create_user


def get_or_create_user(user_id):
    try:
        conn = psycopg2.connect(dbname=dbname, user=user, password=password, host=host, port=port)
        cursor = conn.cursor()

        # Проверяем, существует ли пользователь с таким user_id в таблице bench_press_stats
        cursor.execute("SELECT client_id FROM bench_press_stats WHERE client_id = %s", (user_id,))
        existing_user = cursor.fetchone()

        if not existing_user:
            # Если пользователь не найден, добавляем его в таблицу bench_press_stats
            cursor.execute("INSERT INTO bench_press_stats (client_id) VALUES (%s)", (user_id,))
            conn.commit()

        return user_id  # Возвращаем user_id

    except psycopg2.Error as e:
        print(f'Произошла ошибка при добавлении/поиске пользователя: {e}')
        return None

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


# Функция для сохранения результатов жима лежа
def save_bench_press(client_id, weight, reps):
    try:
        conn = psycopg2.connect(dbname=dbname, user=user, password=password, host=host, port=port)
        cursor = conn.cursor()

        # Проверяем, существует ли пользователь с таким client_id в таблице bench_press_stats
        cursor.execute("SELECT * FROM bench_press_stats WHERE client_id = %s", (client_id,))
        user_exists = cursor.fetchone()

        if user_exists:
            # Получаем текущие значения из таблицы
            cursor.execute("SELECT max_weight, max_reps FROM bench_press_stats WHERE client_id = %s", (client_id,))
            current_max_results = cursor.fetchone()

            if current_max_results:
                current_max_weight, current_max_reps = current_max_results
            else:
                current_max_weight, current_max_reps = None, None

            # Обновляем последние результаты
            cursor.execute("UPDATE bench_press_stats SET last_weight = %s, last_reps = %s WHERE client_id = %s",
                           (weight, reps, client_id))

            # Проверяем и обновляем максимальные результаты, если новые результаты превосходят текущие
            if current_max_weight is None or weight > current_max_weight or (
                    weight == current_max_weight and (current_max_reps is None or reps > current_max_reps)):
                cursor.execute("UPDATE bench_press_stats SET max_weight = %s, max_reps = %s WHERE client_id = %s",
                               (weight, reps, client_id))

        else:
            # Если пользователь не существует (что не должно происходить согласно вашему дизайну базы данных)
            print(f"Пользователь с client_id {client_id} не найден в таблице bench_press_stats.")

        conn.commit()
        print(f"Результаты жима лежа успешно сохранены для пользователя с client_id {client_id}.")

    except psycopg2.Error as e:
        print(f'Произошла ошибка при сохранении результатов жима лежа: {e}')

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


@bot.message_handler(commands=['squat'])
def handle_squat_command(message):
    user_id = str(message.from_user.id)
    # Проверяем, существует ли пользователь с таким user_id в базе данных
    client_id = get_or_create_user2(user_id)
    if client_id:
        # Инициализируем словарь для пользователя, если его еще нет
        if user_id not in user_data:
            user_data[user_id] = {}

        bot.send_message(user_id, "Введите вес (кг) для приседаний:")
        bot.register_next_step_handler(message, get_weight_squat)
    else:
        bot.send_message(user_id, "Произошла ошибка при сохранении ваших данных. Попробуйте позже.")

def get_or_create_user2(user_id):
    try:
        conn = psycopg2.connect(dbname=dbname, user=user, password=password, host=host, port=port)
        cursor = conn.cursor()

        # Проверяем, существует ли пользователь с таким user_id в таблице bench_press_stats
        cursor.execute("SELECT client_id FROM squat_stats WHERE client_id = %s", (user_id,))
        existing_user = cursor.fetchone()

        if not existing_user:
            # Если пользователь не найден, добавляем его в таблицу bench_press_stats
            cursor.execute("INSERT INTO squat_stats (client_id) VALUES (%s)", (user_id,))
            conn.commit()

        return user_id  # Возвращаем user_id

    except psycopg2.Error as e:
        print(f'Произошла ошибка при добавлении/поиске пользователя: {e}')
        return None

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


def get_weight_squat(message):
    user_id = str(message.from_user.id)
    try:
        weight = float(message.text)
        if weight <= 0:
            raise ValueError("Вес должен быть положительным числом.")

        user_data[user_id]['weight_squat'] = weight
        bot.send_message(user_id, "Введите количество повторений для приседаний:")

        # Убедитесь, что функция get_reps_squat определена перед ее использованием
        bot.register_next_step_handler(message, get_reps_squat)

    except ValueError:
        bot.send_message(user_id, "Введите корректное число для веса.")
        bot.register_next_step_handler(message, get_weight_squat)


def get_reps_squat(message):
    user_id = str(message.from_user.id)
    try:
        reps = int(message.text)
        if reps <= 0:
            raise ValueError("Количество повторений должно быть положительным числом.")

        user_data[user_id]['reps_squat'] = reps

        weight_squat = user_data[user_id]['weight_squat']

        # Сохранение данных в базу данных
        save_squat_press(user_id, weight_squat, reps)
        bot.send_message(user_id, f"Ваш результат: {weight_squat} кг на {reps} раз(а) успешно сохранен!")

    except ValueError:
        bot.send_message(user_id, "Введите корректное число для количества повторений.")
        bot.register_next_step_handler(message, get_reps_squat)


def save_squat_press(client_id, weight, reps):
    try:
        conn = psycopg2.connect(dbname=dbname, user=user, password=password, host=host, port=port)
        cursor = conn.cursor()

        # Проверяем, существует ли пользователь с таким client_id в таблице squat_stats
        cursor.execute("SELECT * FROM squat_stats WHERE client_id = %s", (client_id,))
        user_exists = cursor.fetchone()

        if user_exists:
            # Получаем текущие значения из таблицы
            cursor.execute("SELECT max_weight, max_reps FROM squat_stats WHERE client_id = %s", (client_id,))
            current_max_results = cursor.fetchone()

            if current_max_results:
                current_max_weight, current_max_reps = current_max_results
            else:
                current_max_weight, current_max_reps = None, None

            # Обновляем последние результаты
            cursor.execute("UPDATE squat_stats SET last_weight = %s, last_reps = %s WHERE client_id = %s",
                           (weight, reps, client_id))

            # Проверяем и обновляем максимальные результаты, если новые результаты превосходят текущие
            if current_max_weight is None or weight > current_max_weight or (weight == current_max_weight and (current_max_reps is None or reps > current_max_reps)):
                cursor.execute("UPDATE squat_stats SET max_weight = %s, max_reps = %s WHERE client_id = %s",
                               (weight, reps, client_id))

        else:
            # Если пользователь не существует, добавляем его в таблицу squat_stats
            cursor.execute("INSERT INTO squat_stats (client_id, last_weight, last_reps, max_weight, max_reps) "
                           "VALUES (%s, %s, %s, %s, %s)",
                           (client_id, weight, reps, weight, reps))

        conn.commit()
        print(f"Результаты приседа успешно сохранены для пользователя с client_id {client_id}.")

    except psycopg2.Error as e:
        print(f'Произошла ошибка при сохранении результатов приседа: {e}')

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()



@bot.message_handler(commands=['deadlift'])
def handle_deadlift_command(message):
    user_id = str(message.from_user.id)
    # Проверяем, существует ли пользователь с таким user_id в базе данных
    client_id = get_or_create_user3(user_id)
    if client_id:
        # Инициализируем словарь для пользователя, если его еще нет
        if user_id not in user_data:
            user_data[user_id] = {}

        bot.send_message(user_id, "Введите вес (кг) для подтягивания:")
        bot.register_next_step_handler(message, get_deadlift_weight)
    else:
        bot.send_message(user_id, "Произошла ошибка при сохранении ваших данных. Попробуйте позже.")

def get_or_create_user3(user_id):
    try:
        conn = psycopg2.connect(dbname=dbname, user=user, password=password, host=host, port=port)
        cursor = conn.cursor()

        # Проверяем, существует ли пользователь с таким user_id в таблице bench_press_stats
        cursor.execute("SELECT client_id FROM deadlift_stats WHERE client_id = %s", (user_id,))
        existing_user = cursor.fetchone()

        if not existing_user:
            # Если пользователь не найден, добавляем его в таблицу bench_press_stats
            cursor.execute("INSERT INTO deadlift_stats (client_id) VALUES (%s)", (user_id,))
            conn.commit()

        return user_id  # Возвращаем user_id

    except psycopg2.Error as e:
        print(f'Произошла ошибка при добавлении/поиске пользователя: {e}')
        return None

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


def get_deadlift_weight(message):
    user_id = str(message.from_user.id)
    try:
        weight = float(message.text)
        if weight <= 0:
            raise ValueError("Вес должен быть положительным числом.")

        user_data[user_id]['weight'] = weight
        bot.send_message(user_id, "Введите количество повторений:")

        # Убедитесь, что функция get_deadlift_reps определена перед ее использованием
        bot.register_next_step_handler(message, get_deadlift_reps)

    except ValueError:
        bot.send_message(user_id, "Введите корректное число для веса.")
        bot.register_next_step_handler(message, get_deadlift_weight)


def get_deadlift_reps(message):
    user_id = str(message.from_user.id)
    try:
        reps = int(message.text)
        if reps <= 0:
            raise ValueError("Количество повторений должно быть положительным числом.")

        user_data[user_id]['reps'] = reps

        weight = user_data[user_id]['weight']

        # Сохранение данных в базу данных
        save_deadlift(user_id, weight, reps)
        bot.send_message(user_id, f"Ваш результат: {weight} кг на {reps} раз(а) успешно сохранен!")

    except ValueError:
        bot.send_message(user_id, "Введите корректное число для количества повторений.")
        bot.register_next_step_handler(message, get_deadlift_reps)


# Далее следует остальная часть вашего кода, включая функцию save_deadlift и get_or_create_user
def save_deadlift(client_id, weight, reps):
    try:
        conn = psycopg2.connect(dbname=dbname, user=user, password=password, host=host, port=port)
        cursor = conn.cursor()

        # Проверяем, существует ли пользователь с таким client_id в таблице deadlift_stats
        cursor.execute("SELECT * FROM deadlift_stats WHERE client_id = %s", (client_id,))
        user_exists = cursor.fetchone()

        if user_exists:
            # Получаем текущие значения из таблицы
            cursor.execute("SELECT max_weight, max_reps FROM deadlift_stats WHERE client_id = %s", (client_id,))
            current_max_results = cursor.fetchone()

            if current_max_results:
                current_max_weight, current_max_reps = current_max_results
            else:
                current_max_weight, current_max_reps = None, None

            # Обновляем последние результаты
            cursor.execute("UPDATE deadlift_stats SET last_weight = %s, last_reps = %s WHERE client_id = %s",
                           (weight, reps, client_id))

            # Проверяем и обновляем максимальные результаты, если новые результаты превосходят текущие
            if current_max_weight is None or weight > current_max_weight or (weight == current_max_weight and (current_max_reps is None or reps > current_max_reps)):
                cursor.execute("UPDATE deadlift_stats SET max_weight = %s, max_reps = %s WHERE client_id = %s",
                               (weight, reps, client_id))

        else:
            # Если пользователь не существует, добавляем его в таблицу deadlift_stats
            cursor.execute("INSERT INTO deadlift_stats (client_id, last_weight, last_reps, max_weight, max_reps) "
                           "VALUES (%s, %s, %s, %s, %s)",
                           (client_id, weight, reps, weight, reps))

        conn.commit()
        print(f"Результаты становой тяги успешно сохранены для пользователя с client_id {client_id}.")

    except psycopg2.Error as e:
        print(f'Произошла ошибка при сохранении результатов становой тяги: {e}')

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
        add_subscribe = types.KeyboardButton('/add_subscribe')
        remove_subscribe = types.KeyboardButton('/remove_subscribe')
        logout_button = types.KeyboardButton('/logout')
        markup.add(profile_button, view_by_phone_button, logout_button,add_subscribe,remove_subscribe)

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

# Обработчик команды /remove_subscribe
@bot.message_handler(commands=['remove_subscribe'])
def handle_remove_subscribe(message):
    user_id = str(message.from_user.id)  # Приведение user_id к строке

    try:
        # Проверяем статус администратора
        if not is_user_admin(user_id):
            bot.send_message(user_id, "У вас нет доступа к этой функции.")
            return

        # Запрос на ввод номера телефона
        msg = bot.send_message(user_id, "Введите номер телефона пользователя для снятия подписки:")
        bot.register_next_step_handler(msg, process_remove_phone_number)

    except Exception as e:
        bot.send_message(user_id, f'Произошла ошибка: {e}')


def process_remove_phone_number(message):
    user_id = str(message.from_user.id)
    phone_number = message.text.strip()

    if not phone_number.isdigit():
        msg = bot.send_message(user_id, "Неверный формат номера телефона. Пожалуйста, введите номер телефона ещё раз:")
        bot.register_next_step_handler(msg, process_remove_phone_number)
        return

    try:
        conn = psycopg2.connect(dbname=dbname, user=user, password=password, host=host, port=port)
        cursor = conn.cursor()

        # Снятие подписки
        cursor.execute("UPDATE Clients SET active_subscription = FALSE WHERE phone = %s", (phone_number,))
        conn.commit()

        if cursor.rowcount > 0:
            bot.send_message(user_id, f"Подписка успешно снята для номера {phone_number}.")
        else:
            bot.send_message(user_id, f"Пользователь с номером {phone_number} не найден.")

    except psycopg2.Error as e:
        bot.send_message(user_id, f'Произошла ошибка при работе с базой данных: {e}')

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

# Обработчик команды /add_subscribe
@bot.message_handler(commands=['add_subscribe'])
def handle_view_profile_by_phone(message):
    user_id = str(message.from_user.id)  # Приведение user_id к строке

    try:
        # Проверяем статус администратора
        if not is_user_admin(user_id):
            bot.send_message(user_id, "У вас нет доступа к этой функции.")
            return

        # Запрос на ввод номера телефона
        msg = bot.send_message(user_id, "Введите номер телефона пользователя для добавления ему подписки:")
        bot.register_next_step_handler(msg, process_phone_number)

    except Exception as e:
        bot.send_message(user_id, f'Произошла ошибка: {e}')

# Обработчик команды /add_subscribe
def process_phone_number(message):
    user_id = str(message.from_user.id)
    phone_number = message.text.strip()

    if not phone_number.isdigit():
        msg = bot.send_message(user_id, "Неверный формат номера телефона. Пожалуйста, введите номер телефона ещё раз:")
        bot.register_next_step_handler(msg, process_phone_number)
        return

    try:
        conn = psycopg2.connect(dbname=dbname, user=user, password=password, host=host, port=port)
        cursor = conn.cursor()

        # Добавление подписки
        cursor.execute("UPDATE Clients SET active_subscription = TRUE WHERE phone = %s", (phone_number,))
        conn.commit()

        bot.send_message(user_id, f"Подписка успешно добавлена для номера {phone_number}.")

    except psycopg2.Error as e:
        bot.send_message(user_id, f'Произошла ошибка при работе с базой данных: {e}')

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


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
        bot.send_message(user_id, "Чтобы активировать подписку надо перейти по сылке ниже и перевести 200р с коментарием вашего номера телефона")
        bot.send_message(user_id, "https://www.tinkoff.ru/cf/4UizRjPEyiO")
        bot.send_message(user_id, "После оплаты подписка активируеться через несколь ко минут")
        conn.commit()

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