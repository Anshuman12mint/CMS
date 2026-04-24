# UI_USING_HTML

Static HTML UI structure for the CMS plan.

## Files

- `index.html` - login screen wired to the backend
- `meetings.html` - meeting center with join and chat
- `admin/dashboard.html` - admin/staff overview with live summary data
- `admin/students.html` - student management with live detail panel
- `admin/academics.html` - courses and subjects with live data
- `admin/operations.html` - attendance, fees, marks, and meetings summary
- `teacher/workspace.html` - teacher role UI with live assignments and meetings
- `student/portal.html` - student role UI with live attendance, fees, marks, and meetings
- `assets/css/styles.css` - shared styles
- `assets/js/core.js` - auth/session/api layer
- `assets/js/*.js` - page-specific loaders

## How to open

Serve the folder with a local static server, then open `index.html`.

Example:

```powershell
python -m http.server 8081 --directory D:\CMS\UI_USING_HTML
```
