import { initializeApp } from 'firebase/app';
import { getAuth, GoogleAuthProvider } from 'firebase/auth';
import { getAnalytics, isSupported } from 'firebase/analytics';

// Firebase configuration
const firebaseConfig = {
  apiKey: "AIzaSyDFN-2UF6s6iG8l4nKgjTEyHhrEUBOpW1U",
  authDomain: "cyber-intelligence-platform.firebaseapp.com",
  projectId: "cyber-intelligence-platform",
  storageBucket: "cyber-intelligence-platform.firebasestorage.app",
  messagingSenderId: "320997353705",
  appId: "1:320997353705:web:3e4428040e07dc0201e878",
  measurementId: "G-JEHPDLWRWJ"
};

// Initialize Firebase
const app = initializeApp(firebaseConfig);

// Initialize Firebase Authentication and get a reference to the service
export const auth = getAuth(app);

// Initialize Google Auth Provider
export const googleProvider = new GoogleAuthProvider();

// Configure Google Auth Provider
googleProvider.setCustomParameters({
  prompt: 'select_account'
});

// Initialize Analytics (only in browser and if supported)
let analytics: any = null;
if (typeof window !== 'undefined') {
  isSupported().then((supported) => {
    if (supported) {
      analytics = getAnalytics(app);
    }
  });
}
export { analytics };

export default app;
