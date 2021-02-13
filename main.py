import logging
import gc
from aiogram import Bot, Dispatcher, executor, types
from style_transfer import style_transfer_class
API_TOKEN = 'token'

# Configure logging
logging.basicConfig(level=logging.INFO)

# Initialize bot and dispatcher
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

flag= True
content_flag=False
style_flag=False

def transform(content_root, style_root,im_name, im_size ):
    """Function for image transformation."""
    my_gan = style_transfer_class(content_root, style_root, im_name,im_size)
    my_gan.run_style_transfer()

    del content_root
    del style_root
    del im_name
    gc.collect()


@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    """
    This handler will be called when user sends `/start`  command
    """
    await message.reply("Hi!\nI'm Style Transfer Bot!\nPowered by aiogram. \n Command /help for help")

@dp.message_handler(commands=['help'])
async def send_welcome(message: types.Message):
    """
    This handler will be called when user sends  `/help` command
    """
    await message.reply("Please send content picture. Then send style picture")



@dp.message_handler(content_types=['photo'])
async def photo_processing(message):
    """
    Triggered when the user sends an image and saves it for further processing.
    """
    chat_id_str=str(message.chat.id)

    global flag
    global content_flag
    global style_flag


    # The bot is waiting for a picture with content from the user.
    if flag:
        await message.photo[-1].download('content'+chat_id_str+'.jpg')
        await message.answer(text='OK. Now I got the content picture'
                                  ' ,send me a style picture , or '
                                  'the /cancel command to choose '
                                  'a another content image.')
        flag = False
        content_flag = True

    # The bot is waiting for a picture with style from the user.
    else:
        await message.photo[-1].download('style'+chat_id_str+'.jpg')
        await message.answer(text='I got the style pic. Now use the /continue'
                                  ' command or the /cancel command to change'
                                  ' the image style.')
        flag = True
        style_flag = True  # Now the bot knows that the style image exists.


@dp.message_handler(commands=['cancel'])
async def photo_processing(message: types.Message):
    """Allows the user to select a different image with content or style."""

    global flag
    global content_flag
    if not content_flag:
        await message.answer(text="You haven't uploaded the content image yet.")
        return

    if flag:
        flag = False
    else:
        flag = True
    await message.answer(text='Successfully!')


@dp.message_handler(commands=['continue'])
async def continue_processing(message: types.Message):
    """Preparing for image processing."""


    if not (content_flag * style_flag):
        await message.answer(text="You haven't uploaded both images yet. ")
        return

    # Adding answer options.
    res = types.ReplyKeyboardMarkup(resize_keyboard=True,
                                    one_time_keyboard=True)
    res.add(types.KeyboardButton(text="small size(128x128)"))
    res.add(types.KeyboardButton(text="full size"))

    await message.answer(text= "Now please choose the resolution. \n"
                              " If you want to start all over again at this"
                              " step, just send me the content image again,"
                              " and then the style image.", reply_markup=res)


@dp.message_handler(lambda message: message.text in ("small size(128x128)", "full size" ))
async def processing(message: types.Message):
    """Image processing depending on the selected quality."""
    chat_id_str=str(message.chat.id)
    if message.text == 'small size(128x128)':
        image_size = 128
    else :
        image_size = None

    print("user: ",chat_id_str,"size: ",image_size)
    await message.answer(text='Style transfer has started. Please wait',
                         reply_markup=types.ReplyKeyboardRemove())

    transform('content'+chat_id_str+'.jpg', 'style'+chat_id_str+'.jpg', 'result'+chat_id_str+'.jpg',image_size)
    with open('result'+chat_id_str+'.jpg', 'rb') as file:
        await message.answer_photo(file )



if __name__ == '__main__':
    print("Style transfer bot starting: ")
    executor.start_polling(dp, skip_updates=True)