import pandas as pd
import requests
import telebot
import os
import dataframe_image as dfi


bot = telebot.TeleBot("6212330584:AAERNIFhQFWs1EYpVPPBrX4Koms9t0UbaJs")
url = "https://openwater-os.secure-platform.com/societypetroleumengineers/prefill?emailOrUserId="

state = "0"

# getting one member info by id
def manualMemberInfo(ID):
    req = requests.get(url + str(ID), auth=('user', 'pass'))
    req = req.json()
    if req['success'] == True:
        data = req['data']['fields']
        df = pd.DataFrame(data)
        df = df.rename(columns={"alias": "Property",
                            "value": "Value"})
        dfi.export(df, "./MemberInfo.png", table_conversion="matplotlib")
        return df.to_string()
    else:
        return False

# getting a group of members info from a file
def automaticMemberInfo(ID_col_name):
    filePath = "./before.xlsx"
    idsColumnName = ID_col_name
    df = pd.read_excel(filePath)
    ids = df[idsColumnName]
    a = pd.DataFrame(columns=["ID", "collegeUniversityName", "isMembershipPaid"])
    ID = []
    collegeUniversityName = []
    isMembershipPaid = []
    for e in ids:
        try:
            req = requests.get(
                url + (str(e)[1:] if str(e)[0] == "#" else str(e)), auth=("user", "pass")
            )
            req = req.json()["data"]["fields"]
            df = pd.DataFrame(req)
            ID.append(df.iloc[2, 1])
            collegeUniversityName.append(df.iloc[0, 1])
            isMembershipPaid.append(df.iloc[9, 1])
        except:
            ID.append(e)
            collegeUniversityName.append("ID not Found")
            isMembershipPaid.append("ID not Found")
    a["ID"] = ID
    a["collegeUniversityName"] = collegeUniversityName
    a["isMembershipPaid"] = isMembershipPaid
    a.to_excel("./Done.xlsx")



########################################################
buttons = telebot.types.ReplyKeyboardMarkup(True, True, row_width=2)
idbutton = telebot.types.KeyboardButton("Check ID")
filebutton = telebot.types.KeyboardButton("Check a File")
buttons.add(idbutton, filebutton)

backbutton = telebot.types.ReplyKeyboardMarkup(True, True, row_width=1)
back = telebot.types.KeyboardButton("Back")
backbutton.add(back)

########################################################

permission = ["tanx_cotx", "kr_138", "AbdulA_Z", "hu_basil"]

########################################################
@bot.message_handler(func=lambda msg: msg.chat.username not in permission)
def unknownUser(message):
    bot.send_message(chat_id=message.chat.id, text="sorry you don't have permission to use this bot\ncontact: @tanx_cotx".title())
@bot.message_handler(commands = ['start', 'Start'])
def welcome(message):
    global state, buttons
    bot.send_message(chat_id=message.chat.id, text="Welcome")
    bot.send_message(chat_id=message.chat.id, text="this bot checks members info, choose a method".title(), reply_markup=buttons)
    state = "1"

@bot.message_handler(func=lambda msg: state=="-1")
def startAgain(message):
    global state, buttons
    # bot.send_message(chat_id=message.chat.id, text="choose a method".title(), reply_markup=buttons)
    state = "1"
########################################################
# State 1A: Check ID
@bot.message_handler(func = lambda msg: msg.text == "Check ID" and state == "1")
def checkID(message):
    global state, backbutton
    state = "1A"
    checkIDinput(message)
@bot.message_handler(func = lambda msg: state == "1A")
def checkIDinput(message):
    global state, backbutton
    bot.send_message(chat_id=message.chat.id, text="Input ID or Email", reply_markup=backbutton)
    state = "1A.input"
@bot.message_handler(func=lambda msg: (state == "1A.input" and msg.text != "Back"))
def get_info(message):
    global state, backbutton
    id = message.text
    info = manualMemberInfo(id)
    if info:
        bot.send_message(chat_id=message.chat.id, text=info)
        with open("./MemberInfo.png", "rb") as doc:
            bot.send_document(chat_id=message.chat.id, document=doc, reply_markup=buttons)
        startAgain(message)
    else:
        bot.send_message(chat_id=message.chat.id, text="Member not found")
########################################################
# State 1B: Check a File
@bot.message_handler(func = lambda msg: msg.text == "Check a File" and state == "1")
def checkFile(message):
    global state, backbutton
    state == "1B"
    checkFileInput(message)
@bot.message_handler(func = lambda msg: state == "1B")
def checkFileInput(message):
    global state, backbutton
    bot.send_message(chat_id=message.chat.id, text="Send Your File In xlsx Format", reply_markup=backbutton)
    state = "1B.file"
@bot.message_handler(func=lambda msg: state == "1B.file", content_types=["document"])
def getFile(message):
    global state, backbutton
    if message.document.file_name.endswith("xlsx"):
        file_info = bot.get_file(message.document.file_id)
        file = bot.download_file(file_info.file_path)
        try:
            os.remove(f"./before.xlsx")
        except:
            pass
        with open (f"./before.xlsx", "wb") as downloaded:
            downloaded.write(file)
        bot.send_message(chat_id=message.chat.id, text="File Accepted, Input IDs' Column Name", reply_markup=backbutton)
        state = "1B.input"
    else:
        bot.send_message(chat_id=message.chat.id, text="File Not Accepted, Send Your File Again")
@bot.message_handler(func=lambda msg: state == "1B.file" and msg.text != "Back")
def getFileNotText(message):
    global state, backbutton
    bot.send_message(chat_id=message.chat.id, text="This is not a file")
@bot.message_handler(func=lambda msg: state == "1B.input" and msg.text != "Back")
def getColumnName(message):
    try:
        automaticMemberInfo(message.text)
        with open ("./Done.xlsx", "rb") as doc:
            bot.send_document(chat_id=message.chat.id, document=doc, reply_markup=buttons)
        startAgain(message)
    except:
        bot.send_message(chat_id=message.chat.id, text="Name Error")
########################################################
@bot.message_handler(func = lambda msg: msg.text == "Back")
def back(message):
    global state
    match state:
        case "1B.file" | "1A.input":
            bot.send_message(chat_id=message.chat.id, text="choose a method".title(), reply_markup=buttons)
            startAgain(message)
        case "1B.input":
            checkFile(message)
########################################################
bot.polling()