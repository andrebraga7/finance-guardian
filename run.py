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
    Get the username from the user and validate.
    """

    while True:
        print("\nPlease enter your username to begin.\n")
        print("You can create a new one by entering it below.")
        print("It must only contain letters and or numbers")
        print("and be 5 to 10 characters long.\n")

        username = input("Username: ")

        if validate_username(username):
            print("Loading user data...\n")
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
    give the user an option to create a new one. If the user selects
    not to create a new one, it loops back to the username input.
    """

    while True:

        users = SHEET.worksheet("data")
        find_user = users.find(username)

        if find_user is not None:
            name = users.cell(find_user.row, 3).value
            user_id = users.cell(find_user.row, 1).value
            print("User data successfully loaded\n")
            break
        
        print(f"Username: {username} not found!\n")
        option = input("Would you like to create a new username? y/n\n")
            
        if option == "y":
            name, user_id = create_username(username)
            print("User data successfully loaded\n")
            break

        username = username_input()

    return name, user_id


def create_username(username):
    """
    Create a new username with a new user_id
    and generate a new blank worksheet.
    """

    while True:

        name = input("Please enter your first and last name:\n")

        if validate_letters_only(name):
            print("Creating user data...")
            break

    users_worksheet = SHEET.worksheet("data")

    # get the last number of the id column and add 1
    id_data = users_worksheet.col_values(1)
    user_id = int(id_data[-1]) + 1
    print(user_id)

    user_data = [user_id, username, name]
    users_worksheet.append_row(user_data)

    # create a new blank worksheet with the user_id
    blank_worksheet = SHEET.worksheet("blank")
    blank_worksheet.duplicate(new_sheet_name=f"{user_id}")

    print("User data successfully created.\n")

    return name, user_id


def validate_letters_only(data):
    """
    Validates is the input data is letters only.
    """

    try:
        if not all(cha.isalpha() or cha.isspace() for cha in data):
            raise ValueError(
                "You must only use letters and spaces."
            )
        
        if data.isspace() or len(data) == 0:
            raise ValueError(
                "This field cannot be empty."
            )

    except ValueError as e:
        print(f"Invalid data: {e}. Please try again.\n")
        return False

    return True


def new_budget(user_id):
    """
    Checks to see if the budget exists for the selected month
    and call the create_new_budget function.
    """

    user_worksheet = SHEET.worksheet(user_id)
    select_month(user_worksheet)


def select_month(user_worksheet):
    """
    Checks and selects the month the user would like to view.
    If it is empty, it alerts the user.
    """

    while True:
        # generate the list of month using th data worksheet
        months_worksheet = SHEET.worksheet("data")
        months = months_worksheet.col_values(4)

        print("0. Return to main menu")
        for month in months[1:]:
            print(month)

        selection = input("\nPlease select a month number: ")

        if validate_month(selection):
            if selection == "0":
                break
            else:
                col_num = int(selection) * 3
                column = user_worksheet.col_values(col_num)
                print(column[1:])


def validate_month(selection):
    """
    Validate the input from the month selection.
    """
    try:
        if int(selection) > 12:
            raise ValueError(
                "Invalid selection!"
            )
    except ValueError as e:
        print(f"Invalid data: {e} Please try again.\n")
        return False

    return True


def main():
    """
    Run all programm functions.
    """
    welcome_message()
    username = username_input()
    name, user_id = load_username(username)

    print(
        f"Welcome {name.title()}!\n"
        "Please select one of the options bellow:")
    
    while True:

        print(
            "\n1. New budget\n"
            "2. View budget\n"
            "3. Update budget\n"
            "4. Add transaction\n"
            "5. View transactions\n"
            "6. Log out\n")

        option = input("Your selections: ")

        if option == "1":
            new_budget(user_id)

        elif option == "2":
            print("View budget")

        elif option == "3":
            print("Update budget")

        elif option == "4":
            print("Add transaction")

        elif option == "5":
            print("View transactions")

        elif option == "6":
            print("Thank you for using Finance Guardian, good bye!")
            quit()

        else:
            print("Invalid option")


# main()
new_budget("1")