---
applyTo: "cli/**/*.py"
---

# CLI Dashboard Development Instructions

## Textual Framework Guidelines
- Use Textual widgets for all UI components
- Implement reactive properties for data binding
- Handle keyboard events with proper key combinations
- Ensure 60fps rendering for smooth animations

## Component Architecture
- Each component should be in its own file under `components/`
- Implement proper lifecycle methods (on_mount, on_unmount)
- Use message passing for component communication
- Keep components decoupled and reusable

## Data Fetching
- Use async data fetchers from `data/fetchers.py`
- Implement proper error handling for API failures
- Cache data appropriately to reduce API calls
- Show loading states during data fetches

## Visual Design
- Use consistent color scheme:
  - Green for positive changes/gains
  - Red for negative changes/losses
  - Blue for neutral information
  - Yellow for warnings
- Include proper padding and spacing
- Use Unicode characters for charts and indicators
- Implement responsive layouts for different terminal sizes

## Keyboard Shortcuts
- Document all keyboard shortcuts in help text
- Use intuitive key combinations (Ctrl+Q for quit, etc.)
- Implement modal dialogs for confirmations
- Support vim-style navigation where appropriate

## Real-time Updates
- Implement efficient data refresh mechanisms
- Use reactive properties to update UI automatically
- Avoid blocking the UI thread
- Show timestamps for last update

## Error Handling
- Display user-friendly error messages
- Include retry mechanisms for transient failures
- Log errors to file for debugging
- Never crash the application on errors

## Performance
- Optimize rendering for large datasets
- Use pagination for lists
- Implement virtual scrolling for long tables
- Profile rendering performance regularly
