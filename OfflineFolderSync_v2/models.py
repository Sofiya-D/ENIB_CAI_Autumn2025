# coding: utf-8
DEBUG=True



import os
import sqlite3


# OBSERVER PATTERN - SUBJECT
# Rôle d'un "observable" (Subject) :
# notifier ses modifications de propriétés (notify() )
# aux observers qui lui sont associés
class Subject(object):
    def __init__(self):
        self.observers=[]

    def notify(self):
        for obs in self.observers:
            obs.update(self)

    def attach(self,obs):
        if not callable(getattr(obs,"update")) :
            raise ValueError("Observer must have an update() method")
        self.observers.append(obs)

    def detach(self,obs):
        if obs in self.observers :
            self.observers.remove(obs)



class RepoModel(Subject):

    def __init__(self, 
                 db_filename = "Folder_Data.db", 
                 tablename = "tracked_folders"):
        super().__init__()
        self.__db_filename = db_filename if db_filename[-3:]==".db" else str(db_filename+".db")
        self.__db_filepath = self.__set_db_filepath(self.__db_filename) # private because path is relative to working dir & needs to be set properly
        self.__tablename = tablename
        self.__selected_folder = ""
        self.__local_folder = FolderModel()
        self.__remote_folder = FolderModel()
        
        self.initialize_folders_db()

    def notify(self):
        for obs in self.observers:
            obs.update(self)


    ## GETTERS & SETTERS

    def get_db_filename(self):
        return self.__db_filename
    

    def set_db_filename(self, db_filename):
        self.__db_filename = db_filename if db_filename[-3:]==".db" else str(db_filename+".db")
        self.__set_db_filepath(self.__db_filename)
        self.notify()


    def get_db_filepath(self):
        return self.__db_filepath


    def __set_db_filepath(self, db_filename):
        # Get the directory of the current script
        script_dir = os.path.dirname(os.path.abspath(__file__))
        path = os.path.join(script_dir, db_filename)
        self.__db_filepath = path
        self.notify()
        return path
    

    def get_tablename(self):
        return self.__tablename
    

    def set_tablename(self, tablename):
        self.__tablename = tablename
        self.notify()

    
    def get_selected_folder(self):
        return self.__selected_folder
    
    
    def set_selected_folder(self, new_folder_name):
        self.__selected_folder = new_folder_name
        if new_folder_name=="" or new_folder_name is None:
            self.__local_folder.set_path(None)
            self.__remote_folder.set_path(None)
            if DEBUG:
                print(f"Folder selection empty.")
                self.notify()
            return
        folder_data = self.get_folder_data(new_folder_name)[new_folder_name]
        if DEBUG:
            print(f"New folder data: {folder_data}")
        self.__local_folder.set_path(folder_data["local_path"])
        self.__remote_folder.set_path(folder_data["remote_path"])
        self.notify()
    

    def get_local_folder(self):
        return self.__local_folder


    def get_remote_folder(self):
        return self.__remote_folder

    

    ## CRUD: DATABASE MANIPULATION

    def initialize_folders_db(self, db_filepath=None, tablename=None):
        """
        Initialize the database for the app.  
        Looks for a file at 'filepath', otherwise creates it.  
        Looks for the table 'tablename' inside the file, otherwise creates it.  
        Defaults filepath and tablename are the attributes of the associated RepoModel instance.  
        """
        db_filepath = db_filepath if db_filepath else self.get_db_filepath()
        tablename = tablename if tablename else self.get_tablename()

        with sqlite3.connect(db_filepath) as connection:
                connection.execute(f"""
                    CREATE TABLE IF NOT EXISTS {tablename} (
                        id INTEGER PRIMARY KEY,
                        foldername TEXT NOT NULL,
                        local_path TEXT NOT NULL,
                        remote_path TEXT NOT NULL
                    )
                """)
                # TODO!(1) add folder-level sync status tracking:
                        # status TEXT NOT NULL,
                        # last_sync TEXT NOT NULL,
                        # local_hash TEXT NOT NULL,
                        # usb_hash TEXT NOT NULL,
        self.notify()
        return
    

    # CRUD - Create
    def add_new_folder_to_db(self, foldername, local_path, remote_path, db_filepath=None, tablename=None):
        """
        Inserts a new folder in the database.  
        """
        # TODO! if foldername already present, raise error (to warn user & prompt new name)
        # Check if paths are valid
        local_path = os.path.dirname(local_path.rstrip("\\/")) if not os.path.isdir(local_path) else local_path
        if not os.path.exists(local_path):
            raise ValueError("Local directory not found.")
        
        remote_path = os.path.dirname(remote_path.rstrip("\\/")) if not os.path.isdir(remote_path) else remote_path
        if not os.path.exists(local_path):
            raise ValueError("Remote directory not found.")
        
        # initialize tracking files
        # TODO!(1) initialize tracking files at folder init
        # to allow folder-level sync tracking
        # for path in (local_path, remote_path):
        #     try:
        #         initialize_tracking_files(
        # os.path.join(path, "offline_filesync_data.db")
        # )
        #     except Exception as e:
        #         raise RuntimeError(f"Error initializing tracking file in {path}: {e}")
            
        # Add to DB
        db_filepath = db_filepath if db_filepath else self.get_db_filepath()
        tablename = tablename if tablename else self.get_tablename()
        with sqlite3.connect(db_filepath) as connection:
            connection.execute(f"""
                INSERT INTO {tablename} (
                                    foldername, 
                                    local_path, 
                                    remote_path)
                VALUES (?, ?, ?)
            """, (foldername, local_path, remote_path))
        self.notify()
        return


    # CRUD - Read
    def get_folder_data(self, foldername=None, db_filepath=None, tablename=None):
        """
        Get the data for a specified folder.  
        If no folder is specified, returns all folders data.  
        Defaults filepath and tablename are the attributes of the associated RepoModel instance.  
        Returns a dict containing folder data
        """
        db_filepath = db_filepath if db_filepath else self.get_db_filepath()
        tablename = tablename if tablename else self.get_tablename()
        folder_data={}
        sql = f"SELECT * FROM {tablename}"
        params = ()
        if foldername:
            sql += " WHERE foldername = ?"
            params = (foldername,)
        with sqlite3.connect(db_filepath) as connection:
            cursor = connection.execute(sql, params)
            folder_data = {row[1]: { # <- foldername
                                "local_path": row[2],
                                "remote_path": row[3]
                                } for row in cursor.fetchall()}
        return folder_data
    

    # CRUD - Read
    def get_foldernames_list(self, db_filepath=None, tablename=None):
        """
        Get the list of tracked folders from the database.
        """
        db_filepath = db_filepath if db_filepath else self.get_db_filepath()
        tablename = tablename if tablename else self.get_tablename()
        folderlist = []
        with sqlite3.connect(db_filepath) as connection:
            cursor = connection.execute(f"SELECT foldername FROM {tablename}")
            folderlist = [row[0] for row in cursor.fetchall()]
        return folderlist
    

    def get_local_path(self, foldername, db_filepath=None, tablename=None):
        db_filepath = db_filepath if db_filepath else self.get_db_filepath()
        tablename = tablename if tablename else self.get_tablename()
        path = None
        with sqlite3.connect(db_filepath) as connection:
            cursor = connection.execute(f"SELECT local_path FROM {tablename} WHERE foldername = ? ", (foldername,))
            path = cursor.fetchall()
        return path


    def get_remote_path(self, foldername, db_filepath=None, tablename=None):
        db_filepath = db_filepath if db_filepath else self.get_db_filepath()
        tablename = tablename if tablename else self.get_tablename()
        path = None
        with sqlite3.connect(db_filepath) as connection:
            cursor = connection.execute(f"SELECT remote_path FROM {tablename} WHERE foldername = ? ", (foldername,))
            path = cursor.fetchall()
        return path
        

    # CRUD - Update
    def set_folder_data(self, foldername, local_path=None, remote_path=None, new_name=None, db_filepath=None, tablename=None):
        """
        Uptade the data of a folder in the database.  
        """
        fields = []
        values = []
        if new_name is not None:
            fields.append("foldername = ?")
            values.append(new_name)
        if local_path is not None:
            local_path = os.path.dirname(local_path.rstrip("\\/")) if not os.path.isdir(local_path) else local_path
            if not os.path.exists(local_path):
                raise ValueError("Local directory not found.")
            fields.append("local_path = ?")
            values.append(local_path)
        if remote_path is not None:
            remote_path = os.path.dirname(remote_path.rstrip("\\/")) if not os.path.isdir(remote_path) else remote_path
            if not os.path.exists(local_path):
                raise ValueError("Remote directory not found.")
            fields.append("remote_path = ?")
            values.append(remote_path)
        db_filepath = db_filepath if db_filepath else self.get_db_filepath()
        tablename = tablename if tablename else self.get_tablename()
        with sqlite3.connect(db_filepath) as connection:
            if fields:
                values.append(foldername)
                sql = f"UPDATE {tablename} SET {', '.join(fields)} WHERE foldername = ?"
                connection.execute(sql, tuple(values))
        self.notify()
        return
    
    
    # CRUD - Update
    def set_folders_data(self, data_dict):
        """
        Not implemented yet.  
        Set data for several folders at once.  
        """
        # TODO!(1)
        # To set data for several folders at once.
        # Not crucial yet.
        raise NotImplementedError
        self.notify()
        return
        
    # CRUD - Delete
    def remove_folder_from_db(self, foldername, 
                              delete_tracking_files=True,  
                              db_filepath=None, 
                              tablename=None):
        """
        Remove a folder from tracking.
        TODO: Deleting the tracking files in local and usb folders.
        """
        # delete_tracking_files(foldername)
        # Remove folder from DB
        db_filepath = db_filepath if db_filepath else self.get_db_filepath()
        tablename = tablename if tablename else self.get_tablename()
        with sqlite3.connect(db_filepath) as connection:
            connection.execute(f"""
                DELETE FROM {tablename} WHERE foldername = ?
            """, (foldername,))
        self.notify()
        return


class FolderModel:
    def __init__(self, path=None):
        self.__path = path
        # TODO!(1) Add folder state
        pass
    
    def get_path(self):
        return self.__path

    def set_path(self, new_path):
        self.__path = new_path

    def scan_folder(self):
        # TODO!(0)
        # TODO!(1) Add folder state, and update it when scanning
        pass

    def initialize_tracking_file(self, path):
        """
        Not implemented yet.  
        """
        # TODO!(0)
        # Check if it exists
        # If not then create it
        raise NotImplementedError
    
    def delete_tracking_file(self, path):
        """
        Not implemented yet.  
        """
        # TODO!(0)
        raise NotImplementedError


if __name__ == "__main__":
    print()
    print(">> Testing models.py <<")

    test_model = RepoModel(db_filename="test", tablename="test")
    print(f"database filename: {test_model.get_db_filename()}")
    print(f"database filepath: {test_model.get_db_filepath()}")
    print(f"database table name : {test_model.get_tablename()}")
    test = True

    while test:
        choice = input(f"Choose a 'CRUD' test:")
        match choice.upper():

            case "C":
                print(f"Data creation scenario:")
                print(f"Adding a folder to the database.")
                print(f"Database: {test_model.get_folder_data()}")
                localpath = input(f"type local path: ")
                remotepath = input(f"type remote path: ")
                foldername = input(f"name your folder: ")
                test_model.add_new_folder_to_db(foldername=foldername,
                                                local_path=localpath,
                                                remote_path=remotepath)
                print(f"Added folder: {test_model.get_folder_data(foldername=foldername)}")

            case "R":
                print(f"Data reading scenario:")
                print(f"Reading folder data.")
                foldername = input(f"Type the name of the folder of which you want the data: (type * to get all folders data)")
                if foldername=="*":
                    foldername=None
                print(test_model.get_folder_data(foldername=foldername))

            case "U":
                print(f"Data updating scenario:")
                print(f"Updating folder name or paths.")
                print(f"Leave any field blank to keep unchanged")
                foldername = input(f"Type the name of the folder you want to update:")
                print(f"Current data: {test_model.get_folder_data(foldername=foldername)}")
                new_name = input(f"New name? ")
                new_local = input(f"New local path? ")
                new_remote = input(f"New remote path? ")
                if new_name=="":
                    new_name=None
                if new_local=="":
                    new_local=None
                if new_remote=="":
                    new_remote=None
                test_model.set_folder_data(foldername=foldername,
                                           local_path=new_local,
                                           remote_path=new_remote,
                                           new_name=new_name)
                # foldername = new_name if new_name else foldername
                print(f"New data: {test_model.get_folder_data(foldername=(new_name if new_name else foldername))}")

            case "D":
                print(f"Data deletion scenario:")
                print(f"Removing a folder from the database")
                print(f"Database: {test_model.get_folder_data()}")
                foldername = input(f"Type the name of the folder you want to delete: ")
                test_model.remove_folder_from_db(foldername=foldername)
                print(f"Database: {test_model.get_folder_data()}")

            case "R_LIST":
                test_model.get_foldernames_list()
            case "SELECTED_FOLDER":
                selected_folder = input(f"Choose selected_folder: ")
                test_model.set_selected_folder(selected_folder)
            case _ :
                print("Unknown choice, please retry.")

        test = input(f"keep testing? (y/n)").upper() == "Y"


### NOTES ###

# CRUD:
# C = sauvegarde des données
# R = chargement des données
# U = mises à jour des données
# D = suppression des données