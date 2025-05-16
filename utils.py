# --- utils.py ---
# Placeholder for any utility functions like date conversion, formatting, caching, etc.
def annualized_days(expiration_date, current_date):
    delta = (expiration_date - current_date).days
    return delta / 365