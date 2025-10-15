import { initializeApp } from 'firebase/app';
import { getAuth, GoogleAuthProvider, PhoneAuthProvider } from 'firebase/auth';
import { getFirestore } from 'firebase/firestore';

const firebaseConfig = {
  apiKey: "AIzaSyBddiCB-1f5__KZz3oazSE746EFkONaWJA",
  authDomain: "social-media-f01e2.firebaseapp.com",
  projectId: "social-media-f01e2",
  storageBucket: "social-media-f01e2.firebasestorage.app",
  messagingSenderId: "655977776505",
  appId: "1:655977776505:web:8dafd4950a8d9ac9e55ba8",
  measurementId: "G-08SV9BQEWT"
};

// Initialize Firebase
const app = initializeApp(firebaseConfig);

// Initialize Firebase Authentication and get a reference to the service
export const auth = getAuth(app);

// Initialize Cloud Firestore and get a reference to the service
export const db = getFirestore(app);

// Initialize Google Auth Provider
export const googleProvider = new GoogleAuthProvider();

// Initialize Phone Auth Provider
export const phoneProvider = new PhoneAuthProvider(auth);

export default app;
