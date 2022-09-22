import gspread
from google.oauth2.service_account import Credentials

# Created the logo using pyfiglet
import pyfiglet

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
    logo = pyfiglet.figlet_format("FINANCE GUARDIAN")
    print(logo)
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
    user_id = str(int(id_data[-1]) + 1)

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
    print("\nCreate New Budget\n")
    print(75 * "-")

    user_wks = SHEET.worksheet(user_id)

    # function to allow the user to select a month and validate
    selection = select_month()

    # return the selection and analyse what was inputed
    if selection == "0":
        return
    
    col_num = (int(selection) * 2) + 1
    month_income = user_wks.col_values(col_num)[-1]

    # check if a budget already exists
    if month_income != "0":
        print("\nA budget already exists.\n")
        
        while True:
            option = input("Would you like to create a new one? y/n\n")

            if option == "n":
                return
            elif option == "y":
                break
            else:
                print("Invalid option! Please enter only Y or N.")
        
    data = create_new_budget(user_wks)
    display_budget_data(user_wks, data, col_num)
    save_data(user_wks, data, col_num)

    # Option for the user to create a new budget
    while True:
        option = input("\nWould you like to create a new budget? y/n\n")

        if option == "n":
            return
        elif option == "y":
            new_budget(user_id)
            break
        else:
            print("Invalid option! Please enter only Y or N.")


def select_month():
    """
    Checks and selects the month the user would like to view.
    If it is empty, it alerts the user.
    """

    while True:
        print("\nPlease select one of the options bellow:")
        print(
            "\n1. January\n"
            "2. February\n"
            "3. March\n"
            "4. April\n"
            "5. May\n"
            "6. June\n"
            "7. July\n"
            "8. August\n"
            "9. September\n"
            "10. October\n"
            "11. November\n"
            "12. December\n"
            "0. Return to main menu")

        selection = input("\nYour selection: ")

        if validate_list_selection(selection, 12):
            return selection


def validate_list_selection(selection, max_num):
    """
    Validate the input from the month selection.
    """
    try:
        if not selection.isnumeric():
            raise ValueError(
                "Please select only numbers"
            )

        if int(selection) > max_num:
            raise ValueError(
                "Select a number from the list."
            )
    except ValueError as e:
        print(f"\nInvalid data: {e} Please try again.\n")
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
    budget = [str(income * float((int(num) / 100))) for num in standard_budget]

    return budget


def display_budget_data(user_wks, data, col_num):
    """
    Displays the data passed throught the function call.
    """

    # Create a dictionary to display the newly generated budget
    budget_categories = user_wks.col_values(1)[1:]
    expenses = user_wks.col_values(col_num + 1)[1:]
    user_data = dict(zip(budget_categories, data))

    month = user_wks.col_values(col_num)[0]
    print(75 * "-")
    print(f"\n{month} Monthly Budget\n")
    print(75 * "-")

    title1, title2, title3 = "Categories", "Budget", "Expenses"

    # Using for loop to display the budget to the user
    print(f"{title1:25} {title2:25} {title3:25}\n")

    ind = 0
    for category, budget in user_data.items():
        expense = expenses[ind]
        ind += 1
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

        print("\nSuccessfully saved!")
    else:
        print("\nNot saved.")


def view_budget(user_id):
    """
    Gives the user an option to select a month
    and checks to see if a budget exists. If yes, it then
    displays the budget to the user.
    """

    # Title
    print(75 * "-")
    print("\nView Budget\n")
    print(75 * "-")

    user_wks = SHEET.worksheet(user_id)

    # function to allow the user to select a month and validate
    selection = select_month()

    # return the selection and analyse what was inputed
    if selection == "0":
        return
    
    col_num = (int(selection) * 2) + 1
    month_income = user_wks.col_values(col_num)[-1]

    # check if a budget exists
    if month_income == "0":
        print("\nThis budget is empty.\n")

        while True:
            option = input("Would you like to create a new one? y/n\n")

            if option == "n":
                break
            elif option == "y":
                new_budget(user_id)
                break
            else:
                print("Invalid option! Please enter only Y or N.")
    else:
        data = user_wks.col_values(col_num)[1:]
        display_budget_data(user_wks, data, col_num)

    # Option for the user to view a new budget
    while True:
        option = input("\nWould you like to view a new budget? y/n\n")

        if option == "n":
            return
        elif option == "y":
            view_budget(user_id)
            break
        else:
            print("Invalid option! Please enter only Y or N.")


