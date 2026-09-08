# Import the main app class from dictionary_app.py.
from dictionary_app import PersonalDictionaryApp


# This main guard means:
# only start the app when we run this file directly.
if __name__ == "__main__":
    # Create one app object from the class blueprint.
    app = PersonalDictionaryApp()

    # Start the menu loop.
    app.run()
