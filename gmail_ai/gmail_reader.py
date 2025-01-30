import os
import base64
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

class UpdatedAddress:
    """
    表示更新的邮件地址，包含主题和时间戳。
    """
    def __init__(self, subject: str, timestamp: str):
        self.subject = subject
        self.timestamp = timestamp

    def __repr__(self):
        return f"UpdatedAddress(subject='{self.subject}', timestamp='{self.timestamp}')"

def get_gmail_service():
    """
    创建并返回 Gmail API 客户端实例。
    """
    creds = Credentials(
        token=None,
        refresh_token=os.getenv('GOOGLE_REFRESH_TOKEN'),
        client_id=os.getenv('GOOGLE_CLIENT_ID'),
        client_secret=os.getenv('GOOGLE_CLIENT_SECRET'),
        token_uri='https://oauth2.googleapis.com/token'
    )
    service = build('gmail', 'v1', credentials=creds)
    return service

def list_unread_subjects(max_results=10, keyword=None):
    """
    列出未读邮件的主题，并支持通过关键字过滤。
    """
    service = get_gmail_service()
    results = service.users().messages().list(
        userId='me',
        labelIds=['INBOX'],
        q='is:unread',
        maxResults=max_results
    ).execute()
    messages = results.get('messages', [])
    filtered_subjects = []
    for message in messages:
        msg = service.users().messages().get(
            userId='me',
            id=message['id'],
            format='metadata',
            metadataHeaders=['Subject']
        ).execute()
        subject = next(
            (header['value'] for header in msg['payload']['headers']
             if header['name'] == 'Subject'),
            'No Subject'
        )
        if not keyword or keyword.lower() in subject.lower():
            filtered_subjects.append(subject)
            print(f"- {subject}")
    return filtered_subjects

def list_recent_subjects(max_results=10):
    """
    列出最近的 max_results 个邮件的主题。
    """
    service = get_gmail_service()
    results = service.users().messages().list(
        userId='me',
        maxResults=max_results
    ).execute()
    messages = results.get('messages', [])
    recent_subjects = []
    for message in messages:
        msg = service.users().messages().get(
            userId='me',
            id=message['id'],
            format='metadata',
            metadataHeaders=['Subject']
        ).execute()
        subject = next(
            (header['value'] for header in msg['payload']['headers']
             if header['name'] == 'Subject'),
            'No Subject'
        )
        recent_subjects.append(subject)
        print(f"- {subject}")
    return recent_subjects

def list_all_updated_address(number_of_latest_email_to_check: int, keyword: str):
    """
    列出最近的 number_of_latest_email_to_check 封邮件中包含关键字 keyword 的邮件主题和时间戳。
    
    参数:
        number_of_latest_email_to_check (int): 需要检查的最新邮件数量。
        keyword (str): 要搜索的关键字。
    
    返回:
        list: 包含匹配邮件的 UpdatedAddress 对象的列表。
    """
    service = get_gmail_service()
    results = service.users().messages().list(
        userId='me',
        maxResults=number_of_latest_email_to_check
    ).execute()
    messages = results.get('messages', [])
    
    matched_emails = []
    
    for message in messages:
        # 获取邮件的元数据（主题和时间戳）
        msg_metadata = service.users().messages().get(
            userId='me',
            id=message['id'],
            format='metadata',
            metadataHeaders=['Subject', 'Date']
        ).execute()
        
        # 提取邮件主题和时间戳
        subject = next(
            (header['value'] for header in msg_metadata['payload']['headers']
             if header['name'] == 'Subject'),
            'No Subject'
        )
        timestamp = next(
            (header['value'] for header in msg_metadata['payload']['headers']
             if header['name'] == 'Date'),
            'No Timestamp'
        )
        
        # 检查邮件主题是否包含关键字
        if keyword.lower() in subject.lower():
            updated_address = UpdatedAddress(subject, timestamp)
            matched_emails.append(updated_address)
            print(f"- Subject: {subject}, Timestamp: {timestamp}")
    
    return matched_emails

if __name__ == '__main__':
    # import argparse
    # parser = argparse.ArgumentParser(description='Read Gmail inbox')
    # parser.add_argument('--subject', help='Get full body of email with specific subject')
    # parser.add_argument('--filter', help='Filter subjects by keyword')
    # parser.add_argument('--max', type=int, default=10, help='Max emails to check')
    # parser.add_argument('--unread', action='store_true', help='Show only unread emails')
    # parser.add_argument('--recent', action='store_true', help='Show recent email subjects')
    # parser.add_argument('--updated', action='store_true', help='List updated addresses with keyword')
    # parser.add_argument('--keyword', help='Keyword to search in emails')
    # args = parser.parse_args()
    
    # if args.subject:
    #     print("\nSubject-based search is no longer supported.")
    # elif args.unread:
    #     print("\nUnread Email Subjects:")
    #     list_unread_subjects(args.max, args.filter)
    # elif args.recent:
    #     print("\nRecent Email Subjects:")
    #     list_recent_subjects(args.max)
    # elif args.updated and args.keyword:
    #     print(f"\nChecking latest {args.max} emails for keyword '{args.keyword}':")
    #     matched_emails = list_all_updated_address(args.max, args.keyword)
    #     if not matched_emails:
    #         print("No matching emails found.")
    # elif args.filter:
    #     print(f"\nSubjects containing '{args.filter}':")
    #     list_unread_subjects(args.max, args.filter)
    # else:
    #     print("\nLatest Inbox Subjects:")
    #     list_unread_subjects(args.max)
    
    updated_addresses = list_all_updated_address(100, "update")
    print(updated_addresses)