import gspread
from google.oauth2.service_account import Credentials

SCOPE = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive.file",
    "https://www.googleapis.com/auth/drive"
    ]

CREDS = Credentials.from_service_account_file('creds.json')
SCOPED_CREDS = CREDS.with_scopes(SCOPE)
GSPREAD_CLIENT = gspread.authorize(SCOPED_CREDS)
SHEET = GSPREAD_CLIENT.open('finance_guardian')


def welcome_message():
    """
    This will generate an opening welcome message to the user.
    """

    print(50*"_")
    print("\n Welcome to Finance Guardian!\n")
    print(" Your personal budgeting app. \n")
    print(50*"-")


def username_input():
    """
    Get the username from the user and verify if it already exists.
    If it doesn't, give the user and option to create a new username.
    """

    print("\nPlease enter your username to begin.")
    print("You can create a new one by entering it below.")
    print("It must only contain letters and be 5 to 10 characters long.\n")

    username = input("Username: ")
    
    if validate_username(username):
        print("Valid")
    else:
        print("Invalid")


def validate_username(username):
    """
    Validate the username input to check if it contains only letters
    and has between 5 and 10 characters.
    """
    try:

        if username.isalpha() == False:
            raise ValueError(
                "You must only use letters for your username."
            )

        if len(username) < 5 or len(username) > 10:
            raise ValueError(
                "Your username must be between 5 and 10 characters long."
            )

    except ValueError as e:
        print(f"Invalid data: {e}\nPlease try again.\n")
        return False

    return True


def main():
    """
    Run all programm functions.
    """
    username = username_input()
    print(username)


welcome_message()
username_input()