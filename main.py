from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher, FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.contrib.fsm_storage.memory import MemoryStorage
import asyncio
import psycopg2



from config import TOKEN, con
from Parser import listDate, url, pull_all

bot = Bot(token=TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())

global con


class reg(StatesGroup):
    add = State()
    delete = State()


@dp.message_handler(commands=['start'])
async def cmd_start(message: types.Message):
    poll_keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    poll_keyboard.add(types.KeyboardButton(text="Список Моих Аниме"))
    poll_keyboard.add(types.KeyboardButton(text="Добавить Аниме"))
    poll_keyboard.add(types.KeyboardButton(text="Удалить Аниме"))
    poll_keyboard.add(types.KeyboardButton(text="Список всех Онгоингов"))
    await message.answer("Нажмите на кнопку ниже и оставьте все заботы на меня. \n Как только появится"
                         " нужное вам Аниме, я тут же сообщу \U0001F509", reply_markup=poll_keyboard)


# Хэндлер на текстовое сообщение с текстом “Список Моих Аниме”
@dp.message_handler(lambda message: message.text == "Список Моих Аниме", state='*')
async def action_cancel(message: types.Message):
    #conn = sqlite3.connect('chat.db')

    cur = con.cursor()
    cur.execute("SELECT * FROM users WHERE UserId = %s", (message.chat.id,))
    rows = cur.fetchall()
    print(rows)
    plug = '\u2B50Список Аниме за которым Вы следите\u2B50:\n'
    if rows ==  []:
        plug = 'Хозяин, вы еще не выбрали тайтлы, за которыми будете следить\u26A0'
    else:
        for row in rows:
            plug = plug + str(row[-1]) + '\n'
    await message.answer(plug)


# Хэндлер на текстовое сообщение с текстом “Добавить Аниме”
@dp.message_handler(lambda message: message.text == "Добавить Аниме", state='*')
async def action_cancel(message: types.Message):
    await message.answer("Введите полное название на русском\n(Посотреть название можно в Список всех Онгоингов). "
                         "\n\u2755Например: "
                         "\nВторжение Гигантов (четвёртый сезон)"
                         "\nБоруто: Новое поколение Наруто"
                         "\nДоктор Стоун (второй сезон)",)
    await reg.add.set()


@dp.message_handler(state=reg.add, content_types=types.ContentTypes.TEXT)
async def fname_step(message: types.Message, state: FSMContext):
    await state.update_data(name_user=message.text.title())
    anime_name = message.text
    if anime_name in listDate:
        writen(message)
        await message.answer(text='Аниме добавлено\u2B50')
        await state.finish()
    else:
        await message.answer(text='Не найдено в списке Онгоингов, попробуйте еще раз\u26A0')
        await state.finish()


# Хэндлер на текстовое сообщение с текстом “Список всех Онгоингов”
@dp.message_handler(lambda message: message.text == "Список всех Онгоингов", state='*')
async def action_cancel(message: types.Message):
    anime_list = '\U0001F525Список всех Онгоингов Анимевоста\U0001F525:\n'
    for i in listDate:
        anime_list = anime_list + i +'\n'
    await message.answer(anime_list)


# Хэндлер на текстовое сообщение с текстом “Удалить Аниме”
@dp.message_handler(lambda message: message.text == "Удалить Аниме", state='*')
async def action_cancel(message: types.Message):
    await message.answer("Для удаления \U0001F6AE выбраного вами Аниме введите полное название на русском.\n\u2755Например:"
                         "\nВторжение Гигантов (четвёртый сезон)"
                         "\nБоруто: Новое поколение Наруто"
                         "\nДоктор Стоун (второй сезон)",)
    await reg.delete.set()


@dp.message_handler(state=reg.delete, content_types=types.ContentTypes.TEXT)
async def fname_step(message: types.Message, state: FSMContext):
    await state.update_data(name_user=message.text.title())
    cur = con.cursor()
    cur.execute("SELECT * FROM users WHERE UserId = %s AND animeId = %s",
                (message.chat.id, message.text))
    check = cur.fetchone()
    if check != None:
        delete(message)
        await message.answer(text='Аниме удалено\u274C')
        await state.finish()
    else:
        await message.answer(text='Указаное вами Аниме не найдено в вашем списке, попробуйте еще раз\u26A0')
        await state.finish()


@dp.message_handler()
async def cmd_start(message: types.Message):
    await message.answer("Извините, вы не выбрали что я должен сделать\u2753",)


def delete(mess):
    cur = con.cursor()
    cur.execute("DELETE FROM users WHERE UserId = %s AND animeId = %s",
                (mess.chat.id, mess.text))
    con.commit()
    print(mess.chat.id, mess.text)


def writen(mess):
    cur = con.cursor()
    cur.execute("SELECT * FROM users WHERE UserId = %s AND animeId = %s",
                (mess.chat.id, mess.text))
    check = cur.fetchone()
    if check == None:
        try:
            i = (mess.chat.id, mess.text)
            cur.execute("""INSERT INTO users(UserId, animeId) VALUES(%s, %s);""", i)
            con.commit()
        except:
            print('Ошибка БД')


def createDB():
    cur = con.cursor()
    cur.execute("""CREATE TABLE IF NOT EXISTS anime(
           Id SERIAL PRIMARY KEY, 
           AnimeName VARCHAR(128));
        """)
    con.commit()
    cur.execute("""CREATE TABLE IF NOT EXISTS users(
            Id SERIAL PRIMARY KEY,
            UserId INT,
            animeId VARCHAR(128));
        """)
    con.commit()


def add_new_anime(listDate):
    for i in listDate:
        cur = con.cursor()
        cur.execute("Select * from anime where AnimeName = %s", (i,))
        check = cur.fetchone()
        if check == None:
            cur.execute("""INSERT INTO anime(AnimeName)
                   VALUES(%s);""", (i,))
            con.commit()


async def main():
    firs_element = pull_all(url)[0]
    while True:
        gag = pull_all(url)
        firs_element_index = gag.index(firs_element)
        print(firs_element_index)
        if firs_element_index > 0:
            firs_element = gag[firs_element_index - 1]
            print(firs_element_index)
            cur = con.cursor()
            print(firs_element)
            cur.execute("Select * from users where AnimeId = %s", (firs_element,))
            check = cur.fetchall()
            con.commit()
            for i in check:
                print(i, '+++++')
                await bot.send_message(i[1], "Вышло Аниме " + firs_element)
        await asyncio.sleep(180)


if __name__ == '__main__':
    createDB()
    add_new_anime(listDate)
    loop = asyncio.get_event_loop()
    tasks = [loop.create_task(main()), loop.create_task(dp.start_polling())]
    wait_tasks = asyncio.wait(tasks)
    loop.run_until_complete(wait_tasks)
    loop.close()