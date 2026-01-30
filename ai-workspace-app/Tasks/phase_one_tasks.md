1. **Extend base.html with placeholder for future chat input form**
   ```
   Add to base.html inside the sidebar card: a simple form with textarea for prompt, select for model (SDXL, Flux Klein, SD), button "Generate". Use Bootstrap form classes, no JS yet – just static HTML.
   ```

2. **Add offcanvas toggle for mobile (future-proof)**
   ```
   In base.html, add a navbar at top with button that opens the sidebar as Bootstrap offcanvas on screens <1024px. Keep sidebar visible by default on desktop.
   ```

3. **Create a matte texture background**
   ```
   Suggest CSS or generate a very small repeating dark matte texture description that I can create in 5 seconds in any image editor.
   ```

### Exit Criteria for Phase 1
- Flask app starts without errors  
- Page loads with dark Bootstrap theme  
- Layout: fixed left sidebar (Control Panel), flexible right canvas  
- Looks professional & non-distracting on large desktop screen  