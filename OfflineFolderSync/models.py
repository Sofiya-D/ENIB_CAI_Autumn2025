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
    
    ### Update a folder's local_path and/or usb_path
    def update_folder_paths(self, foldername, local_path=None, usb_path=None):
        with self.connection:
            if local_path is not None and usb_path is not None:
                self.connection.execute("""
                    UPDATE synced_folders 
                    SET local_path = ?, usb_path = ?, last_update = ? 
                    WHERE foldername = ?
                """, (local_path, usb_path, datetime.now().isoformat(), foldername))
            elif local_path is not None:
                self.connection.execute("""
                    UPDATE synced_folders 
                    SET local_path = ?, last_update = ? 
                    WHERE foldername = ?
                """, (local_path, datetime.now().isoformat(), foldername))
            elif usb_path is not None:
                self.connection.execute("""
                    UPDATE synced_folders 
                    SET usb_path = ?, last_update = ? 
                    WHERE foldername = ?
                """, (usb_path, datetime.now().isoformat(), foldername))
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


                # CREATE TABLE IF NOT EXISTS synced_files (
                #     id INTEGER PRIMARY KEY,
                #     filename TEXT NOT NULL,
                #     status TEXT NOT NULL,
                #     last_update TEXT NOT NULL,
                #     hash TEXT NOT NULL,
                #     path TEXT NOT NULL
                # )



# TESTING
if __name__ == "__main__":

    # Create a test instance
    repo = RepoModel("offline_filesync_test.db")

    crud=input("choose CRUD (C,R,U,D) : ")

    match crud.upper():

        case "C": # Add a folder to track
            foldername = input("Enter folder name: ")
            status = input("Enter status: ")
            hash = input("Enter hash: ")
            local_path = input("Enter local path: ")
            usb_path = input("Enter USB path: ")
            repo.add_folder(foldername, status, hash, local_path, usb_path)
            print(f"Folder '{foldername}' added.")

        case "R": # Read all folders
            folders = repo.get_all_folders()
            print(f"Folders: {folders}")

        case "U": # Update folder status
            foldername = input("Enter folder name to update: ")
            status = input("Enter new status: ")
            repo.update_folder_status(foldername, status)
            repo.update_folder_paths(foldername, local_path="/new/local/path", usb_path="/new/usb/path")
            print(f"Folder '{foldername}' updated to status '{status}'.")

        case "D": # Delete a folder
            foldername = input("Enter folder name to delete: ")
            repo.remove_folder(foldername)
            print(f"Folder '{foldername}' removed.")

        case _: 
            print("Invalid choice.")