# -*- coding: utf-8 -*-
"""Loan Qualifier Application.

This is a command line application to match applicants with qualifying loans.

#File path : Copy   ../Assignment_2_loan/data/daily_rate_sheet.csv

Example:
    $ python app.py
"""
from fileinput import filename
import sys
import fire
import questionary
from pathlib import Path
import csv

from qualifier.utils.fileio import load_csv, save_csv

from qualifier.utils.calculators import (
    calculate_monthly_debt_ratio,
    calculate_loan_to_value_ratio,
)

from qualifier.filters.max_loan_size import filter_max_loan_size
from qualifier.filters.credit_score import filter_credit_score
from qualifier.filters.debt_to_income import filter_debt_to_income
from qualifier.filters.loan_to_value import filter_loan_to_value


def load_bank_data():
    """Ask for the file path to the latest banking data and load the CSV file.

    Returns:
        The bank data from the data rate sheet CSV file.
    """

    csvpath = questionary.text("Enter a file path to a rate-sheet (.csv):").ask()
    csvpath = Path(csvpath)
    if not csvpath.exists():
        sys.exit(f"Oops! Can't find this path: {csvpath}")

    return load_csv(csvpath)


def get_applicant_info():
    """Prompt dialog to get the applicant's financial information.

    Returns:
        Returns the applicant's financial information.
    """

    credit_score = questionary.text("What's your credit score?").ask()
    debt = questionary.text("What's your current amount of monthly debt?").ask()
    income = questionary.text("What's your total monthly income?").ask()
    loan_amount = questionary.text("What's your desired loan amount?").ask()
    home_value = questionary.text("What's your home value?").ask()

    credit_score = int(credit_score)
    debt = float(debt)
    income = float(income)
    loan_amount = float(loan_amount)
    home_value = float(home_value)

    return credit_score, debt, income, loan_amount, home_value


def find_qualifying_loans(bank_data, credit_score, debt, income, loan, home_value):
    """Determine which loans the user qualifies for.

    Loan qualification criteria is based on:
        - Credit Score
        - Loan Size
        - Debit to Income ratio (calculated)
        - Loan to Value ratio (calculated)

    Args:
        bank_data (list): A list of bank data.
        credit_score (int): The applicant's current credit score.
        debt (float): The applicant's total monthly debt payments.
        income (float): The applicant's total monthly income.
        loan (float): The total loan amount applied for.
        home_value (float): The estimated home value.

    Returns:
        A list of the banks willing to underwrite the loan.

    """

    # Calculate the monthly debt ratio
    monthly_debt_ratio = calculate_monthly_debt_ratio(debt, income)
    print(f"The monthly debt to income ratio is {monthly_debt_ratio:.02f}")

    # Calculate loan to value ratio
    loan_to_value_ratio = calculate_loan_to_value_ratio(loan, home_value)
    print(f"The loan to value ratio is {loan_to_value_ratio:.02f}.")

    # Run qualification filters
    bank_data_filtered = filter_max_loan_size(loan, bank_data)
    bank_data_filtered = filter_credit_score(credit_score, bank_data_filtered)
    bank_data_filtered = filter_debt_to_income(monthly_debt_ratio, bank_data_filtered)
    bank_data_filtered = filter_loan_to_value(loan_to_value_ratio, bank_data_filtered)

    # can use this code to show total : len(bank_data_filtered)
    print(f"Found {len(bank_data_filtered)} qualifying loans")
    #print(f"Here are all the loan options available for your criteria {bank_data_filtered}")
    return bank_data_filtered


def save_qualifying_loans(qualifying_loans):
    """Saves the qualifying loans to a CSV file.
       The question below only comes up when the user wants to save their loans
       Once they select save loans they will be asked to name the loan file
    Args:
        qualifying_loans (list of lists): The qualifying bank loans.
    """
    # @TODO: Complete the usability dialog for savings the CSV Files.
    # saving file as CSV

    csvpath = Path(questionary.text('Give your qualifying loan options file a name (.csv):').ask()+ '.csv')
    save_csv(csvpath, qualifying_loans)



def save_qualifying_loan_options():
    """Dialog for the Loan options Main Menu."""

    # Determines action 
    # taken by application.
    action = questionary.select(
        "Would you like to save your loan otions or not save your loan options?",
        choices=["Exit the system with no loans" , "Save my loan options", "Don't save my loan options"],
    ).ask()
    return action

'''''
# trying to make the 0 loan options close the system automatically
def no_qualifiying_loans():
    """ Sub menu where the user with no options will be put"""
    # Determines action 
    # taken by application.
    no_action = questionary.select(
        "It looks like you have not loan options, you will now exit the system",
        choices=["Exit the system"]
    ).ask()
    return no_action
# just a test above
'''''

def run():
    """The main function for running the script."""

    # Load the latest Bank data
    bank_data = load_bank_data()
    
    # Get the applicant's information
    credit_score, debt, income, loan_amount, home_value = get_applicant_info()

    # Find qualifying loans
    qualifying_loans = find_qualifying_loans(
        bank_data, credit_score, debt, income, loan_amount, home_value
    )
    # save qualifying loans by
    action = save_qualifying_loan_options()

    if action == "No Loans, exit":
        sys.exit(f"You have no qualifying loans available, good bye")
    elif action == "Save my loan options":
        qualifying_loans = save_qualifying_loans(qualifying_loans) #this option is breaking the code
        print(f"You have successfully saved your qualifying loan options, Good Bye")
    else:  
        qualifying_loans = print(f"You have exited the program and have not saved anything")


if __name__ == "__main__":
    fire.Fire(run)
