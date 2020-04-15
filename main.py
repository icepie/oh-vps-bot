import psutil
from datetime import datetime
import telebot
import operator

from telebot import types
from subprocess import Popen, PIPE, STDOUT

# your bot conf
bot = telebot.TeleBot("")

user = bot.get_me()

# global
_global_dict = None


def _init():
    global _global_dict
    _global_dict = {}


def set_value(key, value):
    """ set global variable """
    _global_dict[key] = value


def get_value(key, defValue=None):
    """ to obtain a global variable, if does not exist, it returns the default value """
    try:
        return _global_dict[key]
    except KeyError:
        return defValue


def get_stats():
    memory = psutil.virtual_memory()
    disk = psutil.disk_usage('/')
    boottime = datetime.fromtimestamp(psutil.boot_time())
    now = datetime.now()
    timedif = "Uptime: %.1f H" % (((now - boottime).total_seconds()) / 3600)
    memtotal = "TotalMemory: %.2f GB " % (memory.total / 1000000000)
    memavail = "AvailMemory: %.2f GB" % (memory.available / 1000000000)
    memuseperc = "UsedMemory: " + str(memory.percent) + " %"
    diskused = "Disk: " + str(disk.percent) + " %"
    cpu = "CPU: " + str(psutil.cpu_percent(interval=1)) + "%"
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


def get_task():
    pids = psutil.pids()
    pidsreply = ''
    procs = {}
    for pid in pids:
        p = psutil.Process(pid)
        try:
            pmem = p.memory_percent()
            if pmem > 0.5:
                if p.name() in procs:
                    procs[p.name()] += pmem
                else:
                    procs[p.name()] = pmem
        except:
            print("Hm")
    sortedprocs = sorted(
        procs.items(), key=operator.itemgetter(1), reverse=True)
    for proc in sortedprocs:
        pidsreply += proc[0] + " " + ("%.2f" % proc[1]) + " %\n"
    return(pidsreply)


def shell_input(self):
    p = Popen(self, shell=True, stdin=PIPE, stdout=PIPE, stderr=STDOUT, close_fds=True)
    output = p.stdout.read()
    if output != b'':
        return(output)
    else:
        return('void output')


def main():
    @bot.message_handler(commands=['start', 'help'])
    def send_welcome(message):
        welcome_reply =  "/help Get the user guide" + "\n" + \
            "/stats Check the system status" + "\n" + \
            "/task  Check the daemon" + "\n" + \
            "/shell Into the shell mode" + "\n" + \
            "... more function" + "\n"
        bot.reply_to(message, welcome_reply)

    @bot.message_handler(commands=['stats'])
    def send_stats(message):
        print(message.chat.id)
        bot.send_chat_action(message.chat.id, 'typing')
        bot.reply_to(message, get_stats())

    @bot.message_handler(commands=['task'])
    def send_task(message):
        print(message.chat.id)
        bot.send_chat_action(message.chat.id, 'typing')
        bot.reply_to(message, get_task())

    @bot.message_handler(commands=['shell'])
    def shell_mode(message):
        markup = types.ReplyKeyboardMarkup(row_width=2, one_time_keyboard=True)
        btn = types.KeyboardButton('stop')
        markup.add(btn)
        bot.send_message(message.chat.id, "Send me a command to execute", reply_markup=markup)
        shell_dev(message)
        # set shell mode on
        set_value('shell_on', 1)

    @bot.message_handler(func=lambda message: True)
    def shell_dev(message):
        if message.text == 'stop':
            bot.send_message(message.chat.id, "Done!", reply_markup=bot.types.ReplyKeyboardRemove())
            # set shell mode off
            set_value('shell_on', 0)
        elif get_value('shell_on') == 1:
            bot.send_chat_action(message.chat.id, 'typing')
            bot.send_message(message.chat.id, shell_input(
                message.text), disable_web_page_preview=True)
        pass

    # let the bot always run
    bot.polling(none_stop=True)


if __name__ == "__main__":
    _init()
    main()