def update_budget(user_id):
    """
    Gives the user an option to update an existing budget.
    """

    # Title
    print(75 * "-")
    print("\nUpdate Budget\n")
    print(75 * "-")

    user_wks = SHEET.worksheet(user_id)

    # function to allow the user to select a month and validate
    selection = select_month()

    # return the selection and analyse what was inputed
    if selection == "0":
        return
    
    col_num = (int(selection) * 2) + 1
    month_income = user_wks.col_values(col_num)[-1]

    # check if a budget exists
    if month_income == "0":
        print("\nThis budget is empty.\n")

        while True:
            option = input("Would you like to create a new one? y/n\n")

            if option == "n":
                break
            elif option == "y":
                new_budget(user_id)
                break
            else:
                print("Invalid option! Please enter only Y or N.")
    else:
        data = input_new_budget(user_wks, col_num)
        save_data(user_wks, data, col_num)

    # Option for the user to update a new budget
    while True:
        option = input("\nWould you like to update a new budget? y/n\n")

        if option == "n":
            return
        elif option == "y":
            update_budget(user_id)
            break
        else:
            print("Invalid option! Please enter only Y or N.")


def input_new_budget(user_wks, col_num):
    """
    Allows the user to update existing data in budgets.
    """

    data = user_wks.col_values(col_num)[1:]
    display_budget_data(user_wks, data, col_num)
    
    while True:
        selection = input(
            "\nPlease select a category to update,"
            "\nor select 0 to finish updating:\n")

        if selection == "0":
            break
        
        elif validate_list_selection(selection, 10):
            
            # Give the user the option to input a new value
            while True:

                value = input("\nPlease enter a value:\n")

                if value.replace(".", "", 1).isdigit():
                    value = float(value)
                    break
                print("Please enter a valid number.")
            
            data[int(selection) - 1] = str(value)
            display_budget_data(user_wks, data, col_num)

    return data      


def delete_budget(user_id):
    """
    This function allows the user to delete a budget.
    """

    # Title
    print(75 * "-")
    print("\nDelete Budget\n")
    print(75 * "-")

    user_wks = SHEET.worksheet(user_id)

    # function to allow the user to select a month and validate
    selection = select_month()

    # return the selection and analyse what was inputed
    if selection == "0":
        return
    
    col_num = (int(selection) * 2) + 1
    month = user_wks.col_values(col_num)[0]

    while True:
        option = input(f"Confirm deletion of {month}'s budget? y/n\n")

        if option == "n":
            return
        elif option == "y":
            break
        else:
            print("Invalid option! Please enter only Y or N.")

    print(f"Deleting {month}'s budget...")
    data = user_wks.col_values(col_num)[1:]

    for num in range(len(data)):
        data[num] = "0"

    save_data(user_wks, data, col_num)


def update_transaction(user_id):
    """
    Give the user the option to add or update a transaction.
    """

    # Title
    print(75 * "-")
    print("\nAdd or Update Transaction\n")
    print(75 * "-")

    user_wks = SHEET.worksheet(user_id)

    # function to allow the user to select a month and validate
    selection = select_month()

    # return the selection and analyse what was inputed
    if selection == "0":
        return
    
    col_num = (int(selection) * 2) + 2
    
    data = input_new_transaction(user_wks, col_num)
    save_data(user_wks, data, col_num)

    # Option for the user to update transaction on a new month
    while True:
        option = input("\nWould you like to update transactions in a new month? y/n\n")

        if option == "n":
            return
        elif option == "y":
            update_transaction(user_id)
            break
        else:
            print("Invalid option! Please enter only Y or N.")


