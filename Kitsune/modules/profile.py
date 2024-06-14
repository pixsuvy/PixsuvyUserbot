import os
from asyncio import sleep

from pyrogram import Client, filters
from pyrogram.types import Message

from config import CMD_HANDLER as cmd
from Kitsune.helpers.basic import edit_or_reply
from Kitsune.helpers.PyroHelpers import ReplyCheck
from Kitsune.utils.misc import extract_user

from .help import add_command_help

flood = {}
profile_photo = "Kitsune/modules/cache/pfp.jpg"


@Client.on_message(filters.command(["block"], cmd) & filters.me)
async def block_user_func(client: Client, message: Message):
    user_id = await extract_user(message)
    pix = await edit_or_reply(message, "`Processing . . .`")
    if not user_id:
        return await message.edit(
            "Provide User ID/Username or reply to user message to unblock."
        )
    if user_id == client.me.id:
        return await pix.edit("you are stressed please take medicine immediately.")
    await client.block_user(user_id)
    umention = (await client.get_users(user_id)).mention
    await message.edit(f"**Successfully Blocked** {umention}")


@Client.on_message(filters.command(["unblock"], cmd) & filters.me)
async def unblock_user_func(client: Client, message: Message):
    user_id = await extract_user(message)
    pix = await edit_or_reply(message, "`Processing . . .`")
    if not user_id:
        return await message.edit(
            "Provide User ID/Username or reply to user message to unblock."
        )
    if user_id == client.me.id:
        return await pix.edit("you are stressed please take medicine immediately.")
    await client.unblock_user(user_id)
    umention = (await client.get_users(user_id)).mention
    await message.edit(f"**Unblock Success** {umention}")


@Client.on_message(filters.command(["setname"], cmd) & filters.me)
async def setname(client: Client, message: Message):
    pix = await edit_or_reply(message, "`Processing . . .`")
    if len(message.command) == 1:
        return await pix.edit("Provide a text to set as your telegram name.")
    elif len(message.command) > 1:
        name = message.text.split(None, 1)[1]
        try:
            await client.update_profile(first_name=name)
            await pix.edit(f"**Successfully Changed Your Telegram Name To** `{name}`")
        except Exception as e:
            await pix.edit(f"**ERROR:** `{e}`")
    else:
        return await pix.edit("Provide a text to set as your telegram name.")


@Client.on_message(filters.command(["setbio"], cmd) & filters.me)
async def set_bio(client: Client, message: Message):
    pix = await edit_or_reply(message, "`Processing . . .`")
    if len(message.command) == 1:
        return await pix.edit("Provide text to set as bio.")
    elif len(message.command) > 1:
        bio = message.text.split(None, 1)[1]
        try:
            await client.update_profile(bio=bio)
            await pix.edit(f"**Successfully Changed your BIO to** `{bio}`")
        except Exception as e:
            await pix.edit(f"**ERROR:** `{e}`")
    else:
        return await pix.edit("Provide text to set as bio.")


@Client.on_message(filters.me & filters.command(["setpfp"], cmd))
async def set_pfp(client: Client, message: Message):
    replied = message.reply_to_message
    if (
        replied
        and replied.media
        and (
            replied.photo
            or (replied.document and "image" in replied.document.mime_type)
        )
    ):
        await client.download_media(message=replied, file_name=profile_photo)
        await client.set_profile_photo(profile_photo)
        if os.path.exists(profile_photo):
            os.remove(profile_photo)
        await message.edit("**Your Profile Photo Changed Successfully.**")
    else:
        await message.edit("`Reply to any photo to set as profile photo`")
        await sleep(3)
        await message.delete()


@Client.on_message(filters.me & filters.command(["poto"], cmd))
async def view_pfp(client: Client, message: Message):
    user_id = await extract_user(message)
    if user_id:
        user = await client.get_users(user_id)
    else:
        user = await client.get_me()
    if not user.photo:
        await message.edit("Profile photo not found!")
        return
    await client.download_media(user.photo.big_file_id, file_name=profile_photo)
    await client.send_photo(
        message.chat.id, profile_photo, reply_to_message_id=ReplyCheck(message)
    )
    await message.delete()
    if os.path.exists(profile_photo):
        os.remove(profile_photo)


add_command_help(
    "profile",
    [
        ["block", "To block telegram users"],
        ["unblock", "To unblock a user you have blocked"],
        ["setname", "To Rename Telegram."],
        ["setbio", "To Change Telegram Bio."],
        [
            "setpfp",
            f"Reply To Picture Type {cmd}setpfp To Change Telegram Profile Picture.",
        ],
        ["poto", "To view the current user's profile photo."],
    ],
)
