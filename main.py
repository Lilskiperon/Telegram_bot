import nest_asyncio
nest_asyncio.apply()

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, CallbackContext, CallbackQueryHandler, filters
from config import BOT_TOKEN
from converter import convert_image, convert_video, convert_file
import os
import asyncio
import tempfile

async def start(update: Update, context: CallbackContext) -> None:
    keyboard = [
        [
            InlineKeyboardButton("Фото", callback_data='photo'),
            InlineKeyboardButton("Видео", callback_data='video'),
            InlineKeyboardButton("Файл", callback_data='file'),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    if update.message:
        await update.message.reply_text('Выберите категорию для конвертации:', reply_markup=reply_markup)
    elif update.callback_query:
        await update.callback_query.edit_message_text('Выберите категорию для конвертации:', reply_markup=reply_markup)

async def button(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    await query.answer()

    if query.data == 'photo':
        context.user_data['category'] = 'photo'
        await show_format_buttons(update, context, ['png', 'jpg', 'bmp','ico'])
    elif query.data == 'video':
        context.user_data['category'] = 'video'
        await show_format_buttons(update, context, ['mp4', 'avi', 'mov','webm','mkv'])
    elif query.data == 'file':
        context.user_data['category'] = 'file'
        await show_format_buttons(update, context, ['doc', 'pdf', 'docx','docm'])

async def show_format_buttons(update: Update, context: CallbackContext, formats: list) -> None:
    keyboard = [[InlineKeyboardButton(fmt.upper(), callback_data=f'format_{fmt}')] for fmt in formats]
    keyboard.append([InlineKeyboardButton("Вернуться", callback_data='choose_category')])
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.callback_query.edit_message_text(text="Выберите формат конвертации:", reply_markup=reply_markup)

async def format_selection(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    await query.answer()
    context.user_data['format'] = query.data.split('_')[1]
    keyboard = [[InlineKeyboardButton("Вернуться", callback_data='choose_category')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(text=f"Выбран формат: {context.user_data['format'].upper()}. Теперь отправьте файл для конвертации.", reply_markup=reply_markup)

async def handle_file(update: Update, context: CallbackContext) -> None:
    category = context.user_data.get('category')
    output_format = context.user_data.get('format')
    if not category or not output_format:
        await update.message.reply_text('Пожалуйста, сначала выберите категорию и формат.')
        return

    file = None
    if update.message.document:
        file = await update.message.document.get_file()
    elif update.message.photo:
        file = await update.message.photo[-1].get_file()
    elif update.message.video:
        file = await update.message.video.get_file()

    if not file:
        await update.message.reply_text('Файл не найден. Пожалуйста, отправьте корректный файл.')
        return

    file_path = os.path.join(tempfile.gettempdir(), os.path.basename(file.file_path))
    await file.download_to_drive(file_path)

    try:
        if category == 'photo' and output_format in ['png', 'jpg', 'bmp','ico']:
            output_path = convert_image(file_path, output_format)
        elif category == 'video' and output_format in ['mp4', 'avi', 'mov','webp','mkv']:
            output_path = convert_video(file_path, output_format)
        elif category == 'file' and output_format in ['doc', 'pdf', 'docx','docm']:
            output_path = convert_file(file_path, output_format)
        else:
            raise ValueError("Невозможно конвертировать данный файл в выбранный формат")

        await update.message.reply_document(document=open(output_path, 'rb'))
        os.remove(file_path)
        os.remove(output_path)

        # Спрашиваем пользователя, что делать дальше
        keyboard = [
            [
                InlineKeyboardButton("Вернуться", callback_data='choose_category'),
                InlineKeyboardButton("Использовать те же настройки", callback_data='same_settings')
            ],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text('Что вы хотите сделать дальше?', reply_markup=reply_markup)

    except Exception as e:
        await update.message.reply_text(f'Ошибка конвертации: {e}')

async def choose_next_action(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    await query.answer()

    if query.data == 'choose_category':
        await start(update, context)
    elif query.data == 'same_settings':
        keyboard = [[InlineKeyboardButton("Вернуться", callback_data='choose_category')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(text="Теперь отправьте файл для конвертации.", reply_markup=reply_markup)

async def main() -> None:
    application = ApplicationBuilder().token(BOT_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(button, pattern='^(photo|video|file)$'))
    application.add_handler(CallbackQueryHandler(format_selection, pattern='^format_'))
    application.add_handler(CallbackQueryHandler(choose_next_action, pattern='^(choose_category|same_settings)$'))
    application.add_handler(MessageHandler(filters.Document.ALL | filters.PHOTO | filters.VIDEO, handle_file))

    await application.run_polling(stop_signals=None)

if __name__ == '__main__':
    asyncio.run(main())
