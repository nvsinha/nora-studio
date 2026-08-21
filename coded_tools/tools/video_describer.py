# Copyright (c) 2026 Nishant Sinha
#
# Licensed under the MIT License. See LICENSE.txt in the project
# root for full license information.
#
# END COPYRIGHT

import base64
import logging
from typing import Any

# pylint: disable=import-error
import cv2
from langchain_core.messages import HumanMessage
from langchain_openai import ChatOpenAI
from nora_fleet.interfaces.coded_tool import CodedTool

INSTRUCTIONS = "Describe the content of the video in detail."


class VideoDescriber(CodedTool):
    """
    A CodedTool implementation for invoking OpenAI model to describe a generated video.
    """

    def __init__(self):
        self.logger = logging.getLogger(__name__)

    async def async_invoke(self, args: dict[str, Any], sly_data: dict[str, Any]) -> str:
        """
        :param args: An argument dictionary whose keys are the parameters
                to the coded tool and whose values are the values passed for them
                by the calling agent or user. This dictionary is to be treated as read-only.

                The argument dictionary expects the following keys:
                - from calling agent
                    - "file_path" (str): Path to the video file to be described.
                - from user
                    - "openai_model" (str): OpenAI model to call the tool. Default to gpt-4o.

        :param sly_data: A dictionary whose keys are defined by the agent hierarchy,
                but whose values are meant to be kept out of the chat stream.

        :return: Text string describing the video.
        """

        # Get file_path from args
        file_path: str = args.get("file_path")
        if not file_path:
            raise ValueError("No file_path provided!!!")

        # User-defined arguments
        openai_model: str = args.get("openai_model", "gpt-4o")

        # Read video and extract frames
        video = cv2.VideoCapture(file_path)
        base64_frames: list[str] = []
        while video.isOpened():
            success, frame = video.read()
            if not success:
                break
            _, buffer = cv2.imencode(".jpg", frame)
            base64_frames.append(base64.b64encode(buffer).decode("utf-8"))

        video.release()
        self.logger.info("%d frames read from %s.", len(base64_frames), file_path)

        llm = ChatOpenAI(model=openai_model)
        content = [
            {
                "type": "text",
                "text": f"{INSTRUCTIONS}",
            },
            *[
                {
                    "type": "image",
                    "base64": f"{frame}",
                    "mime_type": "image/jpeg",
                }
                for frame in base64_frames
            ],
        ]

        message = HumanMessage(content=content)
        response = await llm.ainvoke([message])
        return response.text
