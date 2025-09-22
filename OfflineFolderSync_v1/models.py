# models.py
# For managing data
# Here it means: data about files and their sync status
# Uses SQLite database to store information locally

import hashlib
import sqlite3
from datetime import datetime
import os

filename = "offline_filesync_data.db"

# ----- FOLDER-LEVEL OPERATIONS -----
class RepoModel:

    def __init__(self, db_file="offline_filesync_repo.db"):
        self.db_file = db_file
        self.connection = sqlite3.connect(self.db_file)
        self.folders_data = {}  # Initialize data dictionary
        self.load_folderlist()  # Load existing data on initialization

    def close(self):
        if self.connection:
            self.connection.close()


    def create_folders_db(self):
        with self.connection:
            self.connection.execute("""
                CREATE TABLE IF NOT EXISTS tracked_folders (
                    id INTEGER PRIMARY KEY,
                    foldername TEXT NOT NULL,
                    status TEXT NOT NULL,
                    last_sync TEXT NOT NULL,
                    local_hash TEXT NOT NULL,
                    usb_hash TEXT NOT NULL,
                    local_path TEXT NOT NULL,
                    usb_path TEXT NOT NULL
                )
            """) # nb - possible statuses: 'synced', 'local_modified', 'usb_modified', 'conflict'


    def load_folderlist(self):
        """
        Load the folder list from the database into memory.
        if the folders table doesn't exist, it will be created by create_folders_table()
        """
        self.create_folders_db() # Ensure table exists
        with self.connection:
            cursor = self.connection.execute("SELECT * FROM tracked_folders")
            self.folders_data = {row[1]: { # <- foldername
                                  "status": row[2], 
                                  "last_sync": row[3], 
                                  "local_hash": row[4], 
                                  "usb_hash": row[5], 
                                  "local_path": row[6],
                                  "usb_path": row[7]
                                 } for row in cursor.fetchall()}


    def save_folderlist(self):
        """
        Force-save the current in-memory folder data to the database.
        This overwrites all folder records in the database with the current self.data.
        Useful for 'proof saving' before closing the app.
        """
        with self.connection:
            # Clear all existing records
            self.connection.execute("DELETE FROM tracked_folders")
            # Insert all current in-memory data
            for foldername, info in self.folders_data.items():
                self.connection.execute("""
                    INSERT INTO tracked_folders (foldername, status, last_sync, hash, local_path, usb_path)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    foldername,
                    info.get("status", "unknown"),
                    info.get("last_sync", datetime.now().isoformat()),
                    info.get("hash", ""),
                    info.get("local_path", ""),
                    info.get("usb_path", "")
                ))
        self.load_folderlist()
    

    def add_folder_to_db(self, 
                         foldername, 
                         status, 
                        #  local_hash, 
                        #  usb_hash, 
                         local_path, 
                         usb_path):
        """
        Add a new folder to track with its initial state.
        Only if both local and USB parent directories exist.
        Computes hash of folder contents for initial state.
        """
        # Check it paths are valid
        local_parent = os.path.dirname(local_path.rstrip("\\/")) if not os.path.isdir(local_path) else local_path
        usb_parent = os.path.dirname(usb_path.rstrip("\\/")) if not os.path.isdir(usb_path) else usb_path
        if not (os.path.exists(local_parent) and os.path.exists(usb_parent)):
            raise ValueError("One or both parent directories do not exist.")
        # initialize tracking files
        for path in (local_path, usb_path):
            try:
                self.initialize_files_tracking_table(os.path.join(path, "offline_filesync_data.db"))
            except Exception as e:
                raise RuntimeError(f"Error initializing tracking file in {path}: {e}")
        # scan folders to initialize tracking data
        self.scan_folder(local_path)
        self.scan_folder(usb_path)  
        # compute hashes
        local_hash = self.compute_folder_hash(local_path)
        usb_hash = self.compute_folder_hash(usb_path)
        # Add to DB
        with self.connection:
            self.connection.execute("""
                INSERT INTO tracked_folders (
                                    foldername, 
                                    status, 
                                    last_sync, 
                                    local_hash, 
                                    usb_hash, 
                                    local_path, 
                                    usb_path)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (foldername, status, datetime.now().isoformat(), local_hash, usb_hash, local_path, usb_path))
        self.load_folderlist()


    def remove_folder_from_db(self, foldername):
        """
        Remove a folder from tracking.
        Deletes the tracking files in local and usb folders.
        """
        self.delete_tracking_files(foldername)
        # Remove folder from DB
        with self.connection:
            self.connection.execute("""
                DELETE FROM tracked_folders WHERE foldername = ?
            """, (foldername,))
        self.load_folderlist()


    def delete_tracking_files(self, foldername):
        """
        Deletes the tracking files in local and usb folders for a given foldername.
        Does not remove the folder from the database.
        """
        info = self.get_folder_data(foldername)
        local_db = None
        usb_db = None
        if info:
            local_db = os.path.join(info.get('local_path', ''), "offline_filesync_data.db")
            usb_db = os.path.join(info.get('usb_path', ''), "offline_filesync_data.db")
        # Delete tracking files if they exist
        for db_path in (local_db, usb_db):
            if db_path and os.path.exists(db_path):
                try:
                    os.remove(db_path)
                except Exception as e:
                    raise OSError(f"Could not delete tracking file {db_path}: {e}")


    def set_folder_data(self, foldername, newname=None, status=None, local_hash=None, usb_hash=None, local_path=None, usb_path=None):
        """Update fields of a folder. Only non-None fields are updated."""
        with self.connection:
            fields = []
            values = []
            if newname is not None:
                fields.append("foldername = ?")
                values.append(newname)
            if status is not None:
                fields.append("status = ?")
                values.append(status)
            if local_hash is not None:
                fields.append("local_hash = ?")
                values.append(local_hash)
            if usb_hash is not None:
                fields.append("usb_hash = ?")
                values.append(usb_hash)
            if local_path is not None:
                fields.append("local_path = ?")
                values.append(local_path)
            if usb_path is not None:
                fields.append("usb_path = ?")
                values.append(usb_path)
            if fields:
                fields.append("last_sync = ?")
                values.append(datetime.now().isoformat())
                values.append(foldername)
                sql = f"UPDATE tracked_folders SET {', '.join(fields)} WHERE foldername = ?"
                self.connection.execute(sql, tuple(values))
        self.load_folderlist()


    def get_all_folders_data(self):
        self.load_folderlist()
        """Return the current in-memory folder data."""
        return self.folders_data


    def get_folder_data(self, foldername):
        self.load_folderlist()
        """Return data for a specific folder."""
        return self.folders_data.get(foldername, None)


    def compute_folder_hash(self, folder_path):
        """
        Compute the hash of the folder contents.
        """
        tracking_data = self.get_files_tracking_data(os.path.join(folder_path, "offline_filesync_data.db"))
        folder_hash = hashlib.sha256()
        for filename in sorted(tracking_data.keys()):
            file_hash = tracking_data[filename]['hash']
            entry = f"{filename}:{file_hash}"
            folder_hash.update(entry.encode())
        return folder_hash.hexdigest()

    def scan_folder(self, folder_path):
        """
        Scan folder content and update the tracking file
        """
        old_data = self.get_files_tracking_data(os.path.join(folder_path, "offline_filesync_data.db"))
        # scan current folder content
        new_data = {}
        dir = os.scandir(folder_path)
        for entry in dir:
            if entry.is_file():
                filename = entry.name
                file_hash = None
                try:
                    file_hash = self.compute_file_hash(entry.path)
                    if not file_hash:
                        raise ValueError("Hash computation failed")
                    status = "new"
                except Exception as e:
                    print(f"Error computing hash for {entry.path}: {e}")
                    file_hash = None
                    status = "error"
                new_data[filename] = {
                    "status": status,
                    "last_sync": datetime.now().isoformat(),
                    "hash": file_hash
                }
        # Compare old_data and new_data to determine statuses
        for filename, info in new_data.items():
            if filename in old_data:
                info["last_sync"] = old_data[filename]["last_sync"]
                if info["hash"] == old_data[filename]["hash"]:
                    info["status"] = "synced"
                else:
                    info["status"] = "modified"
            else:
                info["status"] = "new"
        for filename, info in old_data.items():
            # if old_data is 'deleted' then don't add it to new_data
            if info["status"] == "deleted":
                continue
            if filename not in new_data:
                new_data[filename] = {
                    "status": "deleted",
                    "last_sync": info["last_sync"],
                    "hash": info["hash"]
                }
        # Save new_data back to tracking file
        self.save_files_tracking_data(os.path.join(folder_path, "offline_filesync_data.db"), new_data)


    def initialize_files_tracking_table(self, file_path):
        """
        Check if the tracking file exists in the given path.
        If not, create it.
        """
        if not os.path.exists(file_path): # check if file does not already exist
            print(f"Opening connection to {file_path} for initialization")
            with sqlite3.connect(file_path) as conn:
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS tracked_files (
                        id INTEGER PRIMARY KEY,
                        filename TEXT NOT NULL,
                        status TEXT NOT NULL,
                        last_sync TEXT NOT NULL,
                        hash TEXT NOT NULL
                    )
                """)
            print(f"Closed connection to {file_path}")


    def get_files_tracking_data(self, file_path):
        """
        Get the files tracking data from the given tracking file.
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Tracking file {file_path} does not exist.")
        print(f"Opening connection to {file_path} for reading")
        with sqlite3.connect(file_path) as conn:
            cursor = conn.execute("SELECT * FROM tracked_files")
            data = {row[1]: { # <- filename
                                  "status": row[2], 
                                  "last_sync": row[3],
                                  "hash": row[4]
                                 } for row in cursor.fetchall()}
        print(f"Closed connection to {file_path}")
        return data


    def save_files_tracking_data(self, file_path, data):
        """
        Save the given files tracking data to the specified tracking file.
        Overwrites existing data.
        """
        print(f"Opening connection to {file_path} for writing")
        with sqlite3.connect(file_path) as conn:
            conn.execute("DELETE FROM tracked_files")
            for filename, info in data.items():
                conn.execute("""
                    INSERT INTO tracked_files (filename, status, last_sync, hash)
                    VALUES (?, ?, ?, ?)
                """, (
                    filename,
                    info.get("status", "unknown"),
                    info.get("last_sync", datetime.now().isoformat()),
                    info.get("hash", "")
                ))
        print(f"Closed connection to {file_path}")


    def compute_file_hash(self, file_path):
        """
        Compute SHA256 hash of a file.
        """
        sha256 = hashlib.sha256()
        try:
            with open(file_path, "rb") as f:
                while chunk := f.read(8192):
                    sha256.update(chunk)
                hash = sha256.hexdigest()
            return hash
        except Exception as e:
            print(f"Error computing hash for {file_path}: {e}")
            return ""
    

