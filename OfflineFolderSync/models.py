# models.py
# For managing data
# Here it means: data about files and their sync status
# Uses SQLite database to store information locally

import sqlite3
from datetime import datetime


class RepoModel:
    def __init__(self, db_file="offline_filesync_repo.db"):
        self.db_file = db_file
        self.connection = sqlite3.connect(self.db_file)
        self.data = {}  # Initialize data dictionary
        self.create_table()
        self.load_folderlist()  # Load existing data on initialization
    
    # FOLDER-LEVEL OPERATIONS

    def create_table(self):
        with self.connection:
            self.connection.execute("""
                CREATE TABLE IF NOT EXISTS synced_folders (
                    id INTEGER PRIMARY KEY,
                    foldername TEXT NOT NULL,
                    status TEXT NOT NULL,
                    last_update TEXT NOT NULL,
                    hash TEXT NOT NULL,
                    local_path TEXT NOT NULL,
                    usb_path TEXT NOT NULL
                )
            """)
                # CREATE TABLE IF NOT EXISTS synced_files (
                #     id INTEGER PRIMARY KEY,
                #     filename TEXT NOT NULL,
                #     status TEXT NOT NULL,
                #     last_update TEXT NOT NULL,
                #     hash TEXT NOT NULL,
                #     path TEXT NOT NULL
                # )
    
    
    ### Load the folders' sync status from the database
    def load_folderlist(self):
        with self.connection:
            cursor = self.connection.execute("SELECT * FROM synced_folders")
            self.data = {row[1]: { # <- foldername
                                  "status": row[2], 
                                  "last_update": row[3], 
                                  "hash": row[4], 
                                  "local_path": row[5],
                                  "usb_path": row[6]
                                 } for row in cursor.fetchall()}
            
    # Save the current folder list to the database
    def save_folderlist(self):
        """
        Force-save the current in-memory folder data to the database.
        This overwrites all folder records in the database with the current self.data.
        Useful for 'proof saving' before closing the app.
        """
        with self.connection:
            # Clear all existing records
            self.connection.execute("DELETE FROM synced_folders")
            # Insert all current in-memory data
            for foldername, info in self.data.items():
                self.connection.execute("""
                    INSERT INTO synced_folders (foldername, status, last_update, hash, local_path, usb_path)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    foldername,
                    info.get("status", "unknown"),
                    info.get("last_update", datetime.now().isoformat()),
                    info.get("hash", ""),
                    info.get("local_path", ""),
                    info.get("usb_path", "")
                ))
        self.load_folderlist()
            
    # TODO: evaluate synced status; should be done at initialization and after each sync
    # TODO: there should be a synced_files table at the top of the folder to track the status inside the folder
    ### Add a folder to track with its initial state
    def add_folder(self, foldername, status, hash, local_path, usb_path):
        with self.connection:
            self.connection.execute("""
                INSERT INTO synced_folders (foldername, status, last_update, hash, local_path, usb_path)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (foldername, status, datetime.now().isoformat(), hash, local_path, usb_path))
        self.load_folderlist()

    ### Remove a folder from tracking
    def remove_folder(self, foldername):
        with self.connection:
            self.connection.execute("""
                DELETE FROM synced_folders WHERE foldername = ?
            """, (foldername,))
        self.load_folderlist()

    ### Update a folder's state (status = 'synced', 'modified', etc.)
    def update_folder_status(self, foldername, status):
        with self.connection:
            self.connection.execute("""
                UPDATE synced_folders 
                SET status = ?, last_update = ? 
                WHERE foldername = ?
            """, (status, datetime.now().isoformat(), foldername))
        self.load_folderlist()

    ### Get all tracked folders and their statuses
    def get_all_folders(self):
        return self.data
    
    ### FILE-LEVEL OPERATIONS
    # TODO

    # def update_file(self, filename, status):
    #     """Update a file's state (status = 'synced', 'modified', etc.)"""
    #     # Note: This method updates in-memory data only since there's no synced_files table
    #     # Consider implementing a synced_files table if file-level tracking is needed
    #     if hasattr(self, 'data'):
    #         self.data[filename] = {
    #             "status": status,
    #             "last_update": datetime.now().isoformat()
    #         }


if __name__ == "__main__":
    # Simple test
    print(">>> Testing RepoModel...")
    
    # Create a test instance
    repo = RepoModel("offline_filesync_test.db")

    # Add a test folder
    repo.add_folder("TestFolder", "new", "hash123", "/home/test", "/usb/test")
    
    # Show all folders
    folders = repo.get_all_folders()
    print(f"Folders: {folders}")
    
    # Update status
    repo.update_folder_status("TestFolder", "synced")
    
    # Show updated data
    updated_folders = repo.get_all_folders()
    print(f"Updated: {updated_folders}")
    
    print("Test completed!")