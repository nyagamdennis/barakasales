from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import sync_to_async
import json

class EmployeeStatusConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.employee_id = self.scope['url_route']['kwargs']['employee_id']
        self.group_name = f"employee_status_{self.employee_id}"

        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

        # ⬇️ Use sync_to_async inside the connect method
        verified = await self.get_verified_status(self.employee_id)
        await self.send(text_data=json.dumps({'verified': verified}))

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def send_verification_status(self, event):
        await self.send(text_data=json.dumps({'verified': event['verified']}))

    @sync_to_async
    def get_verified_status(self, employee_id):
        from BarakaApp.models import Employees  # ⬅️ Import inside the function to avoid early loading
        try:
            return Employees.objects.get(pk=employee_id).verified
        except Employees.DoesNotExist:
            return False
