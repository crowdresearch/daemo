from crowdsourcing.exceptions import InsufficientFunds


def validate_account_balance(request, price, num_rows):
    requester_account = request.user.userprofile.financial_accounts.filter(type='requester', is_active=True).first()
    if price * num_rows > requester_account.balance:
        raise InsufficientFunds