# ----- TESTING -----

if __name__ == "__main__":

    # Create a test instance
    repo = RepoModel(db_file = "offline_filesync_repo.db")

    crud = input("choose CRUD (C,R,U,D) : ")

    match crud.upper():
        case "C": # Add a folder to track
            foldername = input("Enter folder name: ")
            status = 'synced'  # or 'modified', etc.
            local_path = input("Enter local path: ")
            usb_path = input("Enter USB path: ")
            try:
                repo.add_folder_to_db(foldername, status, local_path, usb_path)
                print(f"Folder '{foldername}' added.")
            except Exception as e:
                print(f"Error: {e}")

        case "R": # Read all folders
            folders = repo.get_all_folders_data()
            print(f"Folders: {folders}")

        case "U": # Update folder data
            foldername = input("Enter folder name to update: ")
            status = input("Enter new status (or leave blank): ")
            local_path = input("Enter new local path (or leave blank): ")
            usb_path = input("Enter new USB path (or leave blank): ")
            kwargs = {}
            if status:
                kwargs['status'] = status
            if local_path:
                kwargs['local_path'] = local_path
            if usb_path:
                kwargs['usb_path'] = usb_path
            repo.set_folder_data(foldername, **kwargs)
            print(f"Folder '{foldername}' updated.")

        case "D": # Delete a folder
            foldername = input("Enter folder name to delete: ")
            try:
                repo.remove_folder_from_db(foldername)
                print(f"Folder '{foldername}' removed.")
            except Exception as e:
                print(f"Error: {e}")

        case _:
            print("Invalid choice.")