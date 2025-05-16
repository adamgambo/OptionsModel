# --- strategies/custom_strategy.py ---
def custom_strategy(legs):
    """
    Accepts a list of Leg objects representing a user-defined custom strategy.
    Validates a custom strategy with 2 to 8 user-defined legs and returns both the summarized legs and the net premium.

    Parameters:
    legs (list): List of Leg dataclass instances.

    Returns:
    tuple: (list of summarized legs, net premium)
    """
    if not isinstance(legs, list):
        raise ValueError("Input must be a list of Leg instances.")
    if not (2 <= len(legs) <= 8):
        raise ValueError("Custom strategy must have between 2 and 8 legs.")
    
    required_attrs = ['type', 'position', 'price']
    for leg in legs:
        for attr in required_attrs:
            if not hasattr(leg, attr):
                raise ValueError(f"Each leg must have a '{attr}' attribute.")

    # Compute total premium (net debit or credit)
    net_premium = 0
    summarized_legs = []
    for leg in legs:
        leg_summary = {
            "type": leg.type,
            "position": leg.position,
            "strike": getattr(leg, "strike", None),
            "expiry": getattr(leg, "expiry", None),
            "price": leg.price,
            "quantity": getattr(leg, "quantity", 1)
        }
        premium_effect = leg.price * leg_summary["quantity"]
        if leg.position == "long":
            net_premium -= premium_effect
        elif leg.position == "short":
            net_premium += premium_effect
        summarized_legs.append(leg_summary)

    return summarized_legs, net_premium