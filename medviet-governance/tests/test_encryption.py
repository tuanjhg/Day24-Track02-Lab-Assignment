import base64
import json

import pandas as pd

from src.encryption.vault import SimpleVault


def test_envelope_encryption_round_trip(tmp_path):
    vault = SimpleVault(master_key_path=str(tmp_path / ".vault_key"))
    plaintext = "patient: Nguyen Van A, cccd: 012345678901"

    payload = vault.encrypt_data(plaintext)

    assert payload["algorithm"] == "AES-256-GCM"
    assert plaintext not in payload["ciphertext"]
    assert plaintext not in payload["encrypted_dek"]
    assert vault.decrypt_data(payload) == plaintext


def test_encrypted_dek_is_not_plaintext_dek(tmp_path):
    vault = SimpleVault(master_key_path=str(tmp_path / ".vault_key"))

    plaintext_dek, encrypted_dek = vault.generate_dek()

    assert encrypted_dek != plaintext_dek
    assert len(plaintext_dek) == 32
    assert len(encrypted_dek) > len(plaintext_dek)
    assert vault.decrypt_dek(encrypted_dek) == plaintext_dek


def test_encrypt_column_replaces_plaintext_values(tmp_path):
    vault = SimpleVault(master_key_path=str(tmp_path / ".vault_key"))
    df = pd.DataFrame({"cccd": ["012345678901"]})

    encrypted_df = vault.encrypt_column(df, "cccd")

    encrypted_value = encrypted_df.loc[0, "cccd"]
    assert "012345678901" not in encrypted_value
    assert base64.b64decode(json.loads(encrypted_value)["ciphertext"])
