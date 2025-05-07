from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton

start_user = InlineKeyboardMarkup (inline_keyboard=[
    [InlineKeyboardButton(text='Оставить жалобу',callback_data='new_report')],
    [InlineKeyboardButton(text='Мои жалобы',callback_data='my_reports')]
])

back_to_start = InlineKeyboardButton(text='На главную', callback_data='back_to_start')

back_my_reports = InlineKeyboardMarkup (inline_keyboard=[
    [InlineKeyboardButton(text='Назад', callback_data='my_reports')]
])


question_photo = ReplyKeyboardMarkup (keyboard=[
    [KeyboardButton(text = 'Да'),
    KeyboardButton(text = 'Нет')]
], resize_keyboard= True, input_field_placeholder='Выберите из вариантов снизу')

async def user_reports(reps, type = 0, page=1):
    inline_keyboard = []
    ITEMS_PER_PAGE = 5
    start_index = (page - 1) * ITEMS_PER_PAGE
    end_index = start_index + ITEMS_PER_PAGE
    paginated_reps = reps[start_index:end_index]
    total_pages = (len(reps) + ITEMS_PER_PAGE - 1) // ITEMS_PER_PAGE

    for report in paginated_reps:
        button_text = f'Жалоба № {report.id}'
        callback_data = f'report_{report.id}_{type}'
        button = InlineKeyboardButton(text=button_text, callback_data=callback_data)
        inline_keyboard.append([button])
    
    navigation_buttons = []
    if start_index > 0:
        navigation_buttons.append(InlineKeyboardButton(text='⬅️ Назад', callback_data=f'page_{page-1}_{type}'))
    
    page_counter = InlineKeyboardButton(text=f'Страница {page}/{total_pages}', callback_data='rep_page_counter', callback_disabled=True)
    navigation_buttons.append(page_counter)

    if end_index < len(reps):
        navigation_buttons.append(InlineKeyboardButton(text='Вперед ➡️', callback_data=f'page_{page+1}_{type}'))
    
    if navigation_buttons:
        inline_keyboard.append(navigation_buttons)

    inline_keyboard.append([back_to_start])
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=inline_keyboard)
    return keyboard
    