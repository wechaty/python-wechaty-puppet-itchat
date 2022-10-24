"""
Python Wechaty - https://github.com/wechaty/python-wechaty

Authors:    Huan LI (李卓桓) <https://github.com/huan>
            Jingjing WU (吴京京) <https://github.com/wj-Mcat>

2020-now @ Copyright Wechaty

Licensed under the Apache License, Version 2.0 (the 'License');
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an 'AS IS' BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""
from __future__ import annotations

import asyncio
from distutils import core
from email import message
import types
from typing import Optional, List, Dict

from grpclib.client import Channel

from pyee import AsyncIOEventEmitter  # type: ignore

from wechaty_puppet.schemas.types import PayloadType  # type: ignore

from wechaty_puppet import (  # type: ignore
    EventScanPayload,
    ScanStatus,
    
    # EventReadyPayload,
    #
    # EventDongPayload,
    # EventRoomTopicPayload,
    # EventRoomLeavePayload,
    # EventRoomJoinPayload,
    # EventRoomInvitePayload,

    EventMessagePayload,
    EventLogoutPayload,
    EventLoginPayload,
    # EventFriendshipPayload,
    # EventHeartbeatPayload,
    # EventErrorPayload,
    FileBox, RoomMemberPayload, RoomPayload, RoomInvitationPayload,
    RoomQueryFilter, FriendshipPayload, ContactPayload, MessagePayload,
    MessageQueryFilter,

    ImageType,
    # EventType,
    MessageType,
    Puppet,
    PuppetOptions,
    MiniProgramPayload,
    UrlLinkPayload,
    watch_dog,
    get_logger
)

from wechaty_puppet.exceptions import (  # type: ignore
    # WechatyPuppetConfigurationError,
    # WechatyPuppetError,
    WechatyPuppetGrpcError,
    WechatyPuppetOperationError,
    # WechatyPuppetPayloadError
)
import sys
import os
if os.name == 'nt':
    sys.path.insert(0,f'{os.path.abspath(os.path.dirname(os.path.dirname(__file__)))}/wechaty_puppet_itchat')
    
sys.path.insert(0,f'{os.path.abspath(os.path.dirname(os.path.dirname(__file__)))}/wechaty_puppet_itchat')
    
from itchat  import load_async_itchat
from itchat.async_components import (
    TEXT,
    MAP,
    CARD,
    NOTE,
    SHARING,
    PICTURE,
    RECORDING,
    VOICE,
    ATTACHMENT,
    VIDEO,
    FRIENDS
)
# pylint: disable=E0401

log = get_logger('ItChatPuppet')
log.disabled=True

def _map_message_type(message_payload: MessagePayload) -> MessagePayload:
    """
    get messageType value which is ts-wechaty-puppet type from service server,
        but is MessageType. so we should map it to MessageType from wechaty-grpc
    target MessageType Enum:
        MESSAGE_TYPE_UNSPECIFIED  = 0;

       MESSAGE_TYPE_ATTACHMENT   = 1;
       MESSAGE_TYPE_AUDIO        = 2;
       MESSAGE_TYPE_CONTACT      = 3;
       MESSAGE_TYPE_EMOTICON     = 4;
       MESSAGE_TYPE_IMAGE        = 5;
       MESSAGE_TYPE_TEXT         = 6;
       MESSAGE_TYPE_VIDEO        = 7;
       MESSAGE_TYPE_CHAT_HISTORY = 8;
       MESSAGE_TYPE_LOCATION     = 9;
       MESSAGE_TYPE_MINI_PROGRAM = 10;
       MESSAGE_TYPE_TRANSFER     = 11;
       MESSAGE_TYPE_RED_ENVELOPE = 12;
       MESSAGE_TYPE_RECALLED     = 13;
       MESSAGE_TYPE_URL          = 14;

    source MessageType Enum:
        export enum MessageType {
          Unknown = 0,

          Attachment=1,     // Attach(6),
          Audio=2,          // Audio(1), Voice(34)
          Contact=3,        // ShareCard(42)
          ChatHistory=4,    // ChatHistory(19)
          Emoticon=5,       // Sticker: Emoticon(15), Emoticon(47)
          Image=6,          // Img(2), Image(3)
          Text=7,           // Text(1)
          Location=8,       // Location(48)
          MiniProgram=9,    // MiniProgram(33)
          GroupNote=10,      // GroupNote(53)
          Transfer=11,       // Transfers(2000)
          RedEnvelope=12,    // RedEnvelopes(2001)
          Recalled=13,       // Recalled(10002)
          Url=14,            // Url(5)
          Video=15,          // Video(4), Video(43)
        }
    :return:

    #
    """
    if isinstance(message_payload.type, int):
        map_container: List[MessageType] = [
            MessageType.MESSAGE_TYPE_UNSPECIFIED,
            MessageType.MESSAGE_TYPE_ATTACHMENT,
            MessageType.MESSAGE_TYPE_AUDIO,
            MessageType.MESSAGE_TYPE_CONTACT,
            MessageType.MESSAGE_TYPE_CHAT_HISTORY,
            MessageType.MESSAGE_TYPE_EMOTICON,
            MessageType.MESSAGE_TYPE_IMAGE,
            MessageType.MESSAGE_TYPE_TEXT,
            MessageType.MESSAGE_TYPE_LOCATION,
            MessageType.MESSAGE_TYPE_MINI_PROGRAM,
            MessageType.MESSAGE_TYPE_UNSPECIFIED,
            MessageType.MESSAGE_TYPE_TRANSFER,
            MessageType.MESSAGE_TYPE_RED_ENVELOPE,
            MessageType.MESSAGE_TYPE_RECALLED,
            MessageType.MESSAGE_TYPE_URL,
            MessageType.MESSAGE_TYPE_VIDEO]
        message_payload.type = map_container[message_payload.type]
    return message_payload



# pylint: disable=R0904
class PuppetItChat(Puppet):
    """
    grpc wechaty puppet implementation
    """

    def __init__(self, options: PuppetOptions, name: str = 'puppet_itchat'):
        """init PuppetItChat from options or envrionment

        Args:
            options (PuppetOptions): the configuration of PuppetItChat
            name (str, optional): [description]. Defaults to 'puppet_itchat'.

        Raises:
            WechatyPuppetConfigurationError: raise Error when configuraiton occur error
        """
        super().__init__(options, name)

        self.channel: Optional[Channel] = None
        self._event_stream: AsyncIOEventEmitter = AsyncIOEventEmitter()
        self.login_user_id: Optional[str] = None
        self.puppet_options = None
        self.puppet = self
        self.itchat = load_async_itchat()
        

        self.message_container: Dict[str, dict] = {}

    async def room_list(self) -> List[str]:
        """
        get all room list
        :return:
        """
        # response = await self.puppet_stub.room_list()
        # if response is None:
        #     raise WechatyPuppetGrpcError('can"t get room_list response')
        # return response.ids
        return [i['UserName'] for i in  self.itchat.get_chatrooms()]

    async def message_image(self, message_id: str, image_type: ImageType = 3
                            ) -> FileBox:
        """
        get message image data
        :param message_id:
        :param image_type:
        :return:
        """
        # file_chunk_data: List[bytes] = []
        # name: str = ''
        #
        # async for stream in self.puppet_stub.message_image_stream(id=message_id, type=image_type):
        #     file_chunk_data.append(stream.file_box_chunk.data)
        #     if not name and stream.file_box_chunk.name:
        #         name = stream.file_box_chunk.name
        #
        # file_stream = reduce(lambda pre, cu: pre + cu, file_chunk_data)
        # file_box = FileBox.from_stream(file_stream, name=name)
        # return file_box
        if message_id not in self.message_container:
            raise ValueError('img message not found')
        msg = self.message_container[message_id]
        get_pic = await msg['Text']
        await get_pic(msg['fileName'])
        file_box = FileBox.from_file(path=msg['fileName'], name=msg['fileName'])
        return file_box

    def on(self, event_name: str, caller):
        """
        listen event from the wechaty
        :param event_name:
        :param caller:
        :return:
        """
        # TODO -> if the event is listened twice, how to handle this problem
        self._event_stream.on(event_name, caller)

    def listener_count(self, event_name: str) -> int:
        """
        how to get event count
        :param event_name:
        :return:
        """
        listeners = self._event_stream.listeners(event_name)
        return len(listeners)

    async def contact_list(self) -> List[str]:
        """
        get contact list
        :return:
        """
        return [i['UserName'] for i in self.itchat.get_friends(update=True)]

    async def tag_contact_delete(self, tag_id: str) -> None:
        """
        delete some tag
        :param tag_id:
        :return:
        """
        # await self.puppet_stub.tag_contact_delete(id=tag_id)
        # return None

    async def tag_favorite_delete(self, tag_id: str) -> None:
        """
        delete tag favorite
        :param tag_id:
        :return:
        """
        # wechaty_grpc has not implement this function
        # return None

    async def tag_contact_add(self, tag_id: str, contact_id: str):
        """
        add a tag to contact
        :param tag_id:
        :param contact_id:
        :return:
        """
        # await self.puppet_stub.tag_contact_add(
        #     id=tag_id, contact_id=contact_id)

    async def tag_favorite_add(self, tag_id: str, contact_id: str):
        """
        add a tag to favorite
        :param tag_id:
        :param contact_id:
        :return:
        """
        # wechaty_grpc has not implement this function

    async def tag_contact_remove(self, tag_id: str, contact_id: str):
        """
        remove a tag from contact
        :param tag_id:
        :param contact_id:
        :return:
        """
        # await self.puppet_stub.tag_contact_remove(
        #     id=tag_id,
        #     contact_id=contact_id)

    async def tag_contact_list(self, contact_id: Optional[str] = None
                               ) -> List[str]:
        """
        get tag list from a contact
        :param contact_id:
        :return:
        """
        # response = await self.puppet_stub.tag_contact_list(
        #     contact_id=contact_id)
        # return response.ids
        return []

    async def message_send_text(self, conversation_id: str, message: str,
                                mention_ids: Optional[List[str]] = None) -> str:
        """
        send text message
        :param conversation_id:
        :param message:
        :param mention_ids:
        :return:
        """
        # TODO: it seems that itchat can't send mentonal message.
        # response = await self.puppet_stub.message_send_text(
        #     conversation_id=conversation_id,
        #     text=message, mentonal_ids=mention_ids)
        response = await self.itchat.send_msg(msg = message, toUserName=conversation_id)
        msg=dict()
        msg['MsgId'] = response['MsgID']
        msg['FromUserName'] = ''
        msg['ToUserName'] = ''
        msg['Type'] = 'Text'
        msg['Text'] = message
        msg['FileName'] = ''
        msg['CreateTime']= ''
        self.message_container[response['MsgID']] = msg
        return response['MsgID']

    async def message_send_contact(self, contact_id: str,
                                   conversation_id: str) -> str:
        """
        send contact message
        :param contact_id:
        :param conversation_id:
        :return:
        """
        # TODO: it seems that itchat can't send contact message.
        # response = await self.puppet_stub.message_send_contact(
        #     conversation_id=conversation_id,
        #     contact_id=contact_id
        # )
        # return response.id
        return ''

    async def message_send_file(self, conversation_id: str,
                                file: FileBox) -> str:
        """
        send file message
        :param conversation_id:
        :param file:
        :return:
        """
        file_path = file.name
        if file.name.endswith('.jpg') or \
                file.name.endswith('.jpeg') or \
                file.name.endswith('.png') or \
                file.name.endswith('.gif') or \
                file.name.endswith('.bmp'):
            await file.to_file(file_path=file_path, overwrite=True)
            response = await self.itchat.send_image(fileDir=file_path, toUserName=conversation_id)
        elif file.name.endswith(('.mp4','.MP4'))  :
            await file.to_file(file_path=file_path, overwrite=True)
            response = await self.itchat.send_video(fileDir=file_path, toUserName=conversation_id)
            msg=dict()
            msg['MsgId'] = response['MsgID']
            msg['FromUserName'] = ''
            msg['ToUserName'] = ''
            msg['Type'] = 'Video'
            msg['Text'] = ''
            msg['FileName'] = file_path
            msg['CreateTime']= ''
            self.message_container[response['MsgID']] = msg
            return response['MsgID']
        else:
            file_path = file.name
            await file.to_file(overwrite=True)
            response = await self.itchat.send_file(fileDir=file_path, toUserName=conversation_id)
        msg=dict()
        print(response)
        msg['MsgId'] = response['MsgID']
        msg['FromUserName'] = ''
        msg['ToUserName'] = ''
        msg['Type'] = 'Attachment'
        msg['Text'] = ''
        msg['FileName'] = file_path
        msg['CreateTime']= ''
        self.message_container[response['MsgID']] = msg
        return response['MsgID']

    async def message_send_url(self, conversation_id: str, url: str) -> str:
        """
        send url message
        :param conversation_id:
        :param url:
        :return:
        """
        # TODO: it seems that itchat can't send url message.
        # response = await self.puppet_stub.message_send_url(
        #     conversation_id=conversation_id,
        #     url_link=url
        # )
        # return response.id
        return ''

    async def message_send_mini_program(self, conversation_id: str,
                                        mini_program: MiniProgramPayload
                                        ) -> str:
        """
        send mini_program message
        :param conversation_id:
        :param mini_program:
        :return:
        """
        # TODO: it seems that itchat can't send mini program message.
        # response = await self.puppet_stub.message_send_mini_program(
        #     conversation_id=conversation_id,
        #     # TODO -> check mini_program key
        #     mini_program=json.dumps(asdict(mini_program))
        # )
        # return response.id
        return ''

    async def message_search(self, query: Optional[MessageQueryFilter] = None
                             ) -> List[str]:
        """
        # TODO -> this function should not be here ?
        :param query:
        :return:
        """
        return []

    async def message_recall(self, message_id: str) -> bool:
        """
        recall the message
        :param message_id:
        :return:
        """
        # response = await self.puppet_stub.message_recall(id=message_id)
        # return response.success

    async def message_payload(self, message_id: str) -> MessagePayload:
        """
        get message payload
        :param message_id:
        :return:
        """
        if message_id not in self.message_container:
            raise ValueError('message not found')
        msg = self.message_container[message_id]
        msg_type = msg['Type']
        if msg_type == 'Text':
            type_ = MessageType.MESSAGE_TYPE_TEXT
        elif msg_type == 'Map':
            type_ = MessageType.MESSAGE_TYPE_LOCATION
        elif msg_type == 'Sharing':
            type_ = MessageType.MESSAGE_TYPE_URL
        elif msg_type == 'Picture':
            type_ = MessageType.MESSAGE_TYPE_IMAGE
        elif msg_type == 'Video':
            type_ = MessageType.MESSAGE_TYPE_VIDEO
        elif msg_type == 'Card':
            type_ = MessageType.MESSAGE_TYPE_CONTACT
        elif msg_type in ['Recording', 'Attachment']:
            type_ = MessageType.MESSAGE_TYPE_ATTACHMENT
        else:
            type_ = MessageType.MESSAGE_TYPE_UNSPECIFIED

        if '@@' in msg['FromUserName']:
            message_payload = MessagePayload(id=msg['MsgId'],
                                             type=type_,
                                             from_id=msg['ToUserName'],
                                             room_id=msg['FromUserName'],
                                             filename=msg['FileName'],
                                             text=msg['Text'],
                                             timestamp=msg['CreateTime'],
                                             to_id=msg['ToUserName'])
        else:
            message_payload = MessagePayload(id=msg['MsgId'],
                                             type=type_,
                                             from_id=msg['FromUserName'],
                                             filename=msg['FileName'],
                                             text=msg['Text'],
                                             timestamp=msg['CreateTime'],
                                             to_id=msg['ToUserName'])
        return message_payload

    async def message_forward(self, to_id: str, message_id: str):
        """
        forward the message
        :param to_id:
        :param message_id:
        :return:
        """
        payload = await self.message_payload(message_id=message_id)
        if payload.type == MessageType.MESSAGE_TYPE_TEXT:
            if not payload.text:
                raise Exception('no text')
            await self.message_send_text(conversation_id=to_id, message=payload.text)
        elif payload.type == MessageType.MESSAGE_TYPE_URL:
            url_payload = await self.message_url(message_id=message_id)
            await self.message_send_url(conversation_id=to_id, url=url_payload.url)
        elif payload.type == MessageType.MESSAGE_TYPE_MINI_PROGRAM:
            mini_program = await self.message_mini_program(message_id=message_id)
            await self.message_send_mini_program(conversation_id=to_id, mini_program=mini_program)
        elif payload.type == MessageType.MESSAGE_TYPE_EMOTICON:
            file_box = await self.message_emoticon(message=payload.text)
            await self.message_send_file(conversation_id=to_id, file=file_box)
        elif payload.type == MessageType.MESSAGE_TYPE_AUDIO:
            raise WechatyPuppetOperationError('Can not support audio message forward')
        # elif payload.type == MessageType.ChatHistory:
        elif payload.type == MessageType.MESSAGE_TYPE_IMAGE:
            file_box = await self.message_image(message_id=message_id, image_type=3)
            await self.message_send_file(conversation_id=to_id, file=file_box)
        else:
            file_box = await self.message_file(message_id=message_id)
            await self.message_send_file(conversation_id=to_id, file=file_box)

    async def message_file(self, message_id: str) -> FileBox:
        """
        extract file from message
        :param message_id:
        :return:
        """
        # file_chunk_data: List[bytes] = []
        # name: str = ''
        #
        # async for stream in self.puppet_stub.message_file_stream(id=message_id):
        #     file_chunk_data.append(stream.file_box_chunk.data)
        #     if not name and stream.file_box_chunk.name:
        #         name = stream.file_box_chunk.name

        if message_id not in self.message_container:
            raise ValueError('file message not found')
        msg = self.message_container[message_id]
        get_pic = await msg['Text']
        await get_pic(msg['fileName'])
        file_box = FileBox.from_file(path=msg['fileName'], name=msg['fileName'])
        return file_box

    async def message_emoticon(self, message: str) -> FileBox:
        """
        emoticon from message
        :param message:
        :return:
        """
        if message not in self.message_container:
            raise ValueError('emoticon message not found')
        msg = self.message_container[message]
        get_pic = await msg['Text']
        await get_pic(msg['fileName'])
        file_box = FileBox.from_file(path=msg['fileName'], name=msg['fileName'])
        return file_box

    async def message_contact(self, message_id: str) -> str:
        """
        extract
        :param message_id:
        :return:
        """
        
        # response = await self.puppet.message_contact(id=message_id)
        # return response.id
        if message_id not in self.message_container:
            raise ValueError('contact message not found')
        msg = self.message_container[message_id]
        return msg['RecommendInfo']['UserName']

    async def message_url(self, message_id: str) -> UrlLinkPayload:
        """
        extract url_link payload data from response
        :param message_id:
        :return:
        """
        if message_id not in self.message_container:
            raise ValueError('url message not found')
        msg = self.message_container[message_id]
        return UrlLinkPayload(
            url=msg['Url'],
            title=msg['FileName'],
            description='',
            thumbnailUrl='',
        )

    async def message_mini_program(self, message_id: str) -> MiniProgramPayload:
        """
        extract mini_program from message
        :param message_id:
        :return:
        """
        # TODO -> need to MiniProgram
        # TODO: it seems that itchat can't send mini program message.
        # if self.puppet_stub is None:
        #     raise Exception('puppet_stub should not be none')
        #
        # response = await self.puppet_stub.message_mini_program(id=message_id)
        # response_dict = json.loads(response.mini_program)
        # try:
        #     mini_program = MiniProgramPayload(**response_dict)
        # except Exception as e:
        #     raise WechatyPuppetPayloadError(f'can"t init mini-program payload {response_dict}') \
        #         from e
        # return mini_program
        return MiniProgramPayload()

    async def contact_alias(self, contact_id: str, alias: Optional[str] = None
                            ) -> str:
        """
        get/set contact alias
        :param contact_id:
        :param alias:
        :return:
        """
        # response = await self.puppet_stub.contact_alias(
        #     id=contact_id, alias=alias)
        # if response.alias is None and alias is None:
        #     raise WechatyPuppetGrpcError('can"t get contact<%s> alias' % contact_id)
        # return response.alias
        contact = await self.contact_payload(contact_id=contact_id)
        if contact.alias is None and alias is None:
            raise WechatyPuppetGrpcError(f'can"t get contact<{contact_id}> alias')
        if alias != contact.alias and alias is None:
            self.itchat.set_alias(userName=contact_id, alias=alias)
        return contact.alias if alias is None else alias

    async def contact_payload_dirty(self, contact_id: str):
        """
        mark the contact payload dirty status, and remove it from the cache
        """
        await self.dirty_payload(PayloadType.PAYLOAD_TYPE_CONTACT, contact_id)

    async def contact_payload(self, contact_id: str) -> ContactPayload:
        """
        get contact payload
        :param contact_id:
        :return:
        """
        # response = await self.puppet_stub.contact_payload(id=contact_id)
        # return response
        contact_list = self.itchat.get_friends(update=True)
        for c in contact_list:
            if c.get('UserName') == contact_id:
                return ContactPayload(
                    id=c['UserName'],
                    gender=c['Sex'],
                    name=c['NickName'],
                    avatar=c['HeadImgUrl'],
                    alias=c['Alias'],
                    city=c['City'],
                    province=c['Province'],
                    signature=c['Signature'],
                    star=c['StarFriend'],
                    description=c['RemarkName'])

    async def contact_avatar(self, contact_id: str,
                             file_box: Optional[FileBox] = None) -> FileBox:
        """
        get/set contact avatar
        :param contact_id:
        :param file_box:
        :return:
        """
        # response = await self.puppet_stub.contact_avatar(
        #     id=contact_id, filebox=file_box)
        # return FileBox.from_json(response.filebox)
        self.itchat.get_head_img(userName=contact_id, picDir=contact_id + '.jpg')
        return FileBox.from_file(path=contact_id + '.jpg')

    async def contact_tag_ids(self, contact_id: str) -> List[str]:
        """
        get contact tags
        :param contact_id:
        :return:
        """
        # TODO: it seems that itchat can't contact_tag_ids.
        # response = await self.puppet_stub.tag_contact_list(
        #     contact_id=contact_id)
        # return response.ids
        return []

    def self_id(self) -> str:
        """
        # TODO -> how to get self_id, nwo wechaty has save login_user
            contact_id
        :return:
        """
        if not self.login_user_id:
            raise WechatyPuppetOperationError('can"t call self_id() before logined')
        return self.login_user_id

    async def friendship_search(self, weixin: Optional[str] = None,
                                phone: Optional[str] = None) -> Optional[str]:
        """
        search friendship by wexin/phone
        :param weixin:
        :param phone:
        :return:
        """
        # TODO: itchat can't get contact's phone number, so phone search can't be used.
        if weixin is not None:
            weixin_response = await self.contact_payload(contact_id=weixin)
            if weixin_response is not None:
                return weixin_response.id
        return None

    async def friendship_add(self, contact_id: str, hello: str):
        """
        try to add friendship
        :param contact_id:
        :param hello:
        :return:
        """
        # await self.puppet_stub.friendship_add(
        #     contact_id=contact_id,
        #     hello=hello
        # )
        await self.itchat.Core.add_friend(self.itchat.Core(), userName=contact_id,
                                          status=2, verifyContent=hello)

    async def friendship_payload(self, friendship_id: str,
                                 payload: Optional[FriendshipPayload] = None
                                 ) -> FriendshipPayload:
        """
        get/set friendship payload
        :param friendship_id:
        :param payload:
        :return:
        """
        # response = await self.puppet_stub.friendship_payload(
        #     id=friendship_id, payload=json.dumps(payload)
        # )
        if payload:
            payload.id = friendship_id
        return payload

    async def friendship_accept(self, friendship_id: str):
        """
        accept friendship
        :param friendship_id:
        :return:
        """
        await self.itchat.Core.add_friend(self.itchat.Core(), userName=friendship_id, status=3)

    async def room_create(self, contact_ids: Optional[List[str]], topic: Optional[str] = None
                          ) -> str:
        """
        create room
        :param contact_ids:
        :param topic:
        :return: created room_id
        """
        # response = await self.puppet_stub.room_create(
        #     contact_ids=contact_ids,
        #     topic=topic
        # )
        # return response.id
        return self.itchat.create_chatroom(memberList=contact_ids, topic=topic)['ChatRoomName']

    # async def room_search(self, query: RoomQueryFilter = None) -> List[str]:
    async def room_search(self) -> List[str]:
        """
        find the room_ids
        search room
        :param query:
        :return:
        """
        # room_list_response = await self.puppet_stub.room_list()
        # return room_list_response.ids
        return [i['UserName'] for i in self.itchat.get_chatrooms(update=True)]


    async def room_invitation_payload(self,
                                      room_invitation_id: str,
                                      payload: Optional[RoomInvitationPayload]
                                      = None) -> RoomInvitationPayload:
        """
        get room_invitation_payload
        """
        # response = await self.puppet_stub.room_invitation_payload(
        #     id=room_invitation_id,
        #     payload=payload
        # )
        # return RoomInvitationPayload(**response.to_dict())

    async def room_invitation_accept(self, room_invitation_id: str):
        """
        accept the room invitation
        :param room_invitation_id:
        :return:
        """
        # TODO: it seems that itchat can't room_invitation_accept.
        # await self.puppet_stub.room_invitation_accept(id=room_invitation_id)

    async def contact_self_qr_code(self) -> str:
        """
        :return:
        """

        # response = await self.puppet_stub.contact_self_qr_code()
        # return response.qrcode
        return ''

    async def contact_self_name(self, name: str):
        """
        set the name of the contact
        :param name:
        :return:
        """
        # await self.puppet_stub.contact_self_name(name=name)

    async def contact_signature(self, signature: str):
        """

        :param signature:
        :return:
        """

    async def room_validate(self, room_id: str) -> bool:
        """

        :param room_id:
        :return:
        """

    async def room_payload_dirty(self, room_id: str):
        """
        mark the room payload dirty status, and remove it from the cache
        :param room_id:
        :return:
        """
        await self.dirty_payload(
            PayloadType.PAYLOAD_TYPE_ROOM,
            room_id
        )

    async def room_member_payload_dirty(self, room_id: str):
        """
        mark the room-member payload dirty status, and remove it from the cache
        :param room_id:
        :return:
        """
        await self.dirty_payload(
            PayloadType.PAYLOAD_TYPE_ROOM_MEMBER,
            room_id
        )

    async def room_payload(self, room_id: str) -> RoomPayload:
        """

        :param room_id:
        :return:
        """
        # response = await self.puppet_stub.room_payload(id=room_id)
        # return response
        room_list = self.itchat.get_chatrooms(update=True)
        for r in room_list:
            print(r)
            if r['UserName'] == room_id:
                member_ids = [c['UserName'] for c in r['MemberList']]
                return RoomPayload(
                    id=r['UserName'],
                    topic=r['NickName'],
                    avatar=r['HeadImgUrl'],
                    owner_id=r.get('ChatRoomOwner'),
                    admin_ids= [r.get('ChatRoomOwner')],
                    member_ids=member_ids)

    async def room_members(self, room_id: str) -> List[str]:
        """

        :param room_id:
        :return:
        """
        # response = await self.puppet_stub.room_member_list(id=room_id)
        # return response.member_ids
        rooms_list = self.itchat.get_chatrooms()
        contact_list = []
        for r in rooms_list:
            if r['UserName'] == room_id:
                for c in r['MemberList']:
                    contact_list.append(c['UserName'])
        return contact_list

    async def room_add(self, room_id: str, contact_id: str):
        """
        add contact to room
        :param room_id:
        :param contact_id:
        :return:
        """
        # await self.puppet_stub.room_add(id=room_id, contact_id=contact_id)

    async def room_delete(self, room_id: str, contact_id: str):
        """
        delete contact from room
        :param room_id:
        :param contact_id:
        :return:
        """
        # await self.puppet_stub.room_del(id=room_id, contact_id=contact_id)

    async def room_quit(self, room_id: str):
        """
        quit from room
        :param room_id:
        :return:
        """
        # TODO: it seems that itchat can't room_quit.
        # await self.puppet_stub.room_quit(id=room_id)

    async def room_topic(self, room_id: str, new_topic: str):
        """
        set/set topic of the room
        :param room_id:
        :param new_topic:
        :return:
        """
        # await self.puppet_stub.room_topic(id=room_id, topic=new_topic)

    async def room_announce(self, room_id: str,
                            announcement: Optional[str] = None) -> str:
        """
        get/set announce
        :param room_id:
        :param announcement:
        :return:
        """
        # TODO: it seems that itchat can't send room_announce.
        # room_announce_response = await self.puppet_stub.room_announce(
        #     id=room_id, text=announcement)
        # if announcement is None and room_announce_response.text is not None:
        #     # get the announcement
        #     return room_announce_response.text
        # if announcement is not None and room_announce_response.text is None:
        #     return announcement
        return ''

    async def room_qr_code(self, room_id: str) -> str:
        """
        get room qr_code
        :param room_id:
        :return:
        """
        # # TODO -> wechaty-grpc packages has leave out id params
        # TODO: it seems that itchat can't room_qr_code.
        # log.warning('room_qr_code() <room_id: %s> param is missing', room_id)
        # room_qr_code_response = await \
        #     self.puppet_stub.room_qr_code()
        # return room_qr_code_response.qrcode
        return ''

    async def room_member_payload(self, room_id: str,
                                  contact_id: str) -> RoomMemberPayload:
        """
        get room member payload
        :param room_id:
        :param contact_id:
        :return:
        """
        # member_payload = await self.puppet_stub.room_member_payload(
        #     id=room_id, member_id=contact_id)
        # return member_payload

    async def room_avatar(self, room_id: str) -> FileBox:
        """
        get room avatar
        :param room_id:
        :return:
        """
        # room_avatar_response = await self.puppet_stub.room_avatar(id=room_id)
        #
        # file_box_data = json.loads(room_avatar_response.filebox)
        #
        # if 'remoteUrl' not in file_box_data:
        #     raise WechatyPuppetPayloadError('invalid room avatar response')
        #
        # file_box = FileBox.from_url(
        #     url=file_box_data['remoteUrl'],
        #     name=f'avatar-{room_id}.jpeg'
        # )
        # return file_box
        self.itchat.get_head_img(chatroomUserName=room_id, picDir=room_id + '.jpg')
        return FileBox.from_file(path=room_id + '.jpg')

    async def dirty_payload(self, payload_type: PayloadType, payload_id: str):
        """
        mark the payload dirty status, and remove it from the cache
        """
        # await self.puppet_stub.dirty_payload(
        #     type=payload_type.value,
        #     id=payload_id
        # )

    async def start(self) -> None:
        """
        start puppet_stub
        :return:
        """
        log.info('starting the puppet ...')
        await self._listen_for_event()
        log.info('puppet has started ...')
        return None

    async def stop(self):
        """
        stop the grpc channel connection
        """
        log.info('stop()')
        self._event_stream.remove_all_listeners()
        return None

    async def logout(self):
        """
        logout the account
        :return:
        """
        log.info('logout()')
        if self.login_user_id is None:
            raise WechatyPuppetOperationError('logout before login?')
        try:
            await self.itchat.logout()
        # pylint: disable=W0703
        except Exception as exception:
            log.error('logout() rejection %s', exception)
        finally:
            payload = EventLogoutPayload(contact_id=self.login_user_id, data='')
            self._event_stream.emit('logout', payload)
            self.login_user_id = None

    async def login(self, user_id: str):
        """
        login the account
        :return:
        """
        self.login_user_id = user_id
        payload = EventLoginPayload(contact_id=user_id)
        self._event_stream.emit('login', payload)

    async def ding(self, data: Optional[str] = ''):
        """
        set the ding event
        :param data:
        :return:
        """
        # log.debug('send ding info to itchat server ...')
        #await self.puppet.ding(data='dong')
        food =watch_dog.WatchdogFood(timeout=3)
        if data:
            data.feed(food)

    # pylint: disable=R0912,R0915
    async def _listen_for_event(self):
        """
        listen event from service server with heartbeat
        """
        log.info('listening the event from the puppet ...')

        async def on_scan(uuid: str):
            payload = EventScanPayload(
                status=ScanStatus.Waiting,
                qrcode=f'https://login.weixin.qq.com/l/{uuid}'
            )
            self._event_stream.emit('scan', payload)
            await asyncio.sleep(0.1)

        async def on_logined(userName: str):
            event_login_payload = EventLoginPayload(contact_id=userName)
            self.login_user_id = userName
            self._event_stream.emit('login', event_login_payload)
            await asyncio.sleep(0.1)

        async def on_logout(userName: str):
            payload = EventLogoutPayload(contact_id=userName, data='')
            self.login_user_id = None
            self._event_stream.emit('logout', payload)
            await asyncio.sleep(0.1)

        await self.itchat.auto_login(
            enableCmdQR=True,
            qrCallback=on_scan,
            EventScanPayload=EventScanPayload,
            ScanStatus=ScanStatus,
            event_stream=self._event_stream,
            loginCallback=on_logined,
            exitCallback=on_logout
        )

        @self.itchat.msg_register([TEXT, MAP, CARD, NOTE, SHARING])
        async def on_message_person_text(msg):
            self.message_container[msg['MsgId']] = msg
            log.info(f'receive message info <{msg.text}>')
            event_message_payload = EventMessagePayload(
                message_id=msg['MsgId'],
                type=msg['Type'],
                from_id=msg['FromUserName'],
                filename=msg['FileName'],
                text=msg['Text'],
                timestamp=msg['CreateTime'],
                to_id=msg['ToUserName']
            )
            self._event_stream.emit('message', event_message_payload)
            await asyncio.sleep(0.1)

        @self.itchat.msg_register([TEXT, MAP, CARD, NOTE, SHARING], isGroupChat=True)
        async def on_message_group_text(msg):
            self.message_container[msg['MsgId']] = msg
            log.info(f'receive message info <{msg.text}>')
            event_message_payload = EventMessagePayload(
                message_id=msg['MsgId'],
                type=msg['Type'],
                from_id=msg['FromUserName'],
                filename=msg['FileName'],
                text=msg['Text'],
                timestamp=msg['CreateTime'],
                to_id=msg['ToUserName']
            )

            self._event_stream.emit('message', event_message_payload)
            await asyncio.sleep(0.1)

        @self.itchat.msg_register([PICTURE, RECORDING, ATTACHMENT, VIDEO])
        async def on_message_person_file(msg):
            self.message_container[msg['MsgId']] = msg
            log.info(f'receive file message info <{msg.FileName}>')
            event_message_payload = EventMessagePayload(
                message_id=msg['MsgId'],
                type=msg['Type'],
                from_id=msg['FromUserName'],
                filename=msg['FileName'],
                text='',
                timestamp=msg['CreateTime'],
                to_id=msg['ToUserName']
            )

            self._event_stream.emit('message', event_message_payload)
            await asyncio.sleep(0.1)

        @self.itchat.msg_register([PICTURE, RECORDING, ATTACHMENT, VIDEO, VOICE], isGroupChat=True)
        async def on_message_group_file(msg):
            self.message_container[msg['MsgId']] = msg
            log.info(f'receive file message info <{msg.FileName}>')
            event_message_payload = EventMessagePayload(
                message_id=msg['MsgId'],
                type=msg['Type'],
                from_id=msg['FromUserName'],
                filename=msg['FileName'],
                text='',
                timestamp=msg['CreateTime'],
                to_id=msg['ToUserName']
            )

            self._event_stream.emit('message', event_message_payload)
            await asyncio.sleep(0.1)

        @self.itchat.msg_register(FRIENDS)
        def add_friend(msg):
            self.message_container[msg['MsgId']] = msg
            log.info(f'receive file message info <{msg.user}>')
            msg.user.verify()

        # @itchat.msg_register(SYSTEM)
        # def handle_system_msg(msg):
        #     log.info(f'receive system message info <{msg["Text"]}>')

        message_container = self.message_container.copy()
        async def run(self, event_stream, payload):
            async def reply_fn():
                try:
                    while self.alive :
                        await asyncio.sleep(2)
                        await self.configured_reply(event_stream=event_stream, payload=payload,
                                                        message_container=message_container)
                        
                except KeyboardInterrupt:
                    if self.useHotReload:
                        await self.dump_login_status()
                    self.alive = False
            await reply_fn()

            #v3
            # 定义一个专门创建事件循环loop的函数，在另一个线程中启动它
            # def start_loop(loop):
            #     asyncio.set_event_loop(loop)
            #     loop.run_forever()
            # new_loop = asyncio.new_event_loop()  # 在当前线程下创建时间循环，（未启用），在start_loop里面启动它
            # import threading
            # t = threading.Thread(target=start_loop, args=(new_loop,))  # 通过当前线程开启新的线程去启动事件循环
            # t.start()

            # asyncio.run_coroutine_threadsafe(reply_fn(), new_loop) 
            # def new_thread():
            #     async def main():           
            #         await reply_fn()
            #     asyncio.run(reply_fn())
            # import threading
            # replyThread = threading.Thread(target=new_thread)
            # replyThread.setDaemon(True)
            # replyThread.start() 
            # while True:
            #     await asyncio.sleep(1)
            #     await reply_fn()
            
        self.itchat.run = types.MethodType(run, self.itchat)#self.itchat.originInstance)
        await self.itchat.run(event_stream=self._event_stream, payload=EventMessagePayload)
