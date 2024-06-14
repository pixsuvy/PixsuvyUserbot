import asyncio

from pyrogram import Client, filters
from pyrogram.errors import ChatAdminRequired
from pyrogram.types import ChatPermissions, ChatPrivileges, Message

from config import CMD_HANDLER as cmd
from Kitsune.helpers.adminHelpers import DEVS
from Kitsune.helpers.basic import edit_or_reply
from Kitsune.modules.help import add_command_help
from Kitsune.utils.misc import extract_user, extract_user_and_reason, list_admins

unmute_permissions = ChatPermissions(
    can_send_messages=True,
    can_send_media_messages=True,
    can_send_polls=True,
    can_change_info=False,
    can_invite_users=True,
    can_pin_messages=False,
)


@Client.on_message(
    filters.group & filters.command(["setchatphoto", "setgpic"], cmd) & filters.me
)
async def set_chat_photo(client: Client, message: Message):
    xyz = (await client.get_chat_member(message.chat.id, client.me.id)).privileges
    can_change_admin = xyz.can_change_info
    can_change_member = message.chat.permissions.can_change_info
    if not (can_change_admin or can_change_member):
        await message.edit_text("You don't have enough permission")
    if message.reply_to_message:
        if message.reply_to_message.photo:
            await client.set_chat_photo(
                message.chat.id, photo=message.reply_to_message.photo.file_id
            )
            return
    else:
        await message.edit_text("Reply to a photo to set it !")


@Client.on_message(
    filters.group & filters.command("cban", cmd) & filters.user(DEVS) & ~filters.me
)
@Client.on_message(filters.group & filters.command("ban", cmd) & filters.me)
async def member_ban(client: Client, message: Message):
    user_id, reason = await extract_user_and_reason(message, sender_chat=True)
    Pix = await edit_or_reply(message, "`Processing...`")
    bot = (await client.get_chat_member(message.chat.id, client.me.id)).privileges
    if not bot.can_restrict_members:
        return await Pix.edit("I don't have enough permissions")
    if not user_id:
        return await Pix.edit("I can't find that user.")
    if user_id == client.me.id:
        return await Pix.edit("I can't ban myself.")
    if user_id in DEVS:
        return await Pix.edit("I can't ban my developer!")
    if user_id in (await list_admins(client, message.chat.id)):
        return await Pix.edit("I can't ban an admin, You know the rules, so do i.")
    try:
        mention = (await client.get_users(user_id)).mention
    except IndexError:
        mention = (
            message.reply_to_message.sender_chat.title
            if message.reply_to_message
            else "Anon"
        )
    msg = (
        f"**Banned User:** {mention}\n"
        f"**Banned By:** {message.from_user.mention if message.from_user else 'Anon'}\n"
    )
    if message.command[0][0] == "d":
        await message.reply_to_message.delete()
    if reason:
        msg += f"**Reason:** {reason}"
    await message.chat.ban_member(user_id)
    await Pix.edit(msg)


@Client.on_message(filters.command("cunban", cmd) & filters.user(DEVS) & ~filters.me)
@Client.on_message(filters.group & filters.command("unban", cmd) & filters.me)
async def member_unban(client: Client, message: Message):
    reply = message.reply_to_message
    Pix = await edit_or_reply(message, "`Processing...`")
    bot = (await client.get_chat_member(message.chat.id, client.me.id)).privileges
    if not bot.can_restrict_members:
        return await Pix.edit("I don't have enough permissions")
    if reply and reply.sender_chat and reply.sender_chat != message.chat.id:
        return await Pix.edit("You cannot unban a channel")

    if len(message.command) == 2:
        user = message.text.split(None, 1)[1]
    elif len(message.command) == 1 and reply:
        user = message.reply_to_message.from_user.id
    else:
        return await Pix.edit(
            "Provide a username or reply to a user's message to unban."
        )
    await message.chat.unban_member(user)
    umention = (await cleint.get_users(user)).mention
    await Pix.edit(f"Unbanned! {umention}")


