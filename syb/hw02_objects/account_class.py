"""Exercise 1: (5 points)

a) Using the slides & the script, put together a file containing the
   complete Account class.  Each method must have a documentation
   string at the beginning which describes what the method is doing.
   (1 point)


c) Change the withdraw function such that the minimum balance allowed
   is -1000.  (1 point)

d) Write a function apply_interest(self) which applies an interest
   rate of 1.5% to the current balance and call it on your objects.
   (1 point)

e) Implement the __str__ magic method and use it to print accounts.
   (1 point)
"""
import re


class Account:
    """
    Specifies bank accounts and transaction functions.

    Account(number, holder):
        number: number assigned to the account
        holder: name of the person holding the account

    .set_holder(person):
        specifies 'person' as the holder of the account

    .deposit(amount)
        Deposits 'amount' to the account

    .withdraw(amount)
        Withdraws 'amount' from account.
        If the balance after the withdraw would be lower than 1000 an error message is displayed

    .apply_interest()
        Applies 1.5% interest to the current balance of the account.

    """

    # class attributes
    num_of_accounts = 0

    def __init__(self, num, holder):
        """specifies the account"""
        self.num = num
        self.holder = holder
        self.balance = 0
        Account.num_of_accounts += 1

    def set_holder(self, person):
        """specifies 'person' the holder of the account."""
        if not type(person) == str:
            raise TypeError
        # diese Zeile stand noch im Skript, hab sie aber erstmal zu implementieren übersprungen
        # if not re.match("\W+( \W+) * ", person.strip()):
        #    raise ValueError
        self.holder = person

    def deposit(self, amount):
        """Deposits 'amount' to the account."""
        self.balance += amount

    def withdraw(self, amount):
        """Withdraws 'amount' from account.
        Displays an error message if account balance after transaction would be lower than -1000"""
        if self.balance - amount >= -1000:
            self.balance -= amount
            # In den Folien stand hier "return amount" aber ich finde, das macht keinen Sinn
        else:
            raise ValueError("balance would be lower than -1000")
            #print("error: balance would be lower than -1000")

    def apply_interest(self, rate=1.015):
        """Applies 1.5% interest to the current balance."""
        self.balance *= rate

    def __str__(self):
        """ Return str(self). """
        return f"Account[num: {self.num}, holder: {self.holder}, balance:  {self.balance} ]"
#        return "Account(num: " + str(self.num) \
#               + ", holder: " + str(self.holder) \
#               + ", balance: " + str(self.balance) \
#               + ")"