def input_new_transaction(user_wks, col_num):
    """
    Allows the user to update existing data in transactions.
    """

    data = user_wks.col_values(col_num)[1:]
    display_transaction_data(user_wks, data, col_num)
    
    while True:
        selection = input(
            "\nPlease select a category to update,"
            "\nor select 0 to finish updating:\n")

        if selection == "0":
            break
        
        elif validate_list_selection(selection, 10):
            
            # Give the user the option to input a new value
            while True:

                value = input("\nPlease enter a value:\n")

                if value.replace(".", "", 1).isdigit():
                    value = float(value)
                    break
                print("Please enter a valid number.")
            
            data[int(selection) - 1] = str(value)
            display_transaction_data(user_wks, data, col_num)

    return data  


def display_transaction_data(user_wks, data, col_num):
    """
    Displays the data passed throught the function call.
    """

    # Create a dictionary to display the newly generated budget
    budget_categories = user_wks.col_values(1)[1:]
    saved_budget = user_wks.col_values(col_num - 1)[1:]
    user_data = dict(zip(budget_categories, data))

    month = user_wks.col_values(col_num - 1)[0]
    print(75 * "-")
    print(f"\n{month} Monthly Budget\n")
    print(75 * "-")

    title1, title2, title3 = "Categories", "Budget", "Expenses"

    # Using for loop to display the budget to the user
    print(f"{title1:25} {title2:25} {title3:25}\n")

    ind = 0
    for category, expense in user_data.items():
        budget = saved_budget[ind]
        ind += 1
        print(f"{category:25} {budget:25} {expense:25}")


def view_transaction(user_id):
    """
    Gives the user an option to select a month
    and display all transactions.
    """

    # Title
    print(75 * "-")
    print("\nView Transactions\n")
    print(75 * "-")

    user_wks = SHEET.worksheet(user_id)

    # function to allow the user to select a month and validate
    selection = select_month()

    # return the selection and analyse what was inputed
    if selection == "0":
        return
    
    col_num = (int(selection) * 2) + 2

    data = user_wks.col_values(col_num)[1:]
    display_transaction_data(user_wks, data, col_num)

    # Option for the user to view a new budget
    while True:
        option = input("\nWould you like to view a new month? y/n\n")

        if option == "n":
            return
        elif option == "y":
            view_transaction(user_id)
            break
        else:
            print("Invalid option! Please enter only Y or N.")


def delete_transactions(user_id):
    """
    This function allows the user to delete transactions.
    """

    # Title
    print(75 * "-")
    print("\nDelete Transactions\n")
    print(75 * "-")

    user_wks = SHEET.worksheet(user_id)

    # function to allow the user to select a month and validate
    selection = select_month()

    # return the selection and analyse what was inputed
    if selection == "0":
        return
    
    col_num = (int(selection) * 2) + 2
    month = user_wks.col_values(col_num - 1)[0]

    print(
        "\nTo update or delete a single transaction\n"
        "please go to add or update transactions in the main menu\n")

    while True:
        option = input(f"Confirm deletion of {month}'s transactions? y/n\n")

        if option == "n":
            return
        elif option == "y":
            break
        else:
            print("Invalid option! Please enter only Y or N.")

    print(f"Deleting {month}'s transactions...")
    data = user_wks.col_values(col_num)[1:]

    for num in range(len(data)):
        data[num] = "0"

    save_data(user_wks, data, col_num)


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
            "4. Delete budget\n"
            "5. Add or update transaction\n"
            "6. View transactions\n"
            "7. Delete transactions\n"
            "8. Log out\n")

        option = input("Your selections: ")

        if option == "1":
            new_budget(user_id)

        elif option == "2":
            view_budget(user_id)

        elif option == "3":
            update_budget(user_id)

        elif option == "4":
            delete_budget(user_id)

        elif option == "5":
            update_transaction(user_id)

        elif option == "6":
            view_transaction(user_id)
        
        elif option == "7":
            delete_transactions(user_id)

        elif option == "8":
            print(
                "\nThank you for using Finance Guardian.\n"
                f"Good bye {name}!\n")
            quit()

        else:
            print("Invalid option")


main()
