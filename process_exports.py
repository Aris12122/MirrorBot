import os
import json
import random
from data_processor import ConversationParser
from pprint import pformat

def format_conversation_dict(conversations: dict, max_pairs: int = 5) -> str:
    """Format conversations as a readable dictionary string"""
    formatted_dict = {}
    
    for user, pairs in conversations.items():
        # Format each pair as a tuple of (request, response)
        formatted_dict[user] = pairs[:max_pairs]  # Only display first 5 pairs
    
    return pformat(formatted_dict, indent=2, width=100)

def save_random_dialogues(conversations: dict, output_file: str, num_dialogues: int = 4):
    """Save random dialogues from conversations to a file"""
    # Get list of all users
    users = list(conversations.keys())
    
    # Select random users
    selected_users = random.sample(users, min(num_dialogues, len(users)))
    
    # Format and save dialogues
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("=== Random Dialogue Samples ===\n\n")
        for i, user in enumerate(selected_users, 1):
            f.write(f"Dialog {i} with {user}:\n")
            pairs = conversations[user]
            for j, (req, resp) in enumerate(pairs, 1):
                f.write(f"\nExchange {j}:\n")
                f.write(f"User: {req}\n")
                f.write(f"Bot: {resp}\n")
            f.write("=" * 50 + "\n\n")

def main():
    data_export_path = os.path.join(os.path.dirname(__file__), 'DataExport_2025-01-27')
    
    if not os.path.exists(data_export_path):
        print(f"Error: {data_export_path} directory not found")
        return

    parser = ConversationParser(data_export_path)
    conversations = parser.create_conversation_dict()
    
    print("\n=== Conversation Summary ===")
    print(f"Found conversations with {len(conversations)} users")
    print(f"\nShowing first {5} conversation pairs per user:")
    print(format_conversation_dict(conversations))
    
    # Save random dialogues to file in logs directory
    logs_dir = os.path.join(os.path.dirname(__file__), 'logs')
    os.makedirs(logs_dir, exist_ok=True)
    output_file = os.path.join(logs_dir, 'some_dialogs.log')
    save_random_dialogues(conversations, output_file)
    print(f"\nRandom dialogues saved to: {output_file}")
    
    # Print total statistics
    total_pairs = sum(len(pairs) for pairs in conversations.values())
    print(f"\nTotal conversation pairs stored: {total_pairs}")
    print(f"Full debug log available at: {parser.debug_log_path}")

if __name__ == "__main__":
    main()
