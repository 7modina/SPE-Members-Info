import pandas as pd
import requests
import telebot



url = "https://openwater-os.secure-platform.com/societypetroleumengineers/prefill?emailOrUserId="


# Manual ID Check


bot = telebot.TeleBot('6698520377:AAHxmwFGX6CNEI-59Jl3R52n-JOZauVOs5g')

usernames = ["tanx_cotx", "kr_138", "AbdulA_Z", "hu_basil"]


@bot.message_handler(commands=["start", "Start"])
def inputMessage(message):
    if message.chat.username in usernames:
        bot.send_message(chat_id=message.chat.id, text=f"Input ID or Email by Replying to This Message\nMake sure that ID doesn't have \"#\"")
    else:
        print(message.chat.username)
        bot.send_message(chat_id=message.chat.id, text="Sorry You Don't Have The Permission To Use This Bot")
@bot.message_handler(func=lambda msg: True)
def input(message):
    if message.chat.username in usernames:
        try:
            if message.reply_to_message.text == f"Input ID or Email by Replying to This Message\nMake sure that ID doesn't have \"#\"":
                try:
                    id = str(message.text).strip()
                    print(id)
                    req = requests.get(url + id, auth=('user', 'pass'))
                    req = req.json()
                    if req['success'] == True:
                        data = req['data']['fields']
                        df = pd.DataFrame(data)
                        bot.send_message(chat_id=message.chat.id, text=df.to_string())
                    else:
                        bot.send_message(chat_id=message.chat.id, text="Member Not Found")
                except:
                    bot.send_message(chat_id=message.chat.id, text="An Error Ocurred Try Again")
        except:
            pass
    else:
        print(message.chat.username)
        bot.send_message(chat_id=message.chat.id, text="Sorry You Don't Have The Permission To Use This Bot")
bot.polling()
