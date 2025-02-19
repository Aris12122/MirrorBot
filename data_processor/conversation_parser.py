import os
import json
from datetime import datetime
from typing import List, Dict, Tuple

class ConversationParser:
    def __init__(self, data_export_path: str):
        self.data_export_path = data_export_path
        self.debug_log_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 
                                         'logs', 'debug.log')
        
        # Create logs directory if it doesn't exist
        os.makedirs(os.path.dirname(self.debug_log_path), exist_ok=True)
        
        # Clear debug log file
        with open(self.debug_log_path, 'w', encoding='utf-8') as f:
            f.write(f"=== Debug Log Started: {datetime.now()} ===\n\n")
            
    def log_debug(self, message: str):
        """Write debug message to log file"""
        with open(self.debug_log_path, 'a', encoding='utf-8') as f:
            f.write(f"{message}\n")

    def get_chat_files(self) -> List[str]:
        """Return path to result.json file"""
        result_file = os.path.join(self.data_export_path, 'result.json')
        self.log_debug(f"Checking for result.json at: {result_file}")
        if os.path.exists(result_file):
            return [result_file]
        return []

    def parse_chat(self, chat_file: str) -> List[Dict]:
        """Parse individual chat file and return structured data"""
        try:
            with open(chat_file, 'r', encoding='utf-8') as f:
                self.log_debug("\nReading complete JSON file...")
                data = json.load(f)
                self.log_debug("JSON file loaded successfully")

                # Get all chats from the list array (removed limit)
                chats_list = data.get('chats', {}).get('list', [])
                self.log_debug(f"\nProcessing {len(chats_list)} chats")

                all_chats = []
                for chat in chats_list:
                    chat_name = chat.get('name', 'Unknown')
                    self.log_debug(f"\nProcessing chat: {chat_name}")
                    
                    messages = []
                    for msg in chat.get('messages', []):
                        # Handle complex text structure (arrays with entities)
                        text = msg.get('text', '')
                        if isinstance(text, list):
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
                        'chat_name': chat_name,
                        'messages': messages
                    }
                    self.log_debug(f"Messages processed: {len(messages)}")
                    all_chats.append(chat_data)
                
                return all_chats
                
        except json.JSONDecodeError as e:
            error_msg = f"\nJSON Error at position {e.pos}"
            self.log_debug(error_msg)
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
        """Extract pairs of messages (concatenated user messages, Tropin's responses)"""
        pairs = []
        accumulated_user_messages = []
        accumulated_bot_responses = []
        
        for msg in messages:
            from_user = msg.get('from', '')
            text = msg.get('text', '')
            
            self.log_debug(f"\nProcessing message from '{from_user}': '{text}'")
            
            # Skip empty messages
            if not text or not isinstance(text, str):
                continue
                
            if '️Tropin Mikhail' in from_user or 'Tropin Mikhail' in from_user:
                # Accumulate bot responses
                accumulated_bot_responses.append(text)
            else:
                # If we have both user messages and bot responses, create a pair
                if accumulated_user_messages and accumulated_bot_responses:
                    combined_user_msg = ' '.join(accumulated_user_messages)
                    combined_bot_msg = ' '.join(accumulated_bot_responses)
                    pairs.append((combined_user_msg, combined_bot_msg))
                    self.log_debug(f"Created pair: ({combined_user_msg}, {combined_bot_msg})")
                    
                # Reset bot responses and start new user message accumulation
                accumulated_bot_responses = []
                accumulated_user_messages = [text]
                self.log_debug(f"Started new message accumulation from {from_user}")
                
        # Handle last pair if exists
        if accumulated_user_messages and accumulated_bot_responses:
            combined_user_msg = ' '.join(accumulated_user_messages)
            combined_bot_msg = ' '.join(accumulated_bot_responses)
            pairs.append((combined_user_msg, combined_bot_msg))
            self.log_debug(f"Created final pair: ({combined_user_msg}, {combined_bot_msg})")
                
        return pairs

    def create_conversation_dict(self) -> Dict[str, List[Tuple[str, str]]]:
        """Create dictionary of conversations by user"""
        user_conversations = {}
        
        for chat_file in self.get_chat_files():
            try:
                chats_data = self.parse_chat(chat_file)
                
                for chat_data in chats_data:
                    chat_name = chat_data['chat_name']
                    self.log_debug(f"\nProcessing chat: '{chat_name}'")
                    
                    # Modified conditions for skipping chats
                    if not chat_name or chat_name == 'None' or 'group' in chat_name.lower():
                        self.log_debug(f"Skipping chat: {chat_name}")
                        continue
                    
                    pairs = self.extract_conversation_pairs(chat_data['messages'])
                    self.log_debug(f"Found {len(pairs)} pairs for {chat_name}")
                    
                    if pairs:  # Only add if there are actual conversations
                        user_conversations[chat_name] = pairs  # Store all pairs
                        self.log_debug(f"Stored {len(pairs)} pairs for {chat_name}")
                    
            except Exception as e:
                self.log_debug(f"Error processing {chat_file}: {str(e)}")
                
        return user_conversations
