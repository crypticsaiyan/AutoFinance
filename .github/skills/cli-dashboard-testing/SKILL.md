---
name: cli-dashboard-testing
description: Test and validate the Textual-based CLI dashboard components. Use when building or debugging CLI interface components.
license: MIT
---

# CLI Dashboard Testing Skill

This skill provides comprehensive testing strategies for the Textual-based CLI dashboard.

## Testing Strategy

### 1. Component Testing

Test each Textual component in isolation:

```python
import pytest
from textual.widgets import Static
from cli.components.charts import ChartWidget

@pytest.mark.asyncio
async def test_chart_widget_rendering():
    """Test that chart widget renders correctly."""
    widget = ChartWidget()
    
    # Mount widget in test app
    async with widget.app:
        await widget.app._process_messages()
        
        # Verify widget state
        assert widget.is_mounted
        assert widget.display
        
        # Test data update
        test_data = [1, 2, 3, 4, 5]
        widget.update_data(test_data)
        
        # Verify data is set
        assert widget.data == test_data
```

### 2. Visual Regression Testing

Take snapshots of the dashboard for visual comparison:

```python
from textual.pilot import Pilot

async def test_dashboard_snapshot(snap_compare):
    """Test dashboard visual appearance."""
    from cli.dashboard_textual import AutoFinanceDashboard
    
    app = AutoFinanceDashboard()
    async with app.run_test() as pilot:
        # Wait for initial render
        await pilot.pause()
        
        # Take snapshot
        assert await snap_compare(app)
```

### 3. Interaction Testing

Test keyboard shortcuts and user interactions:

```python
async def test_keyboard_shortcuts():
    """Test keyboard shortcuts work correctly."""
    from cli.dashboard_textual import AutoFinanceDashboard
    
    app = AutoFinanceDashboard()
    async with app.run_test() as pilot:
        # Test quit shortcut
        await pilot.press("ctrl+q")
        assert app.is_exiting
        
        # Test search shortcut
        await pilot.press("/")
        assert app.search_box.has_focus
        
        # Test tab navigation
        await pilot.press("tab")
        assert app.next_widget_has_focus()
```

### 4. Data Fetching Tests

Mock API calls and test data updates:

```python
from unittest.mock import patch, AsyncMock

@pytest.mark.asyncio
async def test_portfolio_data_fetch():
    """Test portfolio data fetching and display."""
    from cli.components.portfolio import PortfolioWidget
    
    # Mock data fetcher
    mock_data = {
        'total_value': 100000,
        'positions': [
            {'symbol': 'AAPL', 'value': 50000},
            {'symbol': 'GOOGL', 'value': 50000}
        ]
    }
    
    with patch('cli.data.fetchers.fetch_portfolio_data', 
               new=AsyncMock(return_value=mock_data)):
        widget = PortfolioWidget()
        await widget.fetch_data()
        
        # Verify data is displayed
        assert widget.total_value == 100000
        assert len(widget.positions) == 2
```

### 5. Performance Testing

Test rendering performance:

```python
import time

async def test_chart_rendering_performance():
    """Test that charts render within acceptable time."""
    from cli.components.charts import ChartWidget
    
    widget = ChartWidget()
    large_dataset = list(range(10000))
    
    start = time.time()
    widget.update_data(large_dataset)
    await widget.refresh()
    elapsed = time.time() - start
    
    # Should render in less than 100ms
    assert elapsed < 0.1
```

### 6. Error Handling Tests

Test error states and recovery:

```python
@pytest.mark.asyncio
async def test_api_error_handling():
    """Test dashboard handles API errors gracefully."""
    from cli.dashboard_textual import AutoFinanceDashboard
    
    with patch('cli.data.fetchers.fetch_market_data',
               side_effect=Exception("API Error")):
        app = AutoFinanceDashboard()
        async with app.run_test() as pilot:
            await pilot.pause()
            
            # Verify error message is displayed
            assert "Error" in app.screen.render()
            
            # Verify app is still responsive
            await pilot.press("ctrl+r")  # Retry
            assert not app.is_frozen
```

## Testing Checklist

### Visual Tests
- [ ] All widgets render correctly
- [ ] Colors are correct (green/red for gains/losses)
- [ ] Charts display without artifacts
- [ ] Text is readable at different terminal sizes
- [ ] Loading spinners appear during data fetch

### Interaction Tests
- [ ] All keyboard shortcuts work
- [ ] Tab navigation works properly
- [ ] Mouse clicks are handled (if enabled)
- [ ] Search functionality works
- [ ] Modal dialogs can be opened and closed

### Data Tests
- [ ] Data fetches successfully
- [ ] Data updates trigger UI refresh
- [ ] Stale data is handled
- [ ] Empty data states are handled
- [ ] Large datasets don't cause slowdown

### Error Tests
- [ ] API errors show user-friendly messages
- [ ] Network errors are recoverable
- [ ] Invalid data doesn't crash app
- [ ] Errors are logged properly

### Performance Tests
- [ ] Initial load time < 2 seconds
- [ ] Chart rendering < 100ms
- [ ] Memory usage is stable
- [ ] No memory leaks during long runs
- [ ] 60fps maintained during animations

## Running Tests

```bash
# Run all CLI tests
pytest tests/test_cli*.py -v

# Run with coverage
pytest tests/test_cli*.py --cov=cli --cov-report=html

# Run visual regression tests
pytest tests/test_cli*.py --snapshot-update

# Run performance tests
pytest tests/test_cli*.py -k performance --benchmark

# Run in watch mode during development
ptw tests/test_cli*.py
```

## Manual Testing Script

Create a manual test script for comprehensive testing:

```python
#!/usr/bin/env python3
"""Manual testing script for CLI dashboard."""

import asyncio
from cli.dashboard_textual import AutoFinanceDashboard

async def manual_test():
    """Run manual test scenarios."""
    app = AutoFinanceDashboard()
    
    print("Starting manual test...")
    print("1. Verify all widgets are visible")
    print("2. Test keyboard shortcuts:")
    print("   - Ctrl+Q: Quit")
    print("   - /: Search")
    print("   - Tab: Navigate")
    print("3. Check data updates")
    print("4. Test error handling (disconnect network)")
    
    await app.run_async()

if __name__ == "__main__":
    asyncio.run(manual_test())
```

## Debugging Tips

1. **Use Textual Devtools**: `textual console` for live debugging
2. **Enable Debug Mode**: Set `DEBUG=1` environment variable
3. **Log Rendering**: Use `app.log()` to debug render issues
4. **Inspect Widget Tree**: Use `app.tree` to see widget hierarchy
5. **Profile Performance**: Use `textual --profile` to find bottlenecks
