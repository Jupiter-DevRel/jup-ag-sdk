from jup_ag_sdk.clients.jupiter_client import JupiterClient
from jup_ag_sdk.models.ultra_api.ultra_execute_request_model import UltraExecuteRequest
from jup_ag_sdk.models.ultra_api.ultra_order_request_model import UltraOrderRequest


class UltraApiClient(JupiterClient):
    """
    A client for interacting with the Jupiter Swap API. Inherits from JupiterClient.
    """

    def __init__(
        self, api_key=None, private_key_env_var="PRIVATE_KEY", timeout=10
    ):
        super().__init__(
            api_key=api_key,
            rpc_url=None,
            private_key_env_var=private_key_env_var,
            timeout=timeout,
        )

    def order(self, request: UltraOrderRequest) -> dict:
        """
        Get an order from the Jupiter Ultra API.

        Args:
            request (UltraOrderRequest): The request parameters for the order.

        Returns:
            dict: The dict api response.
        """
        params = request.to_dict()

        url = f"{self.base_url}/ultra/v1/order"
        response = self.client.get(url, params=params, headers=self._get_headers())
        response.raise_for_status()

        return response.json()

    def execute(self, request: UltraExecuteRequest) -> dict:
        """
        Execute the order with the Jupiter Ultra API.

        Args:
            request (UltraExecuteRequest): The execute request parameters.

        Returns:
            dict: The dict api response.
        """
        payload = request.to_dict()

        url = f"{self.base_url}/ultra/v1/execute"
        response = self.client.post(url, json=payload, headers=self._get_headers())
        response.raise_for_status()

        return response.json()

    def order_and_execute(self, request: UltraOrderRequest) -> dict:
        """
        Get an order from the Jupiter Ultra API and execute it immediately.

        Args:
            request (UltraOrderRequest): The request parameters for the order.

        Returns:
            dict: The dict api response.
        """
        order_response = self.order(request)

        request_id = order_response["requestId"]
        signed_transaction = self._sign_base64_transaction(
            order_response["transaction"]
        )

        execute_request = UltraExecuteRequest(
            request_id=request_id,
            signed_transaction=self._serialize_versioned_transaction(signed_transaction),
        )

        return self.execute(execute_request)
