import aiogram

from aiogram import F, Router
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext

import database.requests as rq
import app.keyboards as kb 

import os
from dotenv import load_dotenv
load_dotenv()

router=Router()

last_bot_message_id = None

SAVE_DIR ="botreports/media"

class Report (StatesGroup):
    text_rep = State()
    ranked = State()
    photo = State()
    photo_question = State()

@router.message(CommandStart())
async def cmd_start(message: Message):
        await message.answer('Добрый день! В меню ниже вы можете перейти к своим жалобам или оставить новую.', reply_markup = kb.start_user)

@router.callback_query(F.data == 'new_report')
async def new_report_1(callback: CallbackQuery, state: FSMContext):
    await state.set_state(Report.text_rep)
    await callback.message.edit_text('Введите текст жалобы.')

@router.message(Report.text_rep)
async def new_report_2(message: Message, state: FSMContext):
        await state.update_data(text_rep = message.text)
        await state.set_state(Report.photo_question)
        await message.answer('Желаете ли вы прикрепить фотографию к жалобе?', reply_markup = kb.question_photo)

@router.message(Report.photo_question)
async def handle_photo_question(message: Message, state: FSMContext):
    if message.text.lower() == 'да':
        await state.set_state(Report.photo)
        await message.answer('Пожалуйста, загрузите фото. Когда закончите, отправьте "Готово".', reply_markup=ReplyKeyboardRemove())
    else:
        await state.set_state(Report.ranked)
        await message.answer('Оставьте оценку от 1 до 5.', reply_markup=ReplyKeyboardRemove())

@router.message(Report.photo, F.photo | F.text)
async def handle_photo(message: Message, state: FSMContext):
    data = await state.get_data()
    photos = data.get('photos', [])

    if message.content_type == F.photo and message.photo:
        photo = message.photo[-1]
        photos.append(photo.file_id)
        await state.update_data(photos=photos)
        await message.answer('Фото добавлено. Вы можете загрузить ещё фото или отправить "Готово", чтобы продолжить.')

    elif message.content_type == F.text and message.text.lower() == 'готово':
        await state.set_state(Report.ranked)
        await message.answer('Оставьте оценку от 1 до 5.', reply_markup=ReplyKeyboardRemove())

    else:
        await message.answer('Пожалуйста, загрузите фото или отправьте "Готово", чтобы продолжить.')


@router.message(Report.ranked)
async def new_report_3(message: Message, state: FSMContext):
    try:
        ranked = int(message.text)
        if ranked < 1 or ranked > 5:
            raise ValueError()
        
        await state.update_data(ranked=ranked)
        data = await state.get_data()
        photos = data.get('photos', [])

        await rq.ins_report(
            message.from_user.id,
            message.from_user.username,
            data["text_rep"],
            ranked,
            photos
        )

        if photos:
            for file_id in photos:
                file_info = await message.bot.get_file(file_id)
                file_path = file_info.file_path
                file_name = f"{file_id}.jpg"
                destination = os.path.join(SAVE_DIR, file_name)
                await message.bot.download_file(file_path, destination)

        await message.answer('Спасибо, ваша жалоба сохранена.', reply_markup=kb.start_user)
        await state.clear()
        
    except ValueError:
        await message.answer("Некорректная оценка. Пожалуйста, введите оценку еще раз.")

@router.callback_query(F.data == 'my_reports')
async def my_reports(callback: CallbackQuery):
    global last_bot_message_id
    reps = await rq.check_reps(callback.from_user.id)
    if reps:
        sent_message = await callback.message.edit_text('Выберите жалобу из списка ниже.', reply_markup= await kb.user_reports(reps))
        last_bot_message_id = sent_message.message_id
    else:
        await callback.message.edit_text('Вы не оставляли жалоб.')
        await callback.message.answer('В меню ниже вы можете перейти к своим жалобам или оставить новую.', reply_markup = kb.start_user)

@router.callback_query(F.data.startswith('report_'))
async def report_n(callback: CallbackQuery, state: FSMContext):
    global last_bot_message_id
    parts = callback.data.split('_')
    report_id = int(parts[1])
    type = int(parts[2])
    rep = await rq.get_report_by_id(report_id)
    await callback.message.bot.delete_message(chat_id=callback.message.chat.id, message_id=last_bot_message_id)
    if rep.status == 0:
        status = 'На рассмотрении'
    else: 
        status = 'Рассмотрена'
    text_message = (
        f'Жалоба №: {rep.id}\n'
        f'Дата: {rep.date}\n'
        f'Статус: {status}\n'
        f'Комментарий специалиста: {rep.comment_moder}\n'
    )
    if rep.photos:
        for idx, photo in enumerate(rep.photos, start=1):
            await callback.message.answer_photo(photo.photo_id, caption=f'Жалоба №: {rep.id}\n'
            f'Фото {idx}')
 
    await callback.message.answer(
        text_message,
        reply_markup = kb.back_my_reports
    )

@router.callback_query(F.data.startswith('page_'))
async def paginate_reports(callback: CallbackQuery):
    parts = callback.data.split('_')
    page = int(parts[1])
    type = int(parts[2])
    reps = await rq.check_reps(callback.from_user.id)
    keyboard = await kb.user_reports(reps, type, page)
    await callback.message.edit_text('Выберите жалобу из списка ниже.', reply_markup=keyboard)

@router.callback_query(F.data == 'back_to_start')
async def back_to_start(callback: CallbackQuery):
    await callback.message.edit_text('Добрый день! В меню ниже вы можете перейти к своим жалобам или оставить новую.', reply_markup = kb.start_user)