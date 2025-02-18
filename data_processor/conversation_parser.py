import os
import json
from datetime import datetime
from typing import List, Dict, Tuple

class ConversationParser:
    def __init__(self, data_export_path: str):
        self.data_export_path = data_export_path
        
    def get_chat_files(self) -> List[str]:
        """Return path to result.json file"""
        result_file = os.path.join(self.data_export_path, 'result.json')
        if os.path.exists(result_file):
            print(f"Found result.json at: {result_file}")
            return [result_file]
        else:
            print(f"Error: result.json not found in {self.data_export_path}")
            return []

    def parse_chat(self, chat_file: str) -> List[Dict]:
        """Parse individual chat file and return structured data"""
        try:
            with open(chat_file, 'r', encoding='utf-8') as f:
                print("\nReading complete JSON file...")
                data = json.load(f)
                print("JSON file loaded successfully")

                # Get first 5 chats from the list array
                chats_list = data.get('chats', {}).get('list', [])[:5]  # Limit to first 5 chats
                print(f"\nDebug - Processing first {len(chats_list)} chats")

                all_chats = []
                for chat in chats_list:
                    print(f"\nProcessing chat: {chat.get('name', 'Unknown')}")
                    
                    messages = []
                    for msg in chat.get('messages', []):
                        # Handle complex text structure (arrays with entities)
                        text = msg.get('text', '')
                        if isinstance(text, list):
                            # Concatenate all text parts
                            text = ''.join(
                                item['text'] if isinstance(item, dict) else item
                                for item in text
                            )

                        msg_data = {
                            'text': text,
                            'timestamp': msg.get('date', ''),
                            'from': msg.get('from', ''),
                            'type': msg.get('type', '')
                        }
                        messages.append(msg_data)
                    
                    chat_data = {
                        'chat_name': chat.get('name', ''),
                        'messages': messages
                    }
                    print(f"Chat name: '{chat_data['chat_name']}'")
                    print(f"Messages processed: {len(messages)}")
                    all_chats.append(chat_data)
                
                return all_chats
                
        except json.JSONDecodeError as e:
            print(f"\nJSON Error at position {e.pos}:")
            with open(chat_file, 'r', encoding='utf-8') as f:
                content = f.read()
                start = max(0, e.pos - 50)
                end = min(len(content), e.pos + 50)
                print(f"Context: ...{content[start:end]}...")
            raise

    def process_all_chats(self) -> List[Dict]:
        """Process all chat files and return structured data"""
        all_chats = []
        chat_files = self.get_chat_files()
        
        for chat_file in chat_files:
            try:
                chats_data = self.parse_chat(chat_file)
                all_chats.extend(chats_data)  # Changed from append to extend
            except Exception as e:
                print(f"Error processing {chat_file}: {str(e)}")
                
        return all_chats

    def extract_conversation_pairs(self, messages: List[Dict]) -> List[Tuple[str, str]]:
        """Extract pairs of messages (concatenated user messages, Tropin's response)"""
        pairs = []
        accumulated_messages = []
        
        for msg in messages:
            from_user = msg.get('from', '')
            text = msg.get('text', '')
            
            print(f"\nDebug - Processing message:")
            print(f"From: '{from_user}'")  # Added quotes to see exact string
            print(f"Text: '{text}'")
            
            # Skip empty messages
            if not text or not isinstance(text, str):
                continue
                
            # Changed condition to handle variations in name
            if '️Tropin Mikhail' in from_user or 'Tropin Mikhail' in from_user:
                # If we have accumulated messages, create a pair
                if accumulated_messages:
                    combined_message = ' '.join(accumulated_messages)
                    pairs.append((combined_message, text))
                    print(f"Created pair: ({combined_message}, {text})")
                    accumulated_messages = []  # Reset accumulator
            else:
                # Accumulate messages from other users
                accumulated_messages.append(text)
                print(f"Accumulated message from {from_user}")
                
        return pairs

    def create_conversation_dict(self) -> Dict[str, List[Tuple[str, str]]]:
        """Create dictionary of conversations by user"""
        user_conversations = {}
        
        for chat_file in self.get_chat_files():
            try:
                chats_data = self.parse_chat(chat_file)
                
                for chat_data in chats_data:
                    chat_name = chat_data['chat_name']
                    print(f"\nProcessing chat: '{chat_name}'")  # Added quotes for debugging
                    
                    # Modified conditions for skipping chats
                    if not chat_name or chat_name == 'None' or 'group' in chat_name.lower():
                        print(f"Skipping chat: {chat_name}")
                        continue
                    
                    pairs = self.extract_conversation_pairs(chat_data['messages'])
                    print(f"Found {len(pairs)} pairs for {chat_name}")
                    
                    if pairs:  # Only add if there are actual conversations
                        user_conversations[chat_name] = pairs[:5]  # Limit to 5 pairs here
                        print(f"Added {len(pairs[:5])} pairs for {chat_name}")
                    
            except Exception as e:
                print(f"Error processing {chat_file}: {str(e)}")
                print(f"Debug - Error details:", str(e.__class__.__name__))
                
        return user_conversations