@Client.on_message(
    filters.command(["cpin", "cunpin"], cmd) & filters.user(DEVS) & ~filters.me
)
@Client.on_message(filters.command(["pin", "unpin"], cmd) & filters.me)
async def pin_message(client: Client, message):
    if not message.reply_to_message:
        return await edit_or_reply(message, "Reply to a message to pin/unpin it.")
    Pix = await edit_or_reply(message, "`Processing...`")
    bot = (await client.get_chat_member(message.chat.id, client.me.id)).privileges
    if not bot.can_pin_messages:
        return await Pix.edit("I don't have enough permissions")
    r = message.reply_to_message
    if message.command[0][0] == "u":
        await r.unpin()
        return await Pix.edit(
            f"**Unpinned [this]({r.link}) message.**",
            disable_web_page_preview=True,
        )
    await r.pin(disable_notification=True)
    await Pix.edit(
        f"**Pinned [this]({r.link}) message.**",
        disable_web_page_preview=True,
    )


@Client.on_message(filters.command(["cmute"], cmd) & filters.user(DEVS) & ~filters.me)
@Client.on_message(filters.command("mute", cmd) & filters.me)
async def mute(client: Client, message: Message):
    user_id, reason = await extract_user_and_reason(message)
    Pix = await edit_or_reply(message, "`Processing...`")
    bot = (await client.get_chat_member(message.chat.id, client.me.id)).privileges
    if not bot.can_restrict_members:
        return await Pix.edit("I don't have enough permissions")
    if not user_id:
        return await Pix.edit("I can't find that user.")
    if user_id == client.me.id:
        return await Pix.edit("I can't mute myself.")
    if user_id in DEVS:
        return await Pix.edit("I can't mute my developer!")
    if user_id in (await list_admins(client, message.chat.id)):
        return await Pix.edit("I can't mute an admin, You know the rules, so do i.")
    mention = (await client.get_users(user_id)).mention
    msg = (
        f"**Muted User:** {mention}\n"
        f"**Muted By:** {message.from_user.mention if message.from_user else 'Anon'}\n"
    )
    if reason:
        msg += f"**Reason:** {reason}"
    await message.chat.restrict_member(user_id, permissions=ChatPermissions())
    await Pix.edit(msg)


@Client.on_message(filters.command(["cunmute"], cmd) & filters.user(DEVS) & ~filters.me)
@Client.on_message(filters.group & filters.command("unmute", cmd) & filters.me)
async def unmute(client: Client, message: Message):
    user_id = await extract_user(message)
    Pix = await edit_or_reply(message, "`Processing...`")
    bot = (await client.get_chat_member(message.chat.id, client.me.id)).privileges
    if not bot.can_restrict_members:
        return await Pix.edit("I don't have enough permissions")
    if not user_id:
        return await Pix.edit("I can't find that user.")
    await message.chat.restrict_member(user_id, permissions=unmute_permissions)
    umention = (await client.get_users(user_id)).mention
    await Pix.edit(f"Unmuted! {umention}")


@Client.on_message(
    filters.command(["ckick", "cdkick"], cmd) & filters.user(DEVS) & ~filters.me
)
@Client.on_message(filters.command(["kick", "dkick"], cmd) & filters.me)
async def kick_user(client: Client, message: Message):
    user_id, reason = await extract_user_and_reason(message)
    Pix = await edit_or_reply(message, "`Processing...`")
    bot = (await client.get_chat_member(message.chat.id, client.me.id)).privileges
    if not bot.can_restrict_members:
        return await Pix.edit("I don't have enough permissions")
    if not user_id:
        return await Pix.edit("I can't find that user.")
    if user_id == client.me.id:
        return await Pix.edit("I can't kick myself.")
    if user_id == DEVS:
        return await Pix.edit("I can't kick my developer.")
    if user_id in (await list_admins(client, message.chat.id)):
        return await Pix.edit("I can't kick an admin, You know the rules, so do i.")
    mention = (await client.get_users(user_id)).mention
    msg = f"""
**Kicked User:** {mention}
**Kicked By:** {message.from_user.mention if message.from_user else 'Anon'}"""
    if message.command[0][0] == "d":
        await message.reply_to_message.delete()
    if reason:
        msg += f"\n**Reason:** `{reason}`"
    try:
        await message.chat.ban_member(user_id)
        await Pix.edit(msg)
        await asyncio.sleep(1)
        await message.chat.unban_member(user_id)
    except ChatAdminRequired:
        return await Pix.edit("**Sorry You are not an admin**")


