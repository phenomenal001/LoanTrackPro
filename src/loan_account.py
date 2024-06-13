from app import db, LoanAccount, app
from random import randint

def genval(w):
    return str(randint(0, 10**w-1)).zfill(w)


def create_loan_account(account_number, latitude, longitude, status, assigned_to=None):
    new_loan_account = LoanAccount(account_number=account_number, latitude=latitude, longitude=longitude, status=status, assigned_to=assigned_to)

    db.session.add(new_loan_account)
    db.session.commit()
    print(f'Loan account: {account_number} created.')


if __name__ == "__main__":
    with app.app_context():
        db.create_all()  # Ensure the tables are created
        account_number = genval(16)
        # Create a Loan accounts
        create_loan_account(account_number, 19.302932413567063, 72.84996176608338, "Not completed",14)