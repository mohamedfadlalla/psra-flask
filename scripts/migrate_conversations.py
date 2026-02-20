import sys
import os

# Add the project directory to sys.path so we can import app and models
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app, db
from models import Message, Conversation, ConversationParticipant

def migrate_conversations():
    with app.app_context():
        messages = Message.query.filter(Message.conversation_id == None).all()
        print(f"Found {len(messages)} messages to migrate to conversations.")
        
        # Group by pairs
        pairs = set()
        for m in messages:
            pair = tuple(sorted([m.sender_id, m.receiver_id]))
            pairs.add(pair)
            
        print(f"Found {len(pairs)} distinct conversations to create.")
        
        for p1, p2 in pairs:
            # Check if conversation already exists for this pair
            # Since participants are unique pairs, we can just create it.
            # But let's check first to be safe
            existing = db.session.query(Conversation).join(ConversationParticipant).filter(
                ConversationParticipant.user_id.in_([p1, p2])
            ).group_by(Conversation.id).having(db.func.count(ConversationParticipant.user_id) == 2).first()
            
            if not existing:
                conv = Conversation()
                db.session.add(conv)
                db.session.flush() # get id
                
                cp1 = ConversationParticipant(conversation_id=conv.id, user_id=p1)
                cp2 = ConversationParticipant(conversation_id=conv.id, user_id=p2)
                db.session.add_all([cp1, cp2])
            else:
                conv = existing
            
            # Update all messages between p1 and p2
            Message.query.filter(
                ((Message.sender_id == p1) & (Message.receiver_id == p2)) |
                ((Message.sender_id == p2) & (Message.receiver_id == p1))
            ).update({'conversation_id': conv.id})
            
        try:
            db.session.commit()
            print("Conversation migration completed successfully.")
        except Exception as e:
            db.session.rollback()
            print(f"Migration failed: {e}")

if __name__ == '__main__':
    migrate_conversations()