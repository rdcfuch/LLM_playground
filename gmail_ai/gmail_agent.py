import argparse
from typing import List, Optional
from pydantic import BaseModel, Field
from gmail_reader import list_unread_subjects, get_email_body_by_subject,list_recent_subjects,mark_mail_as_read_with_subject
from fc_pydantic_agent import DynamicAgent
from dotenv import load_dotenv
import os
from datetime import datetime

# 加载环境变量
load_dotenv()

class MarkEmailAsReadInput(BaseModel):
    """
    输入参数：根据主题标记邮件为已读
    """
    subject: str = Field(description="目标邮件的确切主题")

class MarkEmailAsReadOutput(BaseModel):
    """
    输出结果：标记邮件为已读的结果
    """
    success: bool = Field(description="是否成功标记邮件为已读")
    message: str = Field(description="操作结果的消息")
class ListUnreadEmailsInput(BaseModel):
    """
    输入参数：列出未读邮件主题
    """

    max_results: int = Field(default=10, description="要列出的最大邮件数量", ge=1)
    keyword: Optional[str] = Field(default=None, description="用于过滤主题的关键字")


class ListUnreadEmailsOutput(BaseModel):
    """
    输出结果：未读邮件主题列表
    """

    subjects: List[str] = Field(description="未读邮件的主题列表")


class GetFullEmailInput(BaseModel):
    """
    输入参数：获取完整邮件正文
    """

    subject: str = Field(description="目标邮件的确切主题")


class GetFullEmailOutput(BaseModel):
    """
    输出结果：邮件正文内容
    """

    body: str = Field(description="邮件的完整正文内容")


class ListAllUpdatedAddressInput(BaseModel):
    """
    输入参数：列出包含关键字的邮件主题和时间戳
    """

    number_of_latest_email_to_check: int = Field(
        default=10, description="要检查的最近邮件数量", ge=1
    )
    keyword: str = Field(description="搜索的关键字")


class ListAllUpdatedAddressOutput(BaseModel):
    """
    输出结果：包含关键字的邮件主题和时间戳
    """

    results: List[dict] = Field(description="包含主题和时间戳的邮件列表")


