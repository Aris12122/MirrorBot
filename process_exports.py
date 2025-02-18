import os
import json
from data_processor import ConversationParser
from pprint import pformat

def format_conversation_dict(conversations: dict, max_pairs: int = 5) -> str:
    """Format conversations as a readable dictionary string"""
    formatted_dict = {}
    
    for user, pairs in conversations.items():
        # Limit to max_pairs per user
        limited_pairs = pairs[:max_pairs]
        # Format each pair as a tuple of (request, response)
        formatted_pairs = [
            (user_msg, tropin_msg)
            for user_msg, tropin_msg in limited_pairs
        ]
        formatted_dict[user] = formatted_pairs
    
    # Use pformat for nice dictionary formatting
    return pformat(formatted_dict, indent=2, width=100)

def main():
    data_export_path = os.path.join(os.path.dirname(__file__), 'DataExport_2025-01-27')
    
    if not os.path.exists(data_export_path):
        print(f"Error: {data_export_path} directory not found")
        return

    parser = ConversationParser(data_export_path)
    conversations = parser.create_conversation_dict()
    
    print("\n=== Conversation Dictionary ===")
    print(f"Found conversations with {len(conversations)} users")
    print("\nConversation pairs (limited to 5 per user):")
    print(format_conversation_dict(conversations))

if __name__ == "__main__":
    main()
