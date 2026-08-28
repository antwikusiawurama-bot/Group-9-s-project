from datetime import datetime
class Message:
    def __init__(self, message_id, sender_id, recipient_id, content):
        self.message_id = message_id
        self.sender_id = sender_id
        self.recipient_id = recipient_id
        self.content = content
        self.timestamp = datetime.now().isoformat()
        self.read = False

    def to_dict(self):
        return {
            "message_id": self.message_id,
            "sender_id": self.sender_id,
            "recipient_id": self.recipient_id,
            "content": self.content,
            "timestamp": self.timestamp,
            "read": self.read
        }