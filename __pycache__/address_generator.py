import os
from dotenv import load_dotenv
from bip_utils import Bip39SeedGenerator, Bip44, Bip44Coins, Bip44Changes

load_dotenv()

SEED_PHRASE = os.getenv("SEED_PHRASE")


def generate_tron_address(index: int):
    seed_bytes = Bip39SeedGenerator(SEED_PHRASE).Generate()

    wallet = Bip44.FromSeed(seed_bytes, Bip44Coins.TRON)

    addr = (
        wallet
        .Purpose()
        .Coin()
        .Account(0)
        .Change(Bip44Changes.CHAIN_EXT)
        .AddressIndex(index)
    )

    return addr.PublicKey().ToAddress()
