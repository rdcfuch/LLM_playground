import argparse
from typing import List, Optional
from pydantic import BaseModel, Field
from dotenv import load_dotenv
import os
from GoogleDriveManager import GoogleDriveManager
from fc_pydantic_agent import DynamicAgent

# Load environment variables
load_dotenv()

class ListFilesInFolderInput(BaseModel):
    """
    Input parameters: List files in a specific folder
    """
    folder_id: str = Field(description="The ID of the folder to list files from")
    max_results: int = Field(default=10, description="Maximum number of files to list", ge=1)

class ListFilesInFolderOutput(BaseModel):
    """
    Output result: List of files in the folder
    """
    files: List[dict] = Field(description="List of file names and IDs")

class UploadFileInput(BaseModel):
    """
    Input parameters: Upload a file to a specific folder
    """
    folder_id: str = Field(description="The ID of the folder to upload the file to")
    file_path: str = Field(description="Local path of the file to upload")

class UploadFileOutput(BaseModel):
    """
    Output result: File upload result
    """
    success: bool = Field(description="Whether the file was uploaded successfully")
    message: str = Field(description="Details about the upload operation")
    file_id: Optional[str] = Field(description="ID of the uploaded file")

class DownloadFileInput(BaseModel):
    """
    Input parameters: Download a file from Google Drive
    """
    file_id: str = Field(description="The ID of the file to download")
    destination_path: str = Field(description="Local path to save the downloaded file")

class DownloadFileOutput(BaseModel):
    """
    Output result: File download result
    """
    success: bool = Field(description="Whether the file was downloaded successfully")
    message: str = Field(description="Details about the download operation")

class DeleteFileInput(BaseModel):
    """
    Input parameters: Delete a file from Google Drive
    """
    file_id: str = Field(description="The ID of the file to delete")

class DeleteFileOutput(BaseModel):
    """
    Output result: File deletion result
    """
    success: bool = Field(description="Whether the file was deleted successfully")
    message: str = Field(description="Details about the deletion operation")

class GoogleDriveAgent:
    def __init__(self, model_type: str = "ollama"):
        self.drive_manager = GoogleDriveManager()
        self.agent = DynamicAgent(
            model_type=model_type,
            system_prompt="""
You are a highly specialized Google Drive assistant AI designed to manage and analyze files on Google Drive effectively. Your primary tasks include:
1. **List Files in Folder**: You can list up to a specified number of files in a specific folder.
2. **Upload Files**: You can upload files from the local machine to a specific folder on Google Drive.
3. **Download Files**: You can download files from Google Drive to the local machine.
4. **Delete Files**: You can delete files from Google Drive.
Use these tools to provide comprehensive insights into the user's Google Drive data. Always strive to offer detailed and accurate information tailored to the user's queries. Remember to handle exceptions gracefully and inform the user if any issues arise during your operations.
""",
        )
        # Add tools
        self.agent.add_tool(self.drive_manager.list_files_in_folder)
        self.agent.add_tool(self.drive_manager.upload_file_to_folder)
        self.agent.add_tool(self.drive_manager.download_file)
        self.agent.add_tool(self.drive_manager.delete_file)

        # Tool metadata
        self.tool_metadata = {
            "list_files_in_folder": {
                "input_model": ListFilesInFolderInput,
                "output_model": ListFilesInFolderOutput,
            },
            "upload_file": {
                "input_model": UploadFileInput,
                "output_model": UploadFileOutput,
            },
            "download_file": {
                "input_model": DownloadFileInput,
                "output_model": DownloadFileOutput,
            },
            "delete_file": {
                "input_model": DeleteFileInput,
                "output_model": DeleteFileOutput,
            },
        }

    def list_files_in_folder(self, input_data: ListFilesInFolderInput) -> ListFilesInFolderOutput:
        """
        List files in a specific folder
        """
        try:
            folder_id = input_data.folder_id
            max_results = input_data.max_results
            query = f"'{folder_id}' in parents"
            results = self.drive_manager.service.files().list(
                q=query, pageSize=max_results, fields="files(id, name)"
            ).execute()
            files = results.get("files", [])
            return ListFilesInFolderOutput(files=files)
        except Exception as e:
            raise ValueError(f"Error listing files in folder: {str(e)}")

    def upload_file(self, input_data: UploadFileInput) -> UploadFileOutput:
        """
        Upload a file to a specific folder
        """
        try:
            folder_id = input_data.folder_id
            file_path = input_data.file_path
            if not os.path.exists(file_path):
                raise ValueError(f"File {file_path} does not exist.")
            file_metadata = {"name": os.path.basename(file_path), "parents": [folder_id]}
            media = MediaFileUpload(file_path, mimetype="text/plain")
            file = self.drive_manager.service.files().create(
                body=file_metadata, media_body=media, fields="id"
            ).execute()
            return UploadFileOutput(success=True, message="File uploaded successfully.", file_id=file.get("id"))
        except Exception as e:
            raise ValueError(f"Error uploading file: {str(e)}")

    def download_file(self, input_data: DownloadFileInput) -> DownloadFileOutput:
        """
        Download a file from Google Drive
        """
        try:
            file_id = input_data.file_id
            destination_path = input_data.destination_path
            request = self.drive_manager.service.files().get_media(fileId=file_id)
            fh = io.BytesIO()
            downloader = MediaIoBaseDownload(fh, request)
            done = False
            while not done:
                status, done = downloader.next_chunk()
            with open(destination_path, "wb") as f:
                fh.seek(0)
                f.write(fh.read())
            return DownloadFileOutput(success=True, message=f"File downloaded to {destination_path}.")
        except Exception as e:
            raise ValueError(f"Error downloading file: {str(e)}")

    def delete_file(self, input_data: DeleteFileInput) -> DeleteFileOutput:
        """
        Delete a file from Google Drive
        """
        try:
            file_id = input_data.file_id
            self.drive_manager.service.files().delete(fileId=file_id).execute()
            return DeleteFileOutput(success=True, message=f"File with ID {file_id} has been deleted.")
        except Exception as e:
            raise ValueError(f"Error deleting file: {str(e)}")

    def chat(self, query: str) -> str:
        """
        Process natural language queries
        """
        try:
            return self.agent.interact_with_model(query)
        except Exception as e:
            return f"Error processing query: {str(e)}"

if __name__ == "__main__":
    # Initialize GoogleDriveAgent
    drive_agent = GoogleDriveAgent(model_type="ollama")
    print("Google Drive AI Agent initialized. Type 'quit' to exit.")
    while True:
        # Prompt user for input
        user_input = input("\nEnter your query (or type 'quit' to exit): ").strip()
        if user_input.lower() == "quit":
            print("Exiting Google Drive AI Agent. Goodbye!")
            break
        if not user_input:
            print("Query cannot be empty. Please try again.")
            continue
        # Process the query
        try:
            response = drive_agent.chat(user_input)
            print(f"\nResponse: {response}")
        except Exception as e:
            print(f"\nError processing query: {str(e)}")