class GmailAgent:
    def __init__(self, model_type: str = "ollama"):
        self.agent = DynamicAgent(
            model_type=model_type,
            system_prompt="""
You are a highly specialized Gmail assistant AI designed to manage and analyze email data effectively. Your primary tasks include listing unread emails, retrieving full email contents by subject, and searching for recent emails containing specific keywords along with their timestamps. 

Your capabilities include:
1. **List Unread Emails**: You can list up to a specified number of unread email subjects. Optionally, you can filter these subjects using a keyword.
2. **Retrieve Full Email Content**: Given an exact email subject, you can retrieve the complete content of that email.
3. **Search Recent Emails**: You can search through the most recent emails (up to a specified number) for those containing a particular keyword in their subject lines. For matching emails, you will provide both the subject and the timestamp.

Use these tools to provide comprehensive insights into the user's email data. Always strive to offer detailed and accurate information tailored to the user's queries. Remember to handle exceptions gracefully and inform the user if any issues arise during your operations.
""",
        )

        # 添加工具
        self.agent.add_tool(self.list_unread_emails)
        self.agent.add_tool(self.get_full_email)
        # self.agent.add_tool(self.list_all_updated_address)
        # self.agent.add_tool(self.mark_email_as_read)  
        # 手动记录工具的元数据
        self.tool_metadata = {
            "list_unread_emails": {
                "input_model": ListUnreadEmailsInput,
                "output_model": ListUnreadEmailsOutput,
            },
            "get_full_email": {
                "input_model": GetFullEmailInput,
                "output_model": GetFullEmailOutput,
            },
            # "list_all_updated_address": {
            #     "input_model": ListAllUpdatedAddressInput,
            #     "output_model": ListAllUpdatedAddressOutput,
            # },
            # "mark_email_as_read": {  # Add metadata for the new tool
            #     "input_model": MarkEmailAsReadInput,
            #     "output_model": MarkEmailAsReadOutput,
            # },
        }

    def list_unread_emails(
            self, input_data: ListUnreadEmailsInput
    ) -> ListUnreadEmailsOutput:
        """
        列出未读邮件主题，支持关键字过滤
        """
        try:
            max_results = input_data.max_results
            keyword = input_data.keyword
            unread_subjects = list_unread_subjects(
                max_results=max_results, keyword=keyword
            )
            return ListUnreadEmailsOutput(subjects=unread_subjects)
        except Exception as e:
            raise ValueError(f"Error listing emails: {str(e)}")

    def get_full_email(self, input_data: GetFullEmailInput) -> GetFullEmailOutput:
        """
        根据确切主题获取完整邮件正文
        """
        try:
            subject = input_data.subject.strip()
            if not subject:
                raise ValueError("Error: Subject cannot be empty")
            email_body = get_email_body_by_subject(subject)
            return GetFullEmailOutput(body=email_body)
        except Exception as e:
            raise ValueError(f"Error retrieving email: {str(e)}")

    def list_all_updated_address(
            self, input_data: ListAllUpdatedAddressInput
    ) -> ListAllUpdatedAddressOutput:
        """
        搜索最近的邮件，查找包含关键字的邮件，并返回其主题和时间戳
        """
        try:
            service = self._get_gmail_service()
            results = (
                service.users()
                .messages()
                .list(
                    userId="me", maxResults=input_data.number_of_latest_email_to_check
                )
                .execute()
            )
            messages = results.get("messages", [])
            matching_emails = []
            for message in messages:
                msg = (
                    service.users()
                    .messages()
                    .get(
                        userId="me",
                        id=message["id"],
                        format="metadata",
                        metadataHeaders=["Subject", "Date"],
                    )
                    .execute()
                )
                subject = next(
                    (
                        header["value"]
                        for header in msg["payload"]["headers"]
                        if header["name"] == "Subject"
                    ),
                    "No Subject",
                )
                date = next(
                    (
                        header["value"]
                        for header in msg["payload"]["headers"]
                        if header["name"] == "Date"
                    ),
                    "No Date",
                )
                # 检查主题中是否包含关键字
                if input_data.keyword.lower() in subject.lower():
                    matching_emails.append({"subject": subject, "timestamp": date})
            return ListAllUpdatedAddressOutput(results=matching_emails)
        except Exception as e:
            raise ValueError(f"Error searching emails: {str(e)}")

    def _get_gmail_service(self):
        """
        创建并返回 Gmail API 客户端实例
        """
        creds = Credentials(
            token=None,
            refresh_token=os.getenv("GOOGLE_REFRESH_TOKEN"),
            client_id=os.getenv("GOOGLE_CLIENT_ID"),
            client_secret=os.getenv("GOOGLE_CLIENT_SECRET"),
            token_uri="https://oauth2.googleapis.com/token",
        )
        return build("gmail", "v1", credentials=creds)

    def mark_email_as_read(self, input_data: MarkEmailAsReadInput) -> MarkEmailAsReadOutput:
        """
        根据确切主题标记邮件为已读
        """
        try:
            result = mark_mail_as_read_with_subject(input_data.subject)
            return MarkEmailAsReadOutput(success=result["success"], message=result["message"])
        except Exception as e:
            raise ValueError(f"Error marking email as read: {str(e)}")

    def chat(self, query: str) -> str:
        """
        处理自然语言查询
        """
        try:
            return self.agent.interact_with_model(query)
        except Exception as e:
            return f"Error processing query: {str(e)}"


if __name__ == "__main__":
    # 初始化 GmailAgent
    gmail_agent = GmailAgent(model_type="ollama")

    print("Gmail AI Agent initialized. Type 'quit' to exit.")

    while True:
        # 提示用户输入问题
        user_input = input("\nEnter your query (or type 'quit' to exit): ").strip()

        # 如果用户输入 'quit'，退出循环
        if user_input.lower() == "quit":
            print("Exiting Gmail AI Agent. Goodbye!")
            break

        # 如果用户输入为空，提示重新输入
        if not user_input:
            print("Query cannot be empty. Please try again.")
            continue

        # 调用 chat 方法处理用户输入
        try:
            response = gmail_agent.chat(user_input)
            print(f"\nResponse: {response}")
        except Exception as e:
            print(f"\nError processing query: {str(e)}")
