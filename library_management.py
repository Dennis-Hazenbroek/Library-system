#! /usr/bin/env python3
import json
import os
from datetime import date, timedelta

# ==================================================
# LIBRARY MANAGEMENT SYSTEM
# Python + JSON (No Database)
# ==================================================

DATA_FILE = "library.json"

LOAN_PERIOD = 21
LATE_FEE_PER_DAY = 100  # 100 pence = £1


# ==================================================
# 1. JSON FILE MANAGEMENT
# ==================================================

def load_data():

    if not os.path.exists(DATA_FILE):
        data = {
            "books": [],
            "loans": []
        }
        save_data(data)
        return data

    try:
        with open(DATA_FILE, "r", encoding="utf-8") as file:
            data = json.load(file)

        data.setdefault("books", [])
        data.setdefault("loans", [])

        return data

    except (json.JSONDecodeError, OSError) as error:
        print(f"Error reading library file: {error}")
        print("Please check library.json before continuing.")
        raise


def save_data(data):

    with open(DATA_FILE, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4, ensure_ascii=False)


# ==================================================
# 2. DATE AND MONEY FUNCTIONS
# ==================================================

def format_date(date_string):

    if not date_string:
        return "Not returned"

    return date.fromisoformat(date_string).strftime("%d/%m/%Y")


def calculate_late_fee(due_date, returned_date):

    due = date.fromisoformat(due_date)
    returned = date.fromisoformat(returned_date)

    days_late = max(0, (returned - due).days)

    fee_pence = days_late * LATE_FEE_PER_DAY

    return fee_pence


def format_money(pence):

    pounds = pence / 100

    return f"£{pounds:.2f}"


# ==================================================
# 3. BOOK LOOKUP
# ==================================================

def find_book(data, isbn):

    for book in data["books"]:
        if book["isbn"] == isbn:
            return book

    return None


def active_loan(data, isbn):

    for loan in data["loans"]:
        if loan["isbn"] == isbn and loan["date_returned"] is None:
            return loan

    return None


# ==================================================
# 4. ADD A NEW BOOK
# ==================================================

def add_book(data):

    print("\n========== ADD NEW BOOK ==========")

    isbn = input("Enter ISBN: ").strip()
    title = input("Enter book title: ").strip()
    author = input("Enter author: ").strip()
    category = input("Enter category: ").strip()

    if not all([isbn, title, author, category]):
        print("All fields are required.")
        return

    if find_book(data, isbn):
        print("This ISBN already exists in the catalogue.")
        return

    book = {
        "isbn": isbn,
        "title": title,
        "author": author,
        "category": category
    }

    data["books"].append(book)

    save_data(data)

    print("\nBook successfully added!")
    print(f"ISBN: {isbn}")
    print(f"Title: {title}")


# ==================================================
# 5. BORROW A BOOK
# ==================================================

def borrow_book(data):

    print("\n========== BORROW A BOOK ==========")

    isbn = input("Enter ISBN: ").strip()

    book = find_book(data, isbn)

    if book is None:
        print("Book not found in the library catalogue.")
        return

    if active_loan(data, isbn):
        print("This book is already borrowed.")
        return

    # Automatically generate borrowing date
    date_out = date.today()

    # Automatically calculate due date
    due_date = date_out + timedelta(days=LOAN_PERIOD)

    # Generate a unique loan ID
    loan_id = max(
        (loan["loan_id"] for loan in data["loans"]),
        default=0
    ) + 1

    loan = {
        "loan_id": loan_id,
        "isbn": isbn,
        "date_out": date_out.isoformat(),
        "due_date": due_date.isoformat(),
        "date_returned": None,
        "late_fee_pence": 0
    }

    data["loans"].append(loan)

    save_data(data)

    print("\nBook successfully borrowed!")
    print("----------------------------------")
    print(f"Loan ID: {loan_id}")
    print(f"ISBN: {isbn}")
    print(f"Title: {book['title']}")
    print(f"Author: {book['author']}")
    print(f"Category: {book['category']}")
    print(f"Date Out: {format_date(loan['date_out'])}")
    print(f"Due Date: {format_date(loan['due_date'])}")
    print("Loan Period: 21 days")
    print("----------------------------------")


