# Copyright (C) 2019 The Raphielscape Company LLC.
#
# Licensed under the Raphielscape Public License, Version 1.b (the "License");
# you may not use this file except in compliance with the License.
#

""" Userbot module for keeping control who PM you. """

from telethon.tl.functions.contacts import BlockRequest, UnblockRequest
from telethon.tl.functions.messages import ReportSpamRequest
from telethon.tl.functions.users import GetFullUserRequest
from sqlalchemy.exc import IntegrityError

from userbot import (COUNT_PM, CMD_HELP, BOTLOG, BOTLOG_CHATID,
                     PM_AUTO_BAN, LASTMSG, LOGS)
from userbot.events import register

# ========================= CONSTANTS ============================
UNAPPROVED_MSG = ("`Hello This is an automated reply`\n\n"
                  "`The user you are trying to message is no more availabe for DM but still drop him a message `@techgurujiibot`,if he finds you important he will surely reply you\n`"
                  "`Instead, go to Google find solutions.`\n\n"
                  "`Trust me you will discover more than what you think...\n`"
                  "`And yeah don't send more than 5 messages or else your profile will be reported and blocked. 🙂\n`"
                  "`KBye😊,`\n"
                  "`TECHGURUJII :)`")
# =================================================================


@register(incoming=True, disable_edited=True)
async def permitpm(event):
    """ Permits people from PMing you without approval. \
        Will block retarded nibbas automatically. """
    if PM_AUTO_BAN:
        if event.is_private and not (await event.get_sender()).bot:
            try:
                from userbot.modules.sql_helper.pm_permit_sql import is_approved
                from userbot.modules.sql_helper.globals import gvarstatus
            except AttributeError:
                return
            apprv = is_approved(event.chat_id)
            notifsoff = gvarstatus("NOTIF_OFF")

            # This part basically is a sanity check
            # If the message that sent before is Unapproved Message
            # then stop sending it again to prevent FloodHit
            if not apprv and event.text != UNAPPROVED_MSG:
                if event.chat_id in LASTMSG:
                    prevmsg = LASTMSG[event.chat_id]
                    # If the message doesn't same as previous one
                    # Send the Unapproved Message again
                    if event.text != prevmsg:
                        await event.reply(UNAPPROVED_MSG)
                    LASTMSG.update({event.chat_id: event.text})
                else:
                    await event.reply(UNAPPROVED_MSG)
                    LASTMSG.update({event.chat_id: event.text})

                if notifsoff:
                    await event.client.send_read_acknowledge(event.chat_id)
                if event.chat_id not in COUNT_PM:
                    COUNT_PM.update({event.chat_id: 1})
                else:
                    COUNT_PM[event.chat_id] = COUNT_PM[event.chat_id] + 1

                if COUNT_PM[event.chat_id] > 4:
                    await event.respond(
                        "`You were spamming my peru master's TECHGURUJI PM, which I don't like.`"
                        " `I'mma Report Spam, now Get the Fuck Out.`"
                    )

                    try:
                        del COUNT_PM[event.chat_id]
                        del LASTMSG[event.chat_id]
                    except KeyError:
                        if BOTLOG:
                            await event.client.send_message(
                                BOTLOG_CHATID,
                                "Count PM is seemingly going retard, plis restart bot!",
                            )
                        LOGS.info("CountPM wen't rarted boi")
                        return

                    await event.client(BlockRequest(event.chat_id))
                    await event.client(ReportSpamRequest(peer=event.chat_id))

                    if BOTLOG:
                        name = await event.client.get_entity(event.chat_id)
                        name0 = str(name.first_name)
                        await event.client.send_message(
                            BOTLOG_CHATID,
                            "["
                            + name0
                            + "](tg://user?id="
                            + str(event.chat_id)
                            + ")"
                            + " was just another retarded nibba",
                        )


@register(outgoing=True, pattern="^.notifoff$")
async def notifoff(noff_event):
    """ For .notifoff command, stop getting notifications from unapproved PMs. """
    if not noff_event.text[0].isalpha() and noff_event.text[0] not in ("/", "#", "@", "!"):
        try:
            from userbot.modules.sql_helper.globals import addgvar
        except AttributeError:
            return
        addgvar("NOTIF_OFF", True)
        await noff_event.edit("`Notifications silenced!`")


@register(outgoing=True, pattern="^.notifon$")
async def notifon(non_event):
    """ For .notifoff command, get notifications from unapproved PMs. """
    if not non_event.text[0].isalpha() and non_event.text[0] not in ("/", "#", "@", "!"):
        try:
            from userbot.modules.sql_helper.globals import delgvar
        except AttributeError:
            return
        delgvar("NOTIF_OFF")
        await non_event.edit("`Notifications unmuted!`")


@register(outgoing=True, pattern="^.pm$")
async def approvepm(apprvpm):
    """ For .pm command, give someone the permissions to PM you. """
    if not apprvpm.text[0].isalpha() and apprvpm.text[0] not in ("/", "#", "@", "!"):
        try:
            from userbot.modules.sql_helper.pm_permit_sql import approve
        except AttributeError:
            await apprvpm.edit("`Running on Non-SQL mode!`")
            return

        if apprvpm.reply_to_msg_id:
            reply = await apprvpm.get_reply_message()
            replied_user = await apprvpm.client(GetFullUserRequest(reply.from_id))
            aname = replied_user.user.id
            name0 = str(replied_user.user.first_name)
            uid = replied_user.user.id

        else:
            aname = await apprvpm.client.get_entity(apprvpm.chat_id)
            name0 = str(aname.first_name)
            uid = apprvpm.chat_id

        try:
            approve(uid)
        except IntegrityError:
            await apprvpm.edit("`This bsdka may already be approved.`")
            return

        await apprvpm.edit(
            f"[{name0}](tg://user?id={uid}) `retarted nibba approved to PM, KEK!`"
        )

        if BOTLOG:
            await apprvpm.client.send_message(
                BOTLOG_CHATID,
                "#APPROVED\n"
                + "User: " + f"[{name0}](tg://user?id={uid})",
            )


@register(outgoing=True, pattern="^.block$")
async def blockpm(block):
    """ For .block command, block people from PMing you! """
    if not block.text[0].isalpha() and block.text[0] not in ("/", "#", "@", "!"):

        await block.edit("`This chuu nubfuk has been blocked for PM-ing you Sar!`")

        if block.reply_to_msg_id:
            reply = await block.get_reply_message()
            replied_user = await block.client(GetFullUserRequest(reply.from_id))
            aname = replied_user.user.id
            name0 = str(replied_user.user.first_name)
            await block.client(BlockRequest(replied_user.user.id))
            uid = replied_user.user.id
        else:
            await block.client(BlockRequest(block.chat_id))
            aname = await block.client.get_entity(block.chat_id)
            name0 = str(aname.first_name)
            uid = block.chat_id

        try:
            from userbot.modules.sql_helper.pm_permit_sql import dissprove
            dissprove(uid)
        except AttributeError:  # Non-SQL mode.
            pass

        if BOTLOG:
            await block.client.send_message(
                BOTLOG_CHATID,
                "#BLOCKED\n"
                + "User: " + f"[{name0}](tg://user?id={uid})",
            )


@register(outgoing=True, pattern="^.unblock$")
async def unblockpm(unblock):
    """ For .unblock command, let people PMing you again! """
    if not unblock.text[0].isalpha() and unblock.text[0] \
            not in ("/", "#", "@", "!") and unblock.reply_to_msg_id:

        await unblock.edit("`Aye bc,my Master has forgiven you to PM now`")

        if unblock.reply_to_msg_id:
            reply = await unblock.get_reply_message()
            replied_user = await unblock.client(GetFullUserRequest(reply.from_id))
            name0 = str(replied_user.user.first_name)
            await unblock.client(UnblockRequest(replied_user.user.id))

        if BOTLOG:
            await unblock.client.send_message(
                BOTLOG_CHATID,
                f"[{name0}](tg://user?id={replied_user.user.id})"
                " was unblocc'd!.",
            )

CMD_HELP.update({
    "pmpermit": "\
.pm\
\nUsage: Approves the mentioned/replied person to PM.\
\n\n.block\
\nUsage: Blocks the person from PMing you.\
\n\n.unblock\
\nUsage: Unblocks the person so they can PM you.\
\n\n.notifoff\
\nUsage: Clears any notifications of unapproved PMs.\
\n\n.notifon\
\nUsage: Allows notifications for unapproved PMs.\
"
})
