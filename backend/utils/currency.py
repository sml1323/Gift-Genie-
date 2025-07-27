"""
Currency conversion utilities for Gift Genie
Handles USD-KRW conversion with static rates
"""

from typing import Literal, Dict, Tuple
import logging

logger = logging.getLogger(__name__)

# Static exchange rate for MVP (실제 서비스에서는 API로 실시간 환율 사용)
USD_TO_KRW_RATE = 1300
KRW_TO_USD_RATE = 1 / USD_TO_KRW_RATE

CurrencyType = Literal["USD", "KRW"]

def convert_currency(amount: int, from_currency: CurrencyType, to_currency: CurrencyType) -> int:
    """
    Convert amount between USD and KRW
    
    Args:
        amount: Amount to convert
        from_currency: Source currency
        to_currency: Target currency
        
    Returns:
        Converted amount as integer
    """
    if from_currency == to_currency:
        return amount
    
    if from_currency == "USD" and to_currency == "KRW":
        return int(amount * USD_TO_KRW_RATE)
    elif from_currency == "KRW" and to_currency == "USD":
        return int(amount * KRW_TO_USD_RATE)
    else:
        raise ValueError(f"Unsupported currency conversion: {from_currency} to {to_currency}")

def format_currency(amount: int, currency: CurrencyType) -> str:
    """
    Format currency for display
    
    Args:
        amount: Amount to format
        currency: Currency type
        
    Returns:
        Formatted currency string
    """
    if currency == "KRW":
        return f"₩{amount:,}"
    elif currency == "USD":
        return f"${amount}"
    else:
        raise ValueError(f"Unsupported currency: {currency}")

def get_dual_currency_display(amount: int, primary_currency: CurrencyType) -> Dict[str, str]:
    """
    Get dual currency display (primary + converted secondary)
    
    Args:
        amount: Amount in primary currency
        primary_currency: Primary currency
        
    Returns:
        Dict with primary and secondary currency displays
    """
    if primary_currency == "KRW":
        secondary_currency = "USD"
        secondary_amount = convert_currency(amount, "KRW", "USD")
    else:
        secondary_currency = "KRW"
        secondary_amount = convert_currency(amount, "USD", "KRW")
    
    return {
        "primary": format_currency(amount, primary_currency),
        "secondary": format_currency(secondary_amount, secondary_currency),
        "primary_currency": primary_currency,
        "secondary_currency": secondary_currency
    }

def normalize_budget_to_usd(budget_min: int, budget_max: int, currency: CurrencyType) -> Tuple[int, int]:
    """
    Normalize budget range to USD for internal processing
    Used for maintaining compatibility with existing USD-based logic
    
    Args:
        budget_min: Minimum budget
        budget_max: Maximum budget  
        currency: Budget currency
        
    Returns:
        Tuple of (budget_min_usd, budget_max_usd)
    """
    if currency == "USD":
        return budget_min, budget_max
    elif currency == "KRW":
        budget_min_usd = convert_currency(budget_min, "KRW", "USD")
        budget_max_usd = convert_currency(budget_max, "KRW", "USD")
        return budget_min_usd, budget_max_usd
    else:
        raise ValueError(f"Unsupported currency: {currency}")

def enhance_price_with_currency(price: int, target_currency: CurrencyType = "KRW") -> Dict:
    """
    Enhance price data with currency information
    
    Args:
        price: Price amount (assumed USD for legacy compatibility)
        target_currency: Target currency for display
        
    Returns:
        Dict with enhanced price information
    """
    # Legacy prices are assumed to be USD
    source_currency = "USD"
    
    if target_currency == source_currency:
        converted_price = price
    else:
        converted_price = convert_currency(price, source_currency, target_currency)
    
    return {
        "estimated_price": converted_price,
        "currency": target_currency,
        "price_display": format_currency(converted_price, target_currency)
    }

# Validation helpers
def validate_currency_amount(amount: int, currency: CurrencyType) -> bool:
    """Validate if amount is reasonable for the currency"""
    if currency == "USD":
        return 1 <= amount <= 10000  # $1 to $10,000
    elif currency == "KRW":
        return 1000 <= amount <= 13000000  # ₩1,000 to ₩13,000,000
    return False

def get_currency_bounds(currency: CurrencyType) -> Dict[str, int]:
    """Get reasonable min/max bounds for currency"""
    if currency == "USD":
        return {"min": 1, "max": 10000, "default_min": 10, "default_max": 200}
    elif currency == "KRW":
        return {"min": 1000, "max": 13000000, "default_min": 13000, "default_max": 260000}
    else:
        raise ValueError(f"Unsupported currency: {currency}")