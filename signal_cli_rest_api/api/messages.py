import json
import os
from typing import Any, List
from shlex import quote

from fastapi import APIRouter, BackgroundTasks

from signal_cli_rest_api.config import settings
from signal_cli_rest_api.schemas import (
    MessageIncoming,
    MessageOutgoing,
    MessageOutgoingGrafana,
    MessageSent,
    MessageSentGrafana,
    ReactionOut,
)
from signal_cli_rest_api.utils import run_signal_cli_command, save_attachment

router = APIRouter()


@router.get("/{number}", response_model=List[MessageIncoming])
async def get_messages(number: str) -> Any:
    """
    get messages
    """
    
    response = await run_signal_cli_command(["-u", quote(number), "--output=json", "receive"])

    return [json.loads(m) for m in response.split("\n") if m != ""]


@router.post("/{number}", response_model=MessageSent, status_code=201)
async def send_message(
    message: MessageOutgoing, number: str, background_tasks: BackgroundTasks
) -> Any:
    """
    send message
    """

    cmd = ["-u", quote(number), "send", "-m", quote(message.text)]

    if message.group:
        cmd.append("-g")
        cmd.append(quote(message.groupId))
    else:
        cmd += list(map(quote, message.receivers))

    if len(message.attachments) > 0:
        cmd.append("-a")
        for attachment in message.attachments:
            await save_attachment(attachment)
            attachment_path = f"{settings.signal_upload_path}{attachment.filename}"
            cmd.append(attachment_path)
            background_tasks.add_task(os.remove, attachment_path)

    response = await run_signal_cli_command(cmd)

    return MessageSent(**message.dict(), timestamp=response.split("\n")[0])

@router.post("{number}/grafana/", response_model=MessageSentGrafana, status_code=201)
async def send_message(
    message: MessageOutgoingGrafana, number: str, background_tasks: BackgroundTasks,
    receiver: str, group: bool = True,
) -> Any:
    """
    send message
    """

    metrics = ""
    if message.evalMatches is not None:
        for match in message.evalMatches:
            metrics += "\n" + quote(match.metric) + ": " + quote(match.value) 

    message = quote(message.title) + "\n" + "State: " +  quote(message.ruleName) + "\n" + "Message: " + quote(message.message) + "\n" + "URL: " + quote(message.ruleUrl) + "\n\n" + "Metrics: " + metrics

    cmd = ["-u", quote(number), "send", "-m", message]

    if group:
        cmd.append("-g")
        cmd.append(quote(receiver))
    else:
        cmd += quote(receiver)

    response = await run_signal_cli_command(cmd)

    return MessageSentGrafana(**message.dict(), timestamp=response.split("\n")[0])


@router.post("/{number}/reaction")
async def send_reaction(number: str, reaction: ReactionOut) -> Any:
    """
    send a reaction

    https://emojipedia.org/
    """
    cmd = ["-u", quote(number), "sendReaction"]

    if reaction.group:
        cmd += ["-g", quote(reaction.receiver)]
    else:
        cmd.append(quote(reaction.receiver))

    cmd += [
        "-a",
        quote(reaction.target_number),
        "-t",
        quote(reaction.target_timestamp),
        "-e",
        quote(reaction.emoji),
    ]

    await run_signal_cli_command(cmd)


@router.delete("/{number}/reaction")
async def delete_reaction(number: str, reaction: ReactionOut) -> Any:
    """
    remove a reaction
    """
    cmd = ["-u", quote(number), "sendReaction"]

    if reaction.group:
        cmd += ["-g", quote(reaction.receiver)]
    else:
        cmd.append(quote(reaction.receiver))

    cmd += [
        "-a",
        quote(reaction.target_number),
        "-t",
        quote(reaction.target_timestamp),
        "-e",
        quote(reaction.emoji),
        "-r",
    ]

    await run_signal_cli_command(cmd)
