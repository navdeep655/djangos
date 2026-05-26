# import json
# from channels.generic.websocket import AsyncWebsocketConsumer

# class ChatConsumer(AsyncWebsocketConsumer):

#     async def connect(self):
#         # 👇 Get room and username from URL
#         self.room_name = self.scope['url_route']['kwargs']['room_name']
#         self.username = self.scope['url_route']['kwargs']['username']
#         self.room_group_name = f'chat_{self.room_name}'

#         # Join the group
#         await (self.channel_layer.group_add)(
#             self.room_group_name,
#             self.channel_name
#         )

#         # Announce to the room that someone joined
#         await (self.channel_layer.group_send)(
#             self.room_group_name,
#             {
#                 'type': 'chat_message',
#                 'message': f'{self.username} joined the room 👋',
#                 'username': '🔔 System',
#                 'is_system': True
#             }
#         )

#         self.accept()

#     async def disconnect(self, close_code):
#         # Announce to the room that someone left
#         await(self.channel_layer.group_send)(
#             self.room_group_name,
#             {
#                 'type': 'chat_message',
#                 'message': f'{self.username} left the room 👋',
#                 'username': '🔔 System',
#                 'is_system': True
#             }
#         )

#         await(self.channel_layer.group_discard)(
#             self.room_group_name,
#             self.channel_name
#         )

#     async def receive(self, text_data):
#         data = json.loads(text_data)
#         message = data['message']

#         # Send to the whole group WITH username
#         await(self.channel_layer.group_send)(
#             self.room_group_name,
#             {
#                 'type': 'chat_message',
#                 'message': message,
#                 'username': self.username,  # 👈 include username
#                 'is_system': False
#             }
#         )

#     def chat_message(self, event):
#         # Send message to WebSocket
#         self.send(text_data=json.dumps({
#             'message': event['message'],
#             'username': event['username'],
#             'is_system': event['is_system']
#         }))







# from channels.generic.websocket import WebsocketConsumer
# class chat(WebsocketConsumer):
#     def connect(self):
#         self.accept()
#     def disconnect(self,close):
#         pass
#     def receive(self,text_data):
#         self.send(text_data)



import json
from channels.generic.websocket  import AsyncWebsocketConsumer
from channels.db                 import database_sync_to_async
from django.contrib.auth.models  import User
from .models                     import chatroomr, JoinRequest, Message


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_id    = self.scope["url_route"]["kwargs"]["room_id"]
        self.room_group = f"chat_{self.room_id}"
        self.user       = self.scope["user"]

        # User authenticated nahi hai
        if not self.user.is_authenticated:
            await self.close()
            return

        # Room exist karti hai?
        self.room = await self.get_room()
        if not self.room:
            await self.close()
            return

        # Channel group mein join karo
        await self.channel_layer.group_add(
            self.room_group,
            self.channel_name
        )
        await self.accept()

        # Check karo user ka status
        self.is_owner    = await self.check_owner()
        self.is_accepted = await self.check_accepted()

        # Connect hone par apna status bhejo
        await self.send(text_data=json.dumps({
            "type":       "connection_status",
            "is_owner":   self.is_owner,
            "is_accepted": self.is_accepted,
            "username":   self.user.username,
        }))

        # Purane messages load karke bhejo
        if self.is_owner or self.is_accepted:
            old_messages = await self.get_old_messages()
            for msg in old_messages:
                await self.send(text_data=json.dumps({
                    "type":     "chat_message",
                    "message":  msg["message"],
                    "username": msg["username"],
                    "time":     msg["time"],
                }))

        # Online notify karo
        if self.is_owner or self.is_accepted:
            await self.channel_layer.group_send(
                self.room_group,
                {
                    "type":     "user_joined",
                    "username": self.user.username,
                }
            )


    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group,
            self.channel_name
        )


    async def receive(self, text_data):
        data     = json.loads(text_data)
        msg_type = data.get("type")
        # ── CHAT MESSAGE ──
        if msg_type == "chat_message":
            is_owner    = await self.check_owner()
            is_accepted = await self.check_accepted()

            if not is_owner and not is_accepted:
                await self.send(text_data=json.dumps({
                    "type":    "error",
                    "message": "Chat disabled — owner ka wait karo"
                }))
                return

            message = data.get("message", "").strip()
            if message:

                #  DB mein save karo
                await self.save_message(message)
                await self.channel_layer.group_send(
                    self.room_group,
                    {
                        "type":     "chat_message",
                        "message":  message,
                        "username": self.user.username,
                    }
                )

        # ── OWNER: ACCEPT / REJECT REQUEST ──
        elif msg_type == "handle_request":
            is_owner = await self.check_owner()
            if not is_owner:
                return
            action     = data.get("action")
            request_id = data.get("request_id")
            result = await self.handle_join_request(request_id, action)
            if result:
                await self.channel_layer.group_send(
                    self.room_group,
                    {
                        "type":      "request_handled",
                        "action":    action,
                        "username":  result["username"],
                        "sender_id": result["sender_id"],
                    }
                )


    # ── GROUP MESSAGE HANDLERS ──
    async def chat_message(self, event):
        await self.send(text_data=json.dumps({
            "type":     "chat_message",
            "message":  event["message"],
            "username": event["username"],
            "time":     event.get("time", ""),
        }))

    async def user_joined(self, event):
        await self.send(text_data=json.dumps({
            "type":     "user_joined",
            "username": event["username"],
        }))

    async def request_handled(self, event):
        await self.send(text_data=json.dumps({
            "type":      "request_handled",
            "action":    event["action"],
            "username":  event["username"],
            "sender_id": event["sender_id"],
        }))

    # ── DATABASE HELPERS ──
    @database_sync_to_async
    def get_room(self):
        try:
            return chatroomr.objects.get(id=self.room_id)
        except chatroomr.DoesNotExist:
            return None
    @database_sync_to_async
    def check_owner(self):
        return self.room.owner == self.user
    @database_sync_to_async
    def check_accepted(self):
        return JoinRequest.objects.filter(
            room_name=self.room,
            sender_name=self.user,
            status="accepted"
        ).exists()
    @database_sync_to_async
    def save_message(self, content):
        # Message DB mein save karo
        return Message.objects.create(
            room=self.room,
            message_sender=self.user,
            content=content
        )

    @database_sync_to_async
    def get_old_messages(self):
        # Last 50 messages load karo
        messages = Message.objects.filter(
            room=self.room
        ).select_related("message_sender").order_by("timestamp")[:50]

        return [
            {
                "username": msg.message_sender.username,
                "message":  msg.content,
                "time":     msg.timestamp.strftime("%H:%M"),
            }
            for msg in messages
        ]

    @database_sync_to_async
    def handle_join_request(self, request_id, action):
        try:
            req        = JoinRequest.objects.get(id=request_id, room_name=self.room)
            req.status = action
            req.save()
            if action == "accepted":
                self.room.members.add(req.sender_name)
            return {
                "username":  req.sender_name.username,
                "sender_id": req.sender_name.id,
            }
        except JoinRequest.DoesNotExist:
            return None