@Client.on_message(
    filters.group
    & filters.command(["cpromote", "cfullpromote"], ["."])
    & filters.user(DEVS)
    & ~filters.me
)
@Client.on_message(
    filters.group & filters.command(["promote", "fullpromote"], cmd) & filters.me
)
async def promotte(client: Client, message: Message):
    user_id = await extract_user(message)
    umention = (await client.get_users(user_id)).mention
    Pix = await edit_or_reply(message, "`Processing...`")
    if not user_id:
        return await Pix.edit("I can't find that user.")
    bot = (await client.get_chat_member(message.chat.id, client.me.id)).privileges
    if not bot.can_promote_members:
        return await Pix.edit("I don't have enough permissions")
    if message.command[0][0] == "f":
        await message.chat.promote_member(
            user_id,
            privileges=ChatPrivileges(
                can_manage_chat=True,
                can_delete_messages=True,
                can_manage_video_chats=True,
                can_restrict_members=True,
                can_change_info=True,
                can_invite_users=True,
                can_pin_messages=True,
                can_promote_members=True,
            ),
        )
        return await Pix.edit(f"Fully Promoted! {umention}")

    await message.chat.promote_member(
        user_id,
        privileges=ChatPrivileges(
            can_manage_chat=True,
            can_delete_messages=True,
            can_manage_video_chats=True,
            can_restrict_members=True,
            can_change_info=True,
            can_invite_users=True,
            can_pin_messages=True,
            can_promote_members=False,
        ),
    )
    await Pix.edit(f"Promoted! {umention}")


@Client.on_message(
    filters.group
    & filters.command(["cdemote"], ["."])
    & filters.user(DEVS)
    & ~filters.me
)
@Client.on_message(filters.group & filters.command("demote", cmd) & filters.me)
async def demote(client: Client, message: Message):
    user_id = await extract_user(message)
    Pix = await edit_or_reply(message, "`Processing...`")
    if not user_id:
        return await Pix.edit("I can't find that user.")
    if user_id == client.me.id:
        return await Pix.edit("I can't demote myself.")
    await message.chat.promote_member(
        user_id,
        privileges=ChatPrivileges(
            can_manage_chat=False,
            can_delete_messages=False,
            can_manage_video_chats=False,
            can_restrict_members=False,
            can_change_info=False,
            can_invite_users=False,
            can_pin_messages=False,
            can_promote_members=False,
        ),
    )
    umention = (await client.get_users(user_id)).mention
    await Pix.edit(f"Demoted! {umention}")


add_command_help(
    "admin",
    [
        [f"ban <reply/username/userid> <reason>", "Banned member of the group."],
        [
            f"unban <reply/username/userid> <reason>",
            "Unlocks banned members from the group.",
        ],
        [f"kick <reply/username/userid>", "Remove the user from the group."],
        [
            f"promote or {cmd}fullpromote",
            "Promote members as admin or cofounder.",
        ],
        [f"demote", "Downgrade admin as a member."],
        [
            f"mute <reply/username/userid>",
            "Mute members from the Group.",
        ],
        [
            f"unmute <reply/username/userid>",
            "Unmutes a member of the Group.",
        ],
        [
            f"pin <reply>",
            "To pin a message in a group.",
        ],
        [
            f"unpin <reply>",
            "To unpin messages in a group.",
        ],
        [
            f"setgpic <reply to photo>",
            "To change the group profile photo",
        ],
    ],
)
