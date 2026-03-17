from tronpy import Tron
from tronpy.providers import HTTPProvider

# Official TRC20 USDT contract
USDT_CONTRACT = "TXLAQ63Xg1NAzckPwKHvzw7CSEmLMEqcdj"

client = Tron(HTTPProvider("https://api.trongrid.io"))

# Fetch contract (ABI auto-loaded)
contract = client.get_contract(USDT_CONTRACT)


def check_usdt_balance(address):
    balance = contract.functions.balanceOf(address)
    return balance / 1_000_000


if __name__ == "__main__":
    addr = input("Enter TRON address: ").strip()
    print("Checking balance...")
    print("USDT:", check_usdt_balance(addr))
