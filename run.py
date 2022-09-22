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

    # Title
    print(75 * "-")
    print("\nCreate new budget\n")
    print(75 * "-")

    user_wks = SHEET.worksheet(user_id)

    # function to allow the user to select a month and validate
    selection = select_month()

    # return the selection and analyse what was inputed
    if selection == "0":
        return
    
    col_num = int(selection) * 2
    month_income = user_wks.col_values(col_num)[-1]

    # check if a budget already exists
    if month_income != "0":
        print("A budget already exists.\n")
        option = input("Would you like to create a new one? y/n\n")

        if option == "n":
            return
        
    data = create_new_budget(user_wks)

    display_data(user_wks, data, col_num)

    save_data(user_wks, data, col_num)


def select_month():
    """
    Checks and selects the month the user would like to view.
    If it is empty, it alerts the user.
    """

    while True:
        print(
            "1. January"
            "2. February"
            "3. March"
            "4. April"
            "5. May"
            "6. June"
            "7. July"
            "8. August"
            "9. September"
            "10. October"
            "11. November"
            "12. December"
            "0. Return to main menu")

        selection = input("\nPlease select a month number: ")

        if validate_month(selection):
            return selection


def validate_month(selection):
    """
    Validate the input from the month selection.
    """
    try:
        if int(selection) > 12:
            raise ValueError(
                "Select a number from the list."
            )
    except ValueError as e:
        print(f"{e} Please try again.\n")
        return False

    return True


def create_new_budget(user_wks):
    """
    Creates a new budget and displays it to the user.
    """

    while True:

        income = input("\nPlease enter the income for the month: ")

        if income.replace(".", "", 1).isdigit():
            income = float(income)
            break
        
        print("Please enter a valid number.\n")

    # Get the standard budget and apply it to the income.
    standard_budget = user_wks.col_values(2)[1:]
    budget = [str((income * float(num))) for num in standard_budget]

    return budget


def display_data(user_wks, data, col_num):
    """
    Displays the data passed throught the function call.
    """

    # Then create a dictionary to display the newly generated budget
    budget_categories = user_wks.col_values(1)[1:]
    expenses = user_wks.col_values(col_num + 1)[1:]
    user_budget = dict(zip(budget_categories, data, expenses))

    print(75 * "-")
    print("\nMonthly Budget\n")
    print(75 * "-")

    title1, title2, title3 = "Categories", "Budget", "Expenses"

    # Display the budget to the user
    print(f"{title1:25} {title2:25} {title3:25}")
    for category, budget, expense in user_budget.items():
        print(f"{category:25} {budget:25} {expense:25}")


def save_data(user_wks, data, col_num):
    """
    Gives the user an option to save to the sheet.
    """

    option = input("\nWould you like to save? y/n ")

    if option == "y":
        print("\nSaving...")

        # iterate through the list and update the sheet
        for ind in range(len(data)):
            row = ind + 2
            value = data[ind]
            user_wks.update_cell(row, col_num, value)

        print("\nSuccessfully saved!\n")
    else:
        print("Not saved.")


def main():
    """
    Run all programm functions.
    """
    welcome_message()
    username = username_input()
    name, user_id = load_username(username)

    print(75 * "-")
    print(f"\nWelcome {name.title()}!\n")

    while True:

        print(75 * "-")
        print("\nPlease select one of the options bellow:\n")
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


main()
