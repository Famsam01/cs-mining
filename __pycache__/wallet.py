from bip_utils import (
    Bip39MnemonicGenerator,
    Bip39SeedGenerator,
    Bip44,
    Bip44Coins,
    Bip44Changes,
)

# Generate mnemonic
mnemonic = Bip39MnemonicGenerator().FromWordsNumber(12)
print("SAVE THIS SEED PHRASE SAFELY:")
print(mnemonic)

# Generate seed
seed_bytes = Bip39SeedGenerator(mnemonic).Generate()

# Create wallet
wallet = Bip44.FromSeed(seed_bytes, Bip44Coins.BITCOIN)

# Generate first receiving address
addr = wallet.Purpose().Coin().Account(0).Change(
    Bip44Changes.CHAIN_EXT
).AddressIndex(0)

print("\nYour Bitcoin Address:")
print(addr.PublicKey().ToAddress())
