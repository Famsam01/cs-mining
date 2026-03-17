import requests
import hmac
import hashlib
import json
from datetime import datetime
from flask import current_app


class FlutterwaveService:
    def __init__(self):
        self.base_url = current_app.config['FLW_BASE_URL']
        self.secret_key = current_app.config['FLW_SECRET_KEY']
        self.secret_hash = current_app.config['FLW_SECRET_HASH']

    def _headers(self):
        return {
            'Authorization': f'Bearer {self.secret_key}',
            'Content-Type': 'application/json'
        }

    def _api_call(self, method, endpoint, data=None):
        url = f'{self.base_url}{endpoint}'

        if method == 'GET':
            response = requests.get(url, headers=self._headers())
        elif method == 'POST':
            response = requests.post(url, json=data, headers=self._headers())
        elif method == 'PUT':
            response = requests.put(url, json=data, headers=self._headers())
        else:
            raise ValueError(f'Unsupported method: {method}')

        return response.json()

    # ==================== VIRTUAL ACCOUNTS ====================

    def create_virtual_account(self, email, tx_ref, amount=None,
                               firstname=None, lastname=None,
                               phone=None, is_permanent=False, bvn=None):
        """
        Create virtual account for user

        Args:
            email: Customer email (required)
            tx_ref: Unique transaction reference
            amount: Amount for dynamic accounts (None for static)
            is_permanent: True for wallet funding (static), False for one-time
            bvn: Required for permanent accounts
        """
        payload = {
            'email': email,
            'tx_ref': tx_ref,
            'currency': 'NGN',
            'is_permanent': is_permanent,
        }

        # Add optional fields
        if amount:
            payload['amount'] = amount
        if firstname:
            payload['firstname'] = firstname
        if lastname:
            payload['lastname'] = lastname
        if phone:
            payload['phonenumber'] = phone
        if bvn:
            payload['bvn'] = bvn

        result = self._api_call('POST', '/virtual-account-numbers', payload)

        if result.get('status') == 'success':
            data = result['data']
            return {
                'account_number': data['account_number'],
                'bank_name': data['bank_name'],
                'order_ref': data['order_ref'],
                'flw_ref': data['flw_ref'],
                'expiry_date': data.get('expiry_date'),  # None for permanent
                'amount': data.get('amount'),
                'tx_ref': tx_ref
            }

        raise Exception(
            f"Virtual account creation failed: {result.get('message')}")

    def get_virtual_account(self, order_ref):
        """Fetch virtual account details"""
        return self._api_call('GET', f'/virtual-account-numbers/{order_ref}')

    def update_bvn(self, account_ref, bvn):
        """Update BVN for a virtual account"""
        payload = {'bvn': bvn}
        return self._api_call('PUT', f'/virtual-account-numbers/{account_ref}', payload)

    def delete_virtual_account(self, order_ref):
        """Delete/deactivate a virtual account"""
        # Note: Flutterwave doesn't support true deletion, just deactivation
        pass

    # ==================== TRANSACTION VERIFICATION ====================

    def verify_transaction(self, transaction_id):
        """
        Verify transaction by ID - CRITICAL for webhooks
        Always re-query to confirm payment before crediting user
        """
        result = self._api_call(
            'GET', f'/transactions/{transaction_id}/verify')

        if result.get('status') == 'success':
            data = result['data']
            return {
                'status': data['status'],  # successful, failed, pending
                'amount': float(data['amount']),
                'currency': data['currency'],
                'tx_ref': data['tx_ref'],
                'transaction_id': data['id'],
                'payment_type': data.get('payment_type'),
                'customer': data.get('customer', {}),
                'meta': data.get('meta', {})
            }

        raise Exception(f"Verification failed: {result.get('message')}")

    def verify_transaction_by_ref(self, tx_ref):
        """Verify using your transaction reference"""
        result = self._api_call(
            'GET', f'/transactions/verify_by_reference?tx_ref={tx_ref}')
        return result

    # ==================== WEBHOOK HANDLING ====================

    @staticmethod
    def verify_webhook_signature(payload_body, signature, secret_hash):
        """
        Verify Flutterwave webhook signature

        Flutterwave uses simple secret hash comparison (not HMAC)
        The signature is just the raw secret hash you configured
        """
        if not signature:
            return False
        return hmac.compare_digest(signature, secret_hash)

    def process_webhook(self, event_data):
        """
        Process webhook payload and return standardized data

        Flutterwave webhook events for virtual accounts:
        - 'charge.completed' - Payment received
        """
        event = event_data.get('event')
        data = event_data.get('data', {})

        if event == 'charge.completed':
            return {
                'status': 'success',
                'event': event,
                'transaction_id': data.get('id'),
                'tx_ref': data.get('tx_ref'),
                'amount': float(data.get('amount', 0)),
                'currency': data.get('currency'),
                'payment_type': data.get('payment_type'),
                'customer_email': data.get('customer', {}).get('email'),
                'meta': data.get('meta', {}),
                'raw_data': data
            }

        elif event == 'transfer.completed':
            return {
                'status': 'transfer_success',
                'event': event,
                'reference': data.get('reference'),
                'amount': float(data.get('amount', 0))
            }

        return {'status': 'ignored', 'event': event}

    # ==================== TRANSFERS (Withdrawals) ====================

    def initiate_transfer(self, amount, bank_code, account_number,
                          narration, reference=None, currency='NGN'):
        """Send money from Flutterwave balance to bank account"""
        if not reference:
            reference = f'TRF_{int(datetime.now().timestamp())}'

        payload = {
            'account_bank': bank_code,
            'account_number': account_number,
            'amount': amount,
            'narration': narration[:50],
            'currency': currency,
            'reference': reference,
            'callback_url': current_app.config.get('FLW_TRANSFER_WEBHOOK_URL', '')
        }

        result = self._api_call('POST', '/transfers', payload)

        if result.get('status') == 'success':
            return {
                'reference': reference,
                'transfer_id': result['data']['id'],
                'status': result['data']['status']
            }

        raise Exception(f"Transfer failed: {result.get('message')}")

    def get_transfer_status(self, transfer_id):
        """Check transfer status"""
        return self._api_call('GET', f'/transfers/{transfer_id}')

    def get_banks(self, country='NG'):
        """Get list of banks for transfers"""
        return self._api_call('GET', f'/banks/{country}')
