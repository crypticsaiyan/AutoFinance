---
name: financial-data-validation
description: Validates financial data from MCP servers for accuracy and completeness. Use when checking market data, price quotes, or financial metrics.
license: MIT
---

# Financial Data Validation Skill

This skill helps validate financial data returned from MCP servers to ensure accuracy and completeness.

## Validation Process

1. **Verify Data Structure**
   - Check that all required fields are present
   - Validate data types match expectations
   - Ensure nested objects are properly formatted

2. **Validate Financial Values**
   - Verify prices are positive numbers
   - Check that percentages are in valid ranges (-100% to +∞)
   - Ensure volumes are non-negative
   - Validate that market cap values are reasonable

3. **Check Data Freshness**
   - Verify timestamps are recent (within market hours or last close)
   - Ensure data is not stale (check update frequency)
   - Validate timezone information is correct

4. **Cross-Reference Validation**
   - Compare values across multiple data sources if available
   - Verify calculated metrics match raw data
   - Check for anomalies or outliers

5. **Market-Specific Validation**
   - Verify ticker symbols are valid
   - Check that market hours are respected
   - Ensure currency codes are ISO 4217 compliant
   - Validate exchange identifiers

## Example Validation Checks

```python
def validate_stock_quote(quote_data):
    """Validate a stock quote from market data server."""
    required_fields = ['symbol', 'price', 'volume', 'timestamp']
    
    # Check required fields
    for field in required_fields:
        assert field in quote_data, f"Missing required field: {field}"
    
    # Validate values
    assert quote_data['price'] > 0, "Price must be positive"
    assert quote_data['volume'] >= 0, "Volume cannot be negative"
    
    # Check timestamp is recent
    timestamp = datetime.fromisoformat(quote_data['timestamp'])
    assert datetime.now() - timestamp < timedelta(minutes=15), "Data is stale"
    
    return True
```

## Common Data Issues

- **Missing fields**: Always check for null/undefined values
- **Incorrect precision**: Financial data should have appropriate decimal places
- **Currency mismatches**: Ensure all values use consistent currency
- **Timezone errors**: Always use UTC or specify timezone explicitly
- **Split/dividend adjustments**: Verify if prices are adjusted

## Error Handling

When validation fails:
1. Log the specific validation error
2. Include the problematic data in error message
3. Suggest corrective actions
4. Never proceed with invalid data
5. Consider fallback data sources
