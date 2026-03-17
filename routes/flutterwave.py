@flutterwave_bp.route('/test/create-va', methods=['GET'])
def test_create_va():
    """Quick test endpoint for creating virtual account"""
    import requests

    secret_key = current_app.config.get('FLUTTERWAVE_TEST_SECRET_KEY')

    url = "https://api.flutterwave.com/v3/virtual-account-numbers"
    headers = {
        "Authorization": f"Bearer {secret_key}",
        "Content-Type": "application/json"
    }
    data = {
        "email": "test@example.com",
        "amount": 1000,
        "currency": "NGN",
        "tx_ref": f"test_{int(datetime.now().timestamp())}",
        "is_permanent": False
    }

    try:
        resp = requests.post(url, json=data, headers=headers)
        result = resp.json()
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
