# Expense Tracker

This project is a simple web application that allows users to track their expenses. The application is built using Python Flask, SQLite, and SQLAlchemy.

![Screenshot](images/screenshot.png)

## Features

- User Registration and Login
- Add, Update, and Delete Expenses
- Add Incomes
- Add Categories
- List and Filter Expenses and Incomes
- View Total Expenses and Incomes
- Categorize Expenses and Incomes
- View Expense Reports and Charts

## Installation

Follow these steps to run the project on your local machine.

### Requirements

- Python 3.7+
- SQLite

### Steps

1. Clone the repository:

    ```bash
    git clone https://github.com/seymausta/expense-tracker0.git
    cd expense-tracker0
    ```

2. Create a virtual environment:

    ```bash
    python -m venv venv
    ```

3. Activate the virtual environment:

    ```bash
    # Windows
    venv\Scripts\activate

    # MacOS/Linux
    source venv/bin/activate
    ```

4. Install the required packages:

    ```bash
    pip install -r requirements.txt
    ```

5. Create the database:

    ```bash
    flask db init
    flask db migrate -m "Initial migration."
    flask db upgrade
    ```

6. Run the application:

    ```bash
    flask run
    ```

## Usage

1. Open your browser and go to `http://127.0.0.1:5000`.
2. Register for a new account or log in with an existing account.
3. Add, update, or delete expenses.
4. Filter your expenses by category and view your total expenses.


## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for more information.

## Contact

If you have any questions or feedback, please contact me at [seymanur.usta.123@gmail.com](mailto:seymanur.usta.123@gmail.com).
