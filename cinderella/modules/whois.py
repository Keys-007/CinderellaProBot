#Modificatins by Sur_vivor & Me
import html
import json
import os
import psutil
import random
import time
import datetime
from typing import Optional, List
import re
import requests
from telegram.error import BadRequest
from telegram import Message, Chat, Update, Bot, MessageEntity
from telegram import ParseMode
from telegram.ext import CommandHandler, run_async, Filters
from telegram.utils.helpers import escape_markdown, mention_html
from cinderella.modules.helper_funcs.chat_status import user_admin, sudo_plus, is_user_admin
from cinderella import dispatcher, OWNER_ID, SUDO_USERS, SUPPORT_USERS, DEV_USERS, WHITELIST_USERS
from cinderella.__main__ import STATS, USER_INFO, TOKEN
from cinderella.modules.disable import DisableAbleCommandHandler, DisableAbleRegexHandler
from cinderella.modules.helper_funcs.extraction import extract_user
from cinderella.modules.helper_funcs.filters import CustomFilters
import cinderella.modules.sql.users_sql as sql
import cinderella.modules.helper_funcs.cas_api as cas

@run_async
def info(bot: Bot, update: Update, args: List[str]):
    message = update.effective_message
    chat = update.effective_chat
    user_id = extract_user(update.effective_message, args)

    if user_id:
        user = bot.get_chat(user_id)

    elif not message.reply_to_message and not args:
        user = message.from_user

    elif not message.reply_to_message and (not args or (
            len(args) >= 1 and not args[0].startswith("@") and not args[0].isdigit() and not message.parse_entities(
        [MessageEntity.TEXT_MENTION]))):
        message.reply_text("I can't extract a user from this.")
        return

    else:
        return
    
    text = (f"<b>User Information:</b>\n"
            f"ID: <code>{user.id}</code>\n"
            f"Name: {html.escape(user.first_name)}")

    if user.last_name:
        text += f"\nLast Name: {html.escape(user.last_name)}"

    if user.username:
        text += f"\nUsername: @{html.escape(user.username)}"

    text += f"\nPermanent user link: {mention_html(user.id, 'link')}"

    num_chats = sql.get_user_num_chats(user.id)
    text += f"\nChat count: <code>{num_chats}</code>"
    text += "\nNumber of profile pics: {}".format(bot.get_user_profile_photos(user.id).total_count)
   
    try:
        user_member = chat.get_member(user.id)
        if user_member.status == 'administrator':
            result = requests.post(f"https://api.telegram.org/bot{TOKEN}/getChatMember?chat_id={chat.id}&user_id={user.id}")
            result = result.json()["result"]
            if "custom_title" in result.keys():
                custom_title = result['custom_title']
                text += f"\n⚜️This user holds the title⚜️ <b>{custom_title}</b> here."
    except BadRequest:
        pass

   

    if user.id == OWNER_ID:
        text += "\n Yeah ,This Guy Is My Owner \nI Owe Him The Most!."
        
    elif user.id in DEV_USERS:
        text += "\nWew,This person is my dev👨🏻‍💻\nI Owe A Lot To Him!."     
        
    elif user.id in SUDO_USERS:
        text += "\nThis person is one of my sudo users ❤️! " \
                    "Nearly as powerful as my owner⚡so watch it.."
        
    elif user.id in SUPPORT_USERS:
        text += "\nThis person is one of my support users! " \
                        "Not quite a sudo user, but can still gban you off the map."
        
  
       
    elif user.id in WHITELIST_USERS:
        text += "\nThis person has been whitelisted! " \
                        "That means I'm not allowed to ban/kick them."
    elif user.id == bot.id:     
        text += "\nLol It's Me 😂"


        try:
            mod_info = mod.__user_info__(user.id)
        except TypeError:
            mod_info = mod.__user_info__(user.id, chat.id)
        if mod_info:
            text += "\n" + mod_info
    update.effective_message.reply_text(text, parse_mode=ParseMode.HTML, disable_web_page_preview=True)

INFO_HANDLER = DisableAbleCommandHandler(["info", "whois"],  info, pass_args=True)
dispatcher.add_handler(INFO_HANDLER)
