import asyncio
import mysql.connector
from tabulate import tabulate
import cursor as cursor
import random
import discord
from discord.ext import commands
from config import settings


#База данных SQLite
#conn = sqlite3.connect("Discord.db")
#cursor = conn.cursor()

#База данных MYSQL
mydb = mysql.connector.connect(
    host="127.0.0.1",#Your host db
    user=("user"),#Your username db
    password=("password"),#Your password db
    database="dis_bot"# name db
)
mycursor = mydb.cursor()



intents = discord.Intents.all()
bot = commands.Bot(command_prefix=settings['prefix'],  intents=intents)

@bot.event
async def on_ready():
    print("Bot Has been runned")#сообщение о готовности
    for guild in bot.guilds:#т.к. бот для одного сервера, то и цикл выводит один сервер
        mycursor.execute("SHOW TABLES FROM dis_bot")
        ret = mycursor.fetchall()
        g = 0
        table_list = [x[0] for x in ret]
        table_string = ', '.join([x[0] for x in ret])
        for er in table_list:
            if guild.name == er:
                g = 1
        if g != 1:
            print(guild.id)
            sql = f"""CREATE TABLE {guild.name} (
      id int(11) NOT NULL AUTO_INCREMENT,
      id_dis varchar(45) DEFAULT NULL,
      name varchar(45) DEFAULT NULL,
      lvl varchar(45) DEFAULT NULL,
      xp varchar(45) DEFAULT NULL,
      PRIMARY KEY (id)
    ) ENGINE=InnoDB AUTO_INCREMENT=79 DEFAULT CHARSET=utf8mb4"""
            mycursor.execute(sql)
            mydb.commit()
        for member in guild.members: # цикл, обрабатывающий список участников
            mycursor.execute(f"SELECT id FROM {guild.name} WHERE id_dis={member.id}") # проверка, существует ли участник в БД
            if mycursor.fetchone()==None:#Если не существует
                print(member.name)
                sql = f"INSERT INTO {guild.name} (id_dis, name, lvl, xp) VALUES (%s, %s, %s, %s)"
                val = (member.id, member.name, "1", "0")
                mycursor.execute(sql, val)

                mydb.commit()

            else:#если существует
                pass
    mydb.commit()#применение изменений в БД




@bot.event
async def on_member_join():
    for guild in bot.guilds:
        for member in guild.members:  # цикл, обрабатывающий список участников
            mycursor.execute(
                f"SELECT id FROM {guild.name} WHERE id_dis={member.id}")  # проверка, существует ли участник в БД
            if mycursor.fetchone() == None:  # Если не существует
                print(member.name)
                sql = f"INSERT INTO {guild.name} (id_dis, name, lvl, xp) VALUES (%s, %s, %s, %s)"
                val = (member.id, member.name, "1", "0")
                mycursor.execute(sql, val)

                mydb.commit()

            else:  # если существует
                pass


      # применение изменений в БД

@bot.event
async def on_message(message):
    if len(message.content) > 2:#за каждое сообщение длиной > 10 символов...
        mycursor.execute(f"SELECT xp FROM {message.guild.name} where id_dis={message.author.id}")
        ret = mycursor.fetchall()
        table_list = [x[0] for x in ret]
        print(message.guild.name)
        print(message.author.name)
        expt = int(int(table_list[0])+random.randint(5, 40))#к опыту добавляется случайное число
        print(expt)
        mycursor.execute(f'UPDATE {message.guild.name} SET xp={expt} where id_dis={message.author.id}')
        mydb.commit()
        mycursor.execute(f"SELECT lvl FROM {message.guild.name} where id_dis={message.author.id}")
        rek = mycursor.fetchall()

        table_list1 = [x[0] for x in rek]

        r = int(table_list[0])/(1000*int(table_list1[0]))
        if int(table_list1[0]) < r:#если текущий уровень меньше уровня, который был рассчитан формулой выше,...
            await message.channel.send(str(message.author.name)+' получил(а) '+str(int(table_list1[0])+1)+' уровень!')#то появляется уведомление...
            mycursor.execute(f'UPDATE {message.guild.name} SET lvl=lvl+1 where id_dis={message.author.id}')#и участник получает деньги
            mydb.commit()
    await bot.process_commands(message)#Далее это будет необходимо для ctx команд
   #применение изменений в БД


@bot.command()
async def account(ctx): #команда _account (где "_", ваш префикс указаный в начале)
    table=[["name", "money", "lvl", "xp"]]
    for row in cursor.execute(f"SELECT nickname,money,lvl,xp FROM users where id={ctx.author.id}"):
        table.append([row[0], row[1], row[2], row[3]])
        await ctx.send(f">\n{tabulate(table)}")

@bot.command()
async def mute (ctx,member:discord.Member, time: int, reason):
    mute = discord.utils.get(ctx.message.guild.roles, name = 'mute')
    lol = discord.Embed(title = 'В муте. Говорить не может!')
    lol.add_field(name = 'Модератор/админ', value = ctx.message.author.mention, inline = False)
    lol.add_field(name = 'Нарушитель', value = member.mention, inline = False)
    lol.add_field(name= 'Причина', value = reason, inline = False)
    lol.add_field (name = 'Время', value = time, inline = False)
    await member.add_roles (mute)
    await ctx.channel.send(embed = lol)
    await asyncio.sleep(time * 60)
    await member.remove_roles (mute)



@bot.command()
async def add(ctx, left: int, right: int):
    """Adds two numbers together."""
    await ctx.send(left + right)

bot.run(settings['token'])
