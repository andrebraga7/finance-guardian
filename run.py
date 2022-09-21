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

    print(70*"_")
    print("\n Welcome to Finance Guardian!\n")
    print(" Your personal budgeting app. \n")
    print(70*"-")


def username_input():
    """
    Get the username from the user and verify if it already exists.
    If it doesn't, give the user and option to create a new username.
    """

    while True:
        print("\nPlease enter your username to begin.\n")
        print("You can create a new one by entering it below.")
        print("It must only contain letters and or numbers")
        print("and be 5 to 10 characters long.\n")

        username = input("Username: ")

        if validate_username(username):
            print("Valid username\n")
            break

    return username


def validate_username(username):
    """
    Validate the username input to check if it contains only letters
    and or numbers, and has between 5 and 10 characters.
    """

    try:

        if not username.isalnum():
            raise ValueError(
                "You must only use letters and or numbers for your username."
            )

        if len(username) < 5 or len(username) > 10:
            raise ValueError(
                "Your username must be between 5 and 10 characters long."
            )

    except ValueError as e:
        print(f"Invalid data: {e}\nPlease try again.\n")
        return False

    return True


def load_username(username):
    """
    Check if the input username exists in the worksheet and if not,
    give the user an option to create a new one.
    """

    users = SHEET.worksheet("users")
    find_user = users.find(username)

    if find_user is not None:
        name = users.cell(find_user.row, 3).value
    else:
        print(f"Username {username} not found!")
        option = input("Would you like to create a new username? Y/N ")
        return option

    return name


def main():
    """
    Run all programm functions.
    """
    username = username_input()
    name = load_username(username)
    print(f"Welcome {name}")


welcome_message()
main()
