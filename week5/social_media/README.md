# Social Media App

A modern social media application built with React, TypeScript, Vite, and Firebase. Users can register, login, and post messages that are visible to everyone in real-time.

## Features

### User Authentication (Firebase Authentication)
- **Google Sign-In**: One-click authentication with Google accounts
- **Email/Password**: Traditional email and password authentication
- User registration and login functionality
- Display name support
- Protected routes for authenticated users
- Modern, secure authentication UI

### Message System (Firestore)
- Create, read, update, and delete messages
- Real-time message updates
- Message metadata (title, content, author, timestamps)
- Only message authors can edit/delete their own messages

### User Interface
- Clean, modern card-based design
- Responsive layout
- Real-time updates without page refresh
- Intuitive user experience

## Tech Stack

- **Frontend**: React 18 + TypeScript
- **Build Tool**: Vite
- **Styling**: Tailwind CSS
- **Backend**: Firebase
  - Authentication
  - Firestore Database
- **Icons**: Lucide React

## Getting Started

### Prerequisites

- Node.js (v16 or higher)
- npm or yarn
- Firebase project

### Installation

1. Clone the repository and navigate to the project directory:
   ```bash
   cd week5/social_media
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Set up Firebase:
   - Create a new Firebase project at [Firebase Console](https://console.firebase.google.com/)
   - Enable Authentication (Email/Password provider)
   - Create a Firestore database
   - Get your Firebase configuration

4. Configure Firebase:
   - Open `src/firebase.ts`
   - Replace the placeholder configuration with your actual Firebase config:
   ```typescript
   const firebaseConfig = {
     apiKey: "your-api-key",
     authDomain: "your-project.firebaseapp.com",
     projectId: "your-project-id",
     storageBucket: "your-project.appspot.com",
     messagingSenderId: "123456789",
     appId: "your-app-id"
   };
   ```

5. Set up Firestore Security Rules:
   ```javascript
   rules_version = '2';
   service cloud.firestore {
     match /databases/{database}/documents {
       match /messages/{document} {
         allow read: if true;
         allow create: if request.auth != null;
         allow update, delete: if request.auth != null && request.auth.uid == resource.data.authorId;
       }
     }
   }
   ```

6. Start the development server:
   ```bash
   npm run dev
   ```

7. Open your browser and navigate to `http://localhost:5173`

## Project Structure

```
src/
├── components/          # Reusable UI components
│   ├── Auth.tsx        # Authentication form
│   ├── MessageCard.tsx # Individual message display
│   ├── MessageForm.tsx # Message creation form
│   └── Navbar.tsx      # Navigation bar
├── contexts/           # React contexts
│   └── AuthContext.tsx # Authentication context
├── pages/              # Page components
│   └── HomePage.tsx    # Main application page
├── types/              # TypeScript type definitions
│   ├── Message.ts      # Message-related types
│   └── User.ts         # User-related types
├── utils/              # Utility functions
│   └── messageService.ts # Firestore operations
├── firebase.ts         # Firebase configuration
├── App.tsx            # Main app component
├── main.tsx           # Application entry point
└── index.css          # Global styles
```

## Available Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run preview` - Preview production build
- `npm run lint` - Run ESLint

## Features in Detail

### Authentication
- Users can register with email, password, and display name
- Users can sign in with email and password
- Authentication state is managed globally via React Context
- Protected routes ensure only authenticated users can post messages

### Messages
- **Create**: Authenticated users can post new messages
- **Read**: All users (authenticated and anonymous) can view all messages
- **Update**: Only message authors can edit their own messages
- **Delete**: Only message authors can delete their own messages
- **Real-time**: Messages update automatically without page refresh

### UI/UX
- Clean, modern design with Tailwind CSS
- Card-based layout for messages
- Responsive design works on all screen sizes
- Loading states and error handling
- Intuitive icons and visual feedback

## Security

- Firestore security rules ensure data integrity
- Only authenticated users can create messages
- Users can only modify their own messages
- All messages are publicly readable

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is open source and available under the MIT License.
