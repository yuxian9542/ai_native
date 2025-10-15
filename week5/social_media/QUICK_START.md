# Quick Start Guide

## Prerequisites
- Node.js (v16 or higher)
- Firebase account

## Setup Steps

1. **Install dependencies:**
   ```bash
   npm install
   ```

2. **Configure Firebase:**
   - Follow the detailed guide in `FIREBASE_SETUP.md`
   - Update `src/firebase.ts` with your Firebase configuration

3. **Start development server:**
   ```bash
   npm run dev
   ```

4. **Open your browser:**
   - Go to `http://localhost:5173`
   - Register a new account
   - Start posting messages!

## Features to Test

### Authentication
- [ ] Sign in with Google (one-click authentication)
- [ ] Register a new account with email and password
- [ ] Sign in with existing email account
- [ ] Sign out

### Messages
- [ ] Post a new message (requires login)
- [ ] View all messages (works without login)
- [ ] Edit your own message
- [ ] Delete your own message
- [ ] Try to edit/delete someone else's message (should fail)

### Real-time Updates
- [ ] Open the app in two browser tabs
- [ ] Post a message in one tab
- [ ] Verify it appears in the other tab automatically

## Troubleshooting

If you see errors:
1. Check that Firebase is properly configured
2. Ensure Firestore security rules are set up correctly
3. Check browser console for error messages
4. Verify all dependencies are installed

## Next Steps

- Customize the UI styling
- Add more features like comments or likes
- Deploy to Firebase Hosting
- Add user profiles
