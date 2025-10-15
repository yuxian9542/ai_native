# Firebase Setup Guide

This guide will help you set up Firebase for the Social Media App.

## Step 1: Create a Firebase Project

1. Go to [Firebase Console](https://console.firebase.google.com/)
2. Click "Create a project" or "Add project"
3. Enter a project name (e.g., "social-media-app")
4. Choose whether to enable Google Analytics (optional)
5. Click "Create project"

## Step 2: Enable Authentication

1. In your Firebase project, go to "Authentication" in the left sidebar
2. Click "Get started"
3. Go to the "Sign-in method" tab
4. Enable "Email/Password" provider
5. Enable "Google" provider
   - Click on "Google" in the providers list
   - Toggle "Enable"
   - Add your project's support email
   - Click "Save"
6. Click "Save" on the main sign-in methods page

## Step 3: Create Firestore Database

1. In your Firebase project, go to "Firestore Database" in the left sidebar
2. Click "Create database"
3. Choose "Start in test mode" (for development)
4. Select a location for your database
5. Click "Done"

## Step 4: Set Up Security Rules

1. In Firestore Database, go to the "Rules" tab
2. Replace the default rules with:

```javascript
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    // Messages rules
    match /messages/{document} {
      allow read: if true;
      allow create: if request.auth != null;
      allow update, delete: if request.auth != null && request.auth.uid == resource.data.authorId;
    }
    
    // Comments rules
    match /comments/{document} {
      allow read: if true;
      allow create: if request.auth != null;
      allow update, delete: if request.auth != null && request.auth.uid == resource.data.authorId;
    }
    
    // Likes rules
    match /likes/{document} {
      allow read: if true;
      allow create: if request.auth != null;
      allow delete: if request.auth != null && request.auth.uid == resource.data.userId;
    }
  }
}
```

3. Click "Publish"

## Step 5: Get Firebase Configuration

1. In your Firebase project, go to "Project settings" (gear icon)
2. Scroll down to "Your apps" section
3. Click "Add app" and select the web icon (</>)
4. Register your app with a nickname (e.g., "social-media-web")
5. Copy the Firebase configuration object

## Step 6: Update Your App Configuration

1. Open `src/firebase.ts` in your project
2. Replace the placeholder configuration with your actual Firebase config:

```typescript
const firebaseConfig = {
  apiKey: "your-actual-api-key",
  authDomain: "your-project.firebaseapp.com",
  projectId: "your-actual-project-id",
  storageBucket: "your-project.appspot.com",
  messagingSenderId: "your-actual-sender-id",
  appId: "your-actual-app-id"
};
```

## Step 7: Test Your Setup

1. Run `npm run dev` to start the development server
2. Open your browser and go to `http://localhost:5173`
3. Try to register a new account
4. Try to post a message
5. Check your Firestore database to see if the message was created

## Troubleshooting

### Common Issues

1. **Authentication not working**: Make sure you've enabled Email/Password authentication in Firebase Console
2. **Database permission denied**: Check your Firestore security rules
3. **Configuration errors**: Double-check your Firebase config in `src/firebase.ts`
4. **CORS errors**: Make sure your domain is added to authorized domains in Firebase Console

### Security Rules Explanation

- `allow read: if true` - Anyone can read messages (public feed)
- `allow create: if request.auth != null` - Only authenticated users can create messages
- `allow update, delete: if request.auth != null && request.auth.uid == resource.data.authorId` - Only the message author can edit/delete their own messages

## Production Considerations

For production deployment:

1. Update Firestore security rules to be more restrictive if needed
2. Add your production domain to authorized domains in Firebase Console
3. Consider enabling additional authentication providers
4. Set up proper error monitoring and logging
5. Configure Firebase hosting for deployment

## Support

If you encounter issues:

1. Check the Firebase Console for error logs
2. Check the browser console for client-side errors
3. Verify your Firebase configuration
4. Ensure all required services are enabled
