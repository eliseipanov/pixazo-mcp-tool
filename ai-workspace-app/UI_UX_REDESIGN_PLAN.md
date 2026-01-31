# UI/UX Redesign Plan

## Overview

Based on your feedback, here's the finalized design:

## Layout Structure

### Left Control Panel (Resizable: 320px - 420px)
- Navigation Menu (Collapsible with header, state saved)
- Prompt Form (Always visible)
- Workspace Actions (Save, Import, Export)
- Chat Toggle Button (ON/OFF)

### Main Canvas Area (Full width)
- Generated Images Grid
- Empty state with "Generate your first image" message

### Floating Chat Window (when toggle is ON)
- Draggable by header
- Collapsible to header only
- Resizable (with min/max limits)
- Close button
- Chat messages (scrollable)
- Input field and Send button
- Position saved in localStorage

## ASCII Diagram

```
+----------------+----------------------------------------------+
| Left Panel     | Main Canvas Area                           |
| (320-420px)   |                                          |
|                |                                          |
| +------------+ |  +----------------------------------------+  |
| | Navigation | |  | Generated Images Grid              |  |
| | Menu      | |  | - Thumbnail grid                  |  |
| | [v]       | |  | - Click to open full-size modal   |  |
| |           | |  |                                |  |
| | [Home]    | |  +----------------------------------------+  |
| | [Workspcs]| |                                          |
| | [Themes]  | |                                          |
| | [Styles]  | |                                          |
| | [Models]  | |                                          |
| +------------+ |                                          |
|                |                                          |
| +------------+ |  +----------------------------------------+  |
| | Prompt    | |  | Chat with AI [-] [x]              |  |
| | Form      | |  |------------------------------------|  |
| |           | |  | Chat Messages (scrollable)         |  |
| | [Main]    | |  | User: Help me improve my prompt    |  |
| | [Negative] | |  | AI: Sure! What's your prompt?      |  |
| | [Theme]    | |  |------------------------------------|  |
| | [Style]    | |  | [Input prompt...] [Send]           |  |
| | [Model]    | |  +----------------------------------------+  |
| | [Advanced] | |                                          |
| | [Generate] | |                                          |
| +------------+ |                                          |
|                |                                          |
| +------------+ |                                          |
| | Workspace  | |                                          |
| | Actions    | |                                          |
| | [Save]     | |                                          |
| | [Import]   | |                                          |
| | [Export]   | |                                          |
| +------------+ |                                          |
|                |                                          |
| +------------+ |                                          |
| | [Chat]     | |                                          |
| | Toggle     | |                                          |
| | Button     | |                                          |
| +------------+ |                                          |
+----------------+----------------------------------------------+
```

## Control Panel Components

### Navigation Menu (Collapsible)
- Header with toggle button [v]/[^]
- State saved in localStorage (collapsed/visible)
- Items:
  - Home: Return to dashboard
  - Workspaces: List and manage workspaces
  - Themes: List and manage themes
  - Styles: List and manage styles
  - Models: List and manage AI models (superuser only)

### Prompt Form (Always Visible)
- Main Prompt: Textarea for primary prompt
- Negative Prompt: Textarea for negative prompt
- Theme Select: Dropdown to select theme
- Style Select: Dropdown to select style
- Model Select: Dropdown to select model
- Advanced Parameters: Collapsible section with:
  - Width/Height
  - Steps
  - Guidance Scale
  - Seed
- Generate Button: Triggers image generation

### Workspace Actions
- Save Workspace: Save current workspace state
- Import Workspace: Import workspace from .GZ archive
- Export Workspace: Export workspace to .GZ archive

### Chat Toggle Button
- Icon: Chat bubble icon
- State: ON/OFF toggle
- Behavior: Shows/hides floating chat window

## Floating Chat Window

### Features
- Draggable: Can be moved by dragging header
- Collapsible: Can be minimized to header only
- Resizable: Can be resized (with min/max limits)
- Close Button: Closes window (toggle OFF)
- Always on Top: Stays above other content
- Position Saved: Remembers position in localStorage
- First Open: Centered on screen
- Subsequent Opens: At last saved position
- Streaming Responses: Real-time display of AI responses

### Layout
```
+----------------------------------------+
| Chat with AI [-] [x]  <- Draggable header|
+----------------------------------------+
| Chat Messages (scrollable)             |
| User: Help me improve my prompt        |
| AI: Sure! What's your prompt?          |
|                                        |
| User: A cat in space                   |
| AI: Try: "A majestic cat floating in   |
|     zero gravity, surrounded by        |
|     colorful nebulae and stars..."     |
+----------------------------------------+
| [Input prompt...] [Send]               |
+----------------------------------------+
```

### Collapsed State
```
+----------------------------------------+
| Chat with AI [+] [x]  <- Click [+] to expand|
+----------------------------------------+
```

## Implementation Plan

### Phase 1: Layout Restructure
1. Create new sidebar layout in templates/workspaces/view.html
2. Add resizable sidebar (320px - 420px)
3. Add collapsible navigation menu with header
4. Add prompt form (always visible)
5. Add workspace actions section
6. Add chat toggle button
7. Expand main canvas area
8. Update CSS for new layout

### Phase 2: Chat Interface
1. Create floating chat window component
2. Implement drag-and-drop functionality
3. Implement resize functionality (with min/max limits)
4. Add collapse/expand functionality
5. Implement toggle button behavior
6. Implement chat API integration
7. Add streaming response support
8. Save position/state/size in localStorage

### Phase 3: Polish
1. Add smooth transitions
2. Improve responsive design (desktop first)
3. Add keyboard shortcuts
4. Save UI state (sidebar width, nav menu state, etc.)
5. Test on different screen sizes

## Technical Details

### CSS Requirements
- Sidebar: Resizable 320px-420px, full height
- Canvas: Flex-grow, full height
- Chat window: Fixed position, z-index high
- Drag handle: Header of chat window
- Resize handle: Bottom-right corner of chat window
- Transitions: Smooth animations for show/hide/collapse

### JavaScript Requirements
- Sidebar resize: Mouse events on resize handle
- Drag-and-drop: Mouse events (mousedown, mousemove, mouseup)
- Resize: Mouse events on resize handle
- Toggle: Simple boolean state
- localStorage: Save chat position, size, state; sidebar width; nav menu state
- Streaming: EventSource or fetch with ReadableStream

### localStorage Keys
- `chatWindow_position`: {x, y}
- `chatWindow_size`: {width, height}
- `chatWindow_collapsed`: boolean
- `chatWindow_visible`: boolean
- `sidebar_width`: number (320-420)
- `navMenu_collapsed`: boolean

### API Endpoints Needed
- POST /api/chat/completions - Send chat message
- POST /api/workspaces/<id>/save - Save workspace
- POST /api/workspaces/import - Import workspace
- GET /api/workspaces/<id>/export - Export workspace

## Constraints

### Sidebar
- Min width: 320px
- Max width: 420px
- Default width: 320px
- State saved in localStorage

### Chat Window
- Min width: 300px
- Min height: 200px
- Max width: 600px
- Max height: 800px
- Default size: 400x500px
- Default position: Centered on first open
- Subsequent position: Last saved position
- Collapsed state: Header only (height ~40px)

### Mobile Support
- Desktop first strategy
- Simplified mobile view to be implemented later

## Next Steps

Ready to implement. Will switch to Code mode to:
1. Update templates/workspaces/view.html with new layout
2. Add CSS for resizable sidebar and floating chat window
3. Add JavaScript for drag, resize, toggle, and state management
4. Implement chat API integration with streaming
5. Test all functionality
