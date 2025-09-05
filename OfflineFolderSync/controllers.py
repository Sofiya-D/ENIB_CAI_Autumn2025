class MainController:
    def __init__(self, model, view):
        self.model = model
        self.view = view

        # Initialisation
        self.refresh_view()

    def refresh_view(self):
        files = self.model.get_all_files()
        self.view.update_file_list(files)
        self.view.log("View updated.")
