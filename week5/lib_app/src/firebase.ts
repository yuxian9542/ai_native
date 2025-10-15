import { initializeApp } from 'firebase/app';
import { getAuth } from 'firebase/auth';
import { getFirestore } from 'firebase/firestore';

// Your web app's Firebase configuration
// This configuration is obtained from Firebase CLI: firebase apps:sdkconfig web --project lib-mgmt-dynm
const firebaseConfig = {
  apiKey: "AIzaSyBu3Xtvbt7GOwIrvgUc2u4X99TBqqANWZs",
  authDomain: "lib-mgmt-dynm.firebaseapp.com",
  projectId: "lib-mgmt-dynm",
  storageBucket: "lib-mgmt-dynm.firebasestorage.app",
  messagingSenderId: "250620246471",
  appId: "1:250620246471:web:4f2a98a2bea03bdf2001e2",
  measurementId: "G-FPYCBSVPSF"
};

// Initialize Firebase
const app = initializeApp(firebaseConfig);

// Initialize Firebase Authentication and get a reference to the service
export const auth = getAuth(app);

// Initialize Cloud Firestore and get a reference to the service
export const db = getFirestore(app);

export default app;
