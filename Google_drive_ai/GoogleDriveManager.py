import os
import os.path
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload
from dotenv import load_dotenv
import io

# Load environment variables from .env file
load_dotenv()

class GoogleDriveManager:
    """
    A class to manage Google Drive operations like listing, uploading, downloading, and deleting files.
    """
    SCOPES = ['https://www.googleapis.com/auth/drive']
    
    def __init__(self):
        self.service = self.authenticate()
    
    def authenticate(self):
        """Authenticate and return the Drive service."""
        creds = None
        if os.path.exists('token.json'):
            creds = Credentials.from_authorized_user_file('token.json', self.SCOPES)
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                client_id = os.getenv('GOOGLE_CLIENT_ID')
                client_secret = os.getenv('GOOGLE_CLIENT_SECRET')
                redirect_uri = os.getenv('GOOGLE_REDIRECT_URI')
                client_config = {
                    "installed": {
                        "client_id": client_id,
                        "client_secret": client_secret,
                        "redirect_uris": [redirect_uri],
                        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                        "token_uri": "https://oauth2.googleapis.com/token"
                    }
                }
                flow = InstalledAppFlow.from_client_config(client_config, self.SCOPES)
                creds = flow.run_local_server(port=0)
            with open('token.json', 'w') as token:
                token.write(creds.to_json())
        service = build('drive', 'v3', credentials=creds)
        return service
    
    def list_files(self):
        """List all files in Google Drive."""
        results = self.service.files().list(pageSize=10, fields="nextPageToken, files(id, name)").execute()
        items = results.get('files', [])
        if not items:
            print('No files found.')
        else:
            print('Files:')
            for item in items:
                print(f"{item['name']} ({item['id']})")
    
    def list_files_in_folder(self, folder_id):
        """List all files in a specific folder."""
        query = f"'{folder_id}' in parents"
        results = self.service.files().list(q=query, fields="nextPageToken, files(id, name)").execute()
        items = results.get('files', [])
        if not items:
            print(f"No files found in folder with ID {folder_id}.")
        else:
            print(f"Files in folder with ID {folder_id}:")
            for item in items:
                print(f"{item['name']} ({item['id']})")
    
    def upload_file_to_folder(self, folder_id, file_path, mime_type='text/plain'):
        """Upload a file to a specific folder in Google Drive."""
        if not os.path.exists(file_path):
            print(f"File {file_path} does not exist.")
            return
        
        file_metadata = {
            'name': os.path.basename(file_path),
            'parents': [folder_id]  # Specify the folder ID where the file should be uploaded
        }
        
        media = MediaFileUpload(file_path, mimetype=mime_type)
        file = self.service.files().create(body=file_metadata, media_body=media, fields='id').execute()
        print(f"File ID: {file.get('id')} uploaded to folder with ID {folder_id}")
    
    def download_file(self, file_id, destination_path):
        """Download a file from Google Drive to the local machine."""
        request = self.service.files().get_media(fileId=file_id)
        fh = io.BytesIO()
        downloader = MediaIoBaseDownload(fh, request)
        done = False
        print("Downloading file...")
        while not done:
            status, done = downloader.next_chunk()
            print(f"Download progress: {int(status.progress() * 100)}%")
        
        # Write the downloaded content to the destination file
        with open(destination_path, 'wb') as f:
            fh.seek(0)
            f.write(fh.read())
        print(f"File downloaded to {destination_path}")
    
    def delete_file(self, file_id):
        """Delete a file from Google Drive."""
        try:
            self.service.files().delete(fileId=file_id).execute()
            print(f"File with ID {file_id} has been deleted.")
        except Exception as e:
            print(f"An error occurred while deleting the file: {e}")

if __name__ == '__main__':
    # Initialize the GoogleDriveManager
    drive_manager = GoogleDriveManager()
    
    # Get the directory of the current script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # List files in Google Drive
    print("Listing files...")
    drive_manager.list_files()
    
    # Folder ID of "AI_folder" (replace with your actual folder ID)
    AI_FOLDER_ID = '1hSuEPTn3vvIAJzNxLsEx-IZvzt1OqtOa'  # Use only the folder ID, not the full URL
    
    # List files in the AI_folder
    print("\nListing files in AI_folder...")
    drive_manager.list_files_in_folder(AI_FOLDER_ID)
    
    # Create a simple text file to upload
    file_to_upload = './example.txt'
    with open(file_to_upload, 'w') as f:
        f.write("This is a test file created by the Google Drive Manager script.")
    
    # Upload the file to the "AI_folder"
    print(f"\nUploading {file_to_upload} to AI_folder...")
    drive_manager.upload_file_to_folder(AI_FOLDER_ID, file_to_upload)
    
    # List files again to confirm the upload
    print("\nListing files in AI_folder after upload...")
    drive_manager.list_files_in_folder(AI_FOLDER_ID)
    
    # Download the uploaded file to the local machine
    file_id_to_download = '1axu1RO9jv2h1y9jzE4B4IkGdCFWG4urR'  # Replace with the actual file ID of the uploaded file
    destination_path = os.path.join(script_dir, 'downloaded_example.txt')  # Save in the script's directory
    print(f"\nDownloading file with ID {file_id_to_download} to {destination_path}...")
    drive_manager.download_file(file_id_to_download, destination_path)