# ==================================================
# 6. RETURN A BOOK
# ==================================================

def return_book(data):

    print("\n========== RETURN A BOOK ==========")

    try:
        loan_id = int(input("Enter Loan ID: "))
    except ValueError:
        print("Please enter a valid loan ID.")
        return

    loan = next(
        (
            item for item in data["loans"]
            if item["loan_id"] == loan_id
        ),
        None
    )

    if loan is None:
        print("Loan record not found.")
        return

    if loan["date_returned"] is not None:
        print("This book has already been returned.")
        return

    # Automatically generate return date
    returned_date = date.today()

    # Calculate late fee
    late_fee = calculate_late_fee(
        loan["due_date"],
        returned_date.isoformat()
    )

    loan["date_returned"] = returned_date.isoformat()
    loan["late_fee_pence"] = late_fee

    save_data(data)

    book = find_book(data, loan["isbn"])

    print("\n========== BOOK RETURNED ==========")
    print(f"Title: {book['title']}")
    print(f"ISBN: {loan['isbn']}")
    print(f"Due Date: {format_date(loan['due_date'])}")
    print(f"Date Returned: {format_date(loan['date_returned'])}")

    days_late = max(
        0,
        (returned_date - date.fromisoformat(loan["due_date"])).days
    )

    print(f"Days Late: {days_late}")
    print(f"Late Fee: {format_money(late_fee)}")
    print("===================================")


# ==================================================
# 7. SEARCH FOR A BOOK
# ==================================================

def search_book(data):

    print("\n========== SEARCH BOOKS ==========")

    isbn = input("Enter ISBN: ").strip()

    book = find_book(data, isbn)

    if book is None:
        print("Book not found.")
        return

    loan = active_loan(data, isbn)

    print("\nBook Details")
    print("----------------------------------")
    print(f"ISBN: {book['isbn']}")
    print(f"Title: {book['title']}")
    print(f"Author: {book['author']}")
    print(f"Category: {book['category']}")

    if loan:
        print("Status: ON LOAN")
        print(f"Date Out: {format_date(loan['date_out'])}")
        print(f"Due Date: {format_date(loan['due_date'])}")
    else:
        print("Status: AVAILABLE")

    print("----------------------------------")


# ==================================================
# 8. DISPLAY ALL BOOKS
# ==================================================

def display_all_books(data):

    print("\n========== LIBRARY CATALOGUE ==========")

    if not data["books"]:
        print("No books in the catalogue.")
        return

    for book in data["books"]:

        loan = active_loan(data, book["isbn"])

        status = "ON LOAN" if loan else "AVAILABLE"

        print("\n----------------------------------")
        print(f"ISBN: {book['isbn']}")
        print(f"Title: {book['title']}")
        print(f"Author: {book['author']}")
        print(f"Category: {book['category']}")
        print(f"Status: {status}")

        if loan:
            print(f"Due Date: {format_date(loan['due_date'])}")

    print("----------------------------------")


# ==================================================
# 9. DISPLAY CURRENTLY BORROWED BOOKS
# ==================================================

def display_borrowed_books(data):

    print("\n========== BORROWED BOOKS ==========")

    borrowed = [
        loan for loan in data["loans"]
        if loan["date_returned"] is None
    ]

    if not borrowed:
        print("There are no borrowed books.")
        return

    today = date.today()

    for loan in borrowed:

        book = find_book(data, loan["isbn"])

        due = date.fromisoformat(loan["due_date"])

        estimated_fee = calculate_late_fee(
            loan["due_date"],
            today.isoformat()
        )

        status = "OVERDUE" if today > due else "ON TIME"

        print("\n----------------------------------")
        print(f"Loan ID: {loan['loan_id']}")
        print(f"ISBN: {loan['isbn']}")
        print(f"Title: {book['title']}")
        print(f"Author: {book['author']}")
        print(f"Date Out: {format_date(loan['date_out'])}")
        print(f"Due Date: {format_date(loan['due_date'])}")
        print(f"Status: {status}")
        print(f"Estimated Late Fee: {format_money(estimated_fee)}")


# ==================================================
# 10. DISPLAY OVERDUE BOOKS
# ==================================================

def display_overdue_books(data):

    print("\n========== OVERDUE BOOKS ==========")

    today = date.today()

    overdue = [
        loan for loan in data["loans"]
        if loan["date_returned"] is None
        and date.fromisoformat(loan["due_date"]) < today
    ]

    if not overdue:
        print("There are no overdue books.")
        return

    for loan in overdue:

        book = find_book(data, loan["isbn"])

        due = date.fromisoformat(loan["due_date"])

        days_late = (today - due).days

        estimated_fee = calculate_late_fee(
            loan["due_date"],
            today.isoformat()
        )

        print("\n----------------------------------")
        print(f"Loan ID: {loan['loan_id']}")
        print(f"Title: {book['title']}")
        print(f"Author: {book['author']}")
        print(f"ISBN: {loan['isbn']}")
        print(f"Due Date: {format_date(loan['due_date'])}")
        print(f"Days Overdue: {days_late}")
        print(f"Estimated Late Fee: {format_money(estimated_fee)}")


# ==================================================
# 11. BORROWING AND LATE FEE REPORT
# ==================================================

def display_reports(data):

    print("\n========== LIBRARY REPORT ==========")

    total_books = len(data["books"])
    total_loans = len(data["loans"])

    returned = [
        loan for loan in data["loans"]
        if loan["date_returned"] is not None
    ]

    borrowed = [
        loan for loan in data["loans"]
        if loan["date_returned"] is None
    ]

    overdue = [
        loan for loan in borrowed
        if date.fromisoformat(loan["due_date"]) < date.today()
    ]

    total_fees = sum(
        loan["late_fee_pence"] for loan in returned
    )

    outstanding_fees = sum(
        calculate_late_fee(
            loan["due_date"],
            date.today().isoformat()
        )
        for loan in overdue
    )

    print(f"Total Books in Catalogue: {total_books}")
    print(f"Total Loans Recorded: {total_loans}")
    print(f"Books Currently Borrowed: {len(borrowed)}")
    print(f"Books Returned: {len(returned)}")
    print(f"Books Overdue: {len(overdue)}")
    print("----------------------------------")
    print(f"Recorded Late Fees: {format_money(total_fees)}")
    print(f"Estimated Outstanding Fees: {format_money(outstanding_fees)}")
    print("==================================")


# ==================================================
# 12. MAIN MENU
# ==================================================

def main():

    data = load_data()

    while True:

        print("\n")
        print("======================================")
        print("       LIBRARY MANAGEMENT SYSTEM")
        print("======================================")
        print("1. Add a New Book")
        print("2. Borrow a Book")
        print("3. Return a Book")
        print("4. Search for a Book (ISBN)")
        print("5. Display All Books")
        print("6. Display Borrowed Books")
        print("7. Display Overdue Books")
        print("8. Borrowing and Late Fee Reports")
        print("9. Exit")
        print("======================================")

        choice = input("Please select an option (1-9): ").strip()

        if choice == "1":
            add_book(data)

        elif choice == "2":
            borrow_book(data)

        elif choice == "3":
            return_book(data)

        elif choice == "4":
            search_book(data)

        elif choice == "5":
            display_all_books(data)

        elif choice == "6":
            display_borrowed_books(data)

        elif choice == "7":
            display_overdue_books(data)

        elif choice == "8":
            display_reports(data)

        elif choice == "9":
            print("\nThank you for using the Library Management System.")
            break

        else:
            print("\nInvalid selection. Please try again.")


# ==================================================
# START THE PROGRAMME
# ==================================================

if __name__ == "__main__":
    main()
