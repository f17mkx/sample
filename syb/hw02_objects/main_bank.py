
from account_class import Account

if __name__ == "__main__":
    print("Welcome to the Python Bank!")

    stevoACC = Account(123, "Stefan Volk")
    jowoACC = Account(999, "Jonas Welle")
    frikuACC = Account(823, "Friderike Kunze")
    hameiACC = Account(982, "Hans Meier")

    print(Account.num_of_accounts, "accounts have been created.")

    print(stevoACC)

    stevoACC.deposit(400)
    print(f"Balance: {stevoACC.balance}")

    import itertools
    for _ in itertools.repeat(None, 100):
        stevoACC.apply_interest()

    print(f"Balance: {stevoACC.balance}")

    stevoACC.withdraw(1407)
    print(stevoACC)

    stevoACC.set_holder("Hannes Mannes")
    print(stevoACC)

    stevoACC.withdraw(10)
    print(stevoACC)

