def calculate_commission(sales_amount: float, commission_rate: float) -> float:
    """
    Calculate the commission for a given sales amount and commission rate.

    Args:
        sales_amount (float): The total sales amount.
        commission_rate (float): The commission rate as a percentage.

    Returns:
        float: The calculated commission.
    """
    return sales_amount * (commission_rate / 100)

print(calculate_commission(100, 0.5))  # Example usage