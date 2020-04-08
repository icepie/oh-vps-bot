import psutil
from datetime import datetime
import telebot

bot = telebot.TeleBot("")

user = bot.get_me()

def get_stats():
    memory = psutil.virtual_memory()
    disk = psutil.disk_usage('/')
    boottime = datetime.fromtimestamp(psutil.boot_time())
    now = datetime.now()
    timedif = "在线时间: %.1f 小时" % (((now - boottime).total_seconds()) / 3600)
    memtotal = "总内存: %.2f GB " % (memory.total / 1000000000)
    memavail = "可用内存: %.2f GB" % (memory.available / 1000000000)
    memuseperc = "使用内存: " + str(memory.percent) + " %"
    diskused = "磁盘占用: " + str(disk.percent) + " %"
    cpu = "当前CPU占用率" + str(psutil.cpu_percent(interval=1)) + "%"
    pids = psutil.pids()
    pidsreply = ''

    reply = timedif + "\n" + \
            memtotal + "\n" + \
            memavail + "\n" + \
            memuseperc + "\n" + \
            diskused + "\n" + \
            cpu + "\n" + \
            pidsreply
    return(reply)

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
	bot.reply_to(message, "/stats 查看系统状态")

@bot.message_handler(commands=['stats'])
def send_stats(message):
    print(message.chat.id)
    bot.send_chat_action(message.chat.id,'typing')
    bot.reply_to(message, get_stats())
    
@bot.message_handler(func=lambda message: True)
def echo_all(message):
	bot.reply_to(message, message.text)

bot.polling()