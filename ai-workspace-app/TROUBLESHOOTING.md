# Troubleshooting Guide

## Registration/Login Issues

### Issue: "After Registration process it appears I have no Account"

If you successfully registered but can't see your account or login, follow these steps:

### 1. Verify Database

Run the database test script to verify your account was created:

```bash
/var/www/pixazo/.venv/bin/python ai-workspace-app/test_db.py
```

This will show all users in the database. You should see your username listed.

### 2. Check Authentication Status

Visit the debug endpoint to check your authentication status:

```
http://127.0.0.1:5000/debug
```

This will show:
- Whether you're authenticated
- Your user ID and username (if logged in)
- Total number of users in database

### 3. Clear Browser Cookies

Sometimes session cookies can cause issues:

1. Open browser DevTools (F12)
2. Go to Application/Storage tab
3. Clear cookies for localhost/127.0.0.1
4. Try logging in again

### 4. Check Flash Messages

After registration, you should see a success message:
- "Registration successful! Please login."

If you see an error message, note it down for troubleshooting.

### 5. Verify Login Credentials

Make sure you're using the correct credentials:
- Username: The username you registered with (case-sensitive)
- Password: The password you set during registration

### 6. Test with Test Account

Try logging in with the test account:
- Username: `testuser`
- Password: `testpass123`

If this works, your database and authentication system are functioning correctly.

### 7. Check Browser Console

Open browser DevTools (F12) and check the Console tab for any JavaScript errors.

### 8. Restart the Application

Sometimes restarting the Flask app can help:

```bash
# Stop the current app (Ctrl+C)
# Restart it
/var/www/pixazo/.venv/bin/python ai-workspace-app/app.py
```

### 9. Check Database File Permissions

Ensure the database file is writable:

```bash
ls -la ai-workspace-app/db/workspace.db
```

The file should be readable and writable by your user.

### 10. Reinitialize Database (Last Resort)

If all else fails, you can reinitialize the database:

```bash
# Remove existing database
rm ai-workspace-app/db/workspace.db

# Reinitialize with sample data
/var/www/pixazo/.venv/bin/python ai-workspace-app/init_db.py
```

**Warning:** This will delete all existing data including your registered account.

## Common Error Messages

### "All fields are required"
- Make sure you filled in username, email, and password fields
- Check that password confirmation field is also filled

### "Passwords do not match"
- Ensure password and confirm password fields are identical
- Check for extra spaces

### "Password must be at least 6 characters"
- Your password needs to be 6+ characters long

### "Username already exists"
- Choose a different username
- Usernames are case-sensitive

### "Email already registered"
- This email is already in use
- Use a different email address

### "Invalid username or password"
- Check your username spelling (case-sensitive)
- Verify your password is correct
- Try resetting your password (not implemented yet)

## Getting Help

If you continue to have issues:

1. Check the Flask app terminal output for error messages
2. Visit `/debug` endpoint to see authentication status
3. Run `test_db.py` to verify database integrity
4. Check browser console for JavaScript errors

## Database Location

The database is located at:
```
ai-workspace-app/db/workspace.db
```

You can view this file in VSCode with the SQLite extension to verify your account exists.
