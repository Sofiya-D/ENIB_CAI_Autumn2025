# models.py
# For managing data
# Here it means: data about files and their sync status
# Uses JSON to store information locally


import json
import os
from datetime import datetime


class RepoModel:
    def __init__(self, repo_file="repo.json"):
        self.repo_file = repo_file
        self.data = {}
        self.load()

    def load(self):
        if os.path.exists(self.repo_file):
            with open(self.repo_file, "r") as f:
                self.data = json.load(f)
        else:
            self.data = {}

    def save(self):
        with open(self.repo_file, "w") as f:
            json.dump(self.data, f, indent=2)

    def update_file(self, filename, status):
        """Met à jour l'état d'un fichier (status = 'synced', 'modified', etc.)"""
        self.data[filename] = {
            "status": status,
            "last_update": datetime.now().isoformat()
        }
        self.save()

    def get_all_files(self):
        return self.data
