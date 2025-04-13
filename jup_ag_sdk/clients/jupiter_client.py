import base64
import os
from typing import Dict, Optional

import base58
import httpx
from solana.rpc.api import Client
from solders.solders import Keypair, SendTransactionResp, VersionedTransaction


class JupiterClient:
    """
    Base client for interacting with Jupiter API.
    Also acts as a parent class for all sub-clients.
    """

    def __init__(
        self,
        api_key: Optional[str],
        rpc_url: Optional[str],
        private_key_env_var: str,
        timeout: int,
    ):
        self.api_key = api_key
        self.rpc = Client(rpc_url) if rpc_url else None
        self.base_url = (
            "https://api.jup.ag" if api_key else "https://lite-api.jup.ag"
        )
        self.private_key_env_var = private_key_env_var
        self.timeout = timeout
        self.client = httpx.Client(timeout=self.timeout)

    def close(self) -> None:
        self.client.close()

    def _get_headers(self) -> Dict[str, str]:
        headers = {
            "Accept": "application/json",
        }
        if self.api_key:
            headers["x-api-key"] = self.api_key
        return headers

    def _post_headers(self) -> Dict[str, str]:
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
        }
        if self.api_key:
            headers["x-api-key"] = self.api_key
        return headers

    def _get_public_key(self) -> str:
        wallet = Keypair.from_bytes(
            base58.b58decode(os.getenv(self.private_key_env_var, ""))
        )
        return str(wallet.pubkey())

    def _send_transaction(
        self, transaction: VersionedTransaction
    ) -> SendTransactionResp:
        if not self.rpc:
            raise ValueError("Client was initialized without RPC URL.")
        return self.rpc.send_transaction(transaction)

    def _sign_base64_transaction(
        self, transaction_base64: str
    ) -> VersionedTransaction:
        transaction_bytes = base64.b64decode(transaction_base64)
        versioned_transaction = VersionedTransaction.from_bytes(
            transaction_bytes
        )
        return self._sign_versioned_transaction(versioned_transaction)

    def _sign_versioned_transaction(
        self, versioned_transaction: VersionedTransaction
    ) -> VersionedTransaction:
        wallet = Keypair.from_bytes(
            base58.b58decode(os.getenv(self.private_key_env_var, ""))
        )
        account_keys = versioned_transaction.message.account_keys
        wallet_index = account_keys.index(wallet.pubkey())

        signers = list(versioned_transaction.signatures)
        signers[wallet_index] = wallet  # type: ignore

        return VersionedTransaction(
            versioned_transaction.message, signers  # type: ignore
        )

    def _serialize_versioned_transaction(
        self, versioned_transaction: VersionedTransaction
    ) -> str:
        return base64.b64encode(bytes(versioned_transaction)).decode("utf-8")
