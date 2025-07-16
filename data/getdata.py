# This script extracts all conversations from the JSON file downloaded from ChatGPT website 
# and writes them to a CSV file.
# The CSV file contains the conversation ID, message ID, role, and text.
# The script also filters out conversations with less than 3 messages.
# The script also cleans the message by removing newlines, carriage returns, and tabs.
# The script also limits the message length to 500 characters.

import json
import csv

def extract_conversations_from_mapping(mapping):
    conversations = []

    def traverse(node_id):
        node = mapping.get(node_id)
        if not node or not isinstance(node, dict):
            return []

        messages = []
        message_obj = node.get("message")
        if message_obj:
            role = message_obj.get("author", {}).get("role")
            parts = message_obj.get("content", {}).get("parts")
            if role in ["user", "assistant"] and parts:
                if isinstance(parts, list):
                    text_list = []
                    for part in parts:
                        if isinstance(part, str):
                            text_list.append(part)
                        elif isinstance(part, dict):
                            text_list.append(part.get("text", str(part)))
                        else:
                            text_list.append(str(part))
                    text = ' '.join(text_list)
                else:
                    text = str(parts)
                messages.append((role, text.strip()))

        for child_id in node.get("children", []):
            messages.extend(traverse(child_id))
        return messages

    for node_id, node in mapping.items():
        if node.get("parent") is None and node.get("children"):
            messages = traverse(node_id)
            if messages:
                conversations.append(messages)
    return conversations



def extract_all_conversations(json_path):
    """
    Extract all conversations from the JSON file.
    """
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    all_messages = []

    if isinstance(data, dict):
        mapping = data.get("mapping", {})
        all_messages.extend(extract_conversations_from_mapping(mapping))
    elif isinstance(data, list):
        for item in data:
            if isinstance(item, dict) and "mapping" in item:
                mapping = item["mapping"]
                all_messages.extend(extract_conversations_from_mapping(mapping))
    else:
        mapping = {}

    return all_messages


file_path = "./conversations.json"
conversations = extract_all_conversations(file_path)

# Filter conversations to only those with at least 3 messages
filtered_conversations = [convo for convo in conversations if len(convo) >= 3]

def clean_message(msg):
    """
    Clean the message by removing newlines, carriage returns, and tabs.
    """
    msg = msg.strip()
    msg = msg.replace('\n', ' ').replace('\r', ' ').replace('\t', ' ')
    msg = ' '.join(msg.split())
    return msg

with open("conversations.csv", "w", encoding="utf-8", newline='') as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(["Conversation", "Message", "Role", "Text"])
    for convo_idx, convo in enumerate(filtered_conversations, start=1):
        for msg_idx, (role, msg) in enumerate(convo, start=1):
            cleaned_msg = clean_message(msg)
            if cleaned_msg:
                if len(cleaned_msg) > 500:
                    cleaned_msg = cleaned_msg[:500] + "..."
                writer.writerow([convo_idx, msg_idx, role.upper(), cleaned_msg])