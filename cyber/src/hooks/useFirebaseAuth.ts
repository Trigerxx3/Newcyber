import { useState, useEffect } from 'react';
import { 
  User,
  signInWithPopup, 
  signOut as firebaseSignOut,
  onAuthStateChanged,
  getIdToken
} from 'firebase/auth';
import { auth, googleProvider } from '@/lib/firebase';

export interface FirebaseAuthState {
  user: User | null;
  loading: boolean;
  error: string | null;
}

export function useFirebaseAuth() {
  const [authState, setAuthState] = useState<FirebaseAuthState>({
    user: null,
    loading: true,
    error: null
  });

  useEffect(() => {
    const unsubscribe = onAuthStateChanged(auth, 
      (user) => {
        setAuthState(prev => ({
          ...prev,
          user,
          loading: false
        }));
      },
      (error) => {
        setAuthState(prev => ({
          ...prev,
          error: error.message,
          loading: false
        }));
      }
    );

    return () => unsubscribe();
  }, []);

  const signInWithGoogle = async () => {
    try {
      setAuthState(prev => ({ ...prev, loading: true, error: null }));
      
      // Suppress CORS opener policy warnings
      const originalError = console.error;
      console.error = (...args) => {
        const message = args[0]?.toString() || '';
        if (message.includes('Cross-Origin-Opener-Policy')) {
          return; // Suppress these warnings
        }
        originalError.apply(console, args);
      };
      
      const result = await signInWithPopup(auth, googleProvider);
      const user = result.user;
      
      // Restore original console.error
      console.error = originalError;
      
      // Get Firebase ID token
      const idToken = await getIdToken(user);
      console.log('🔑 Firebase ID token obtained (first 50 chars):', idToken.substring(0, 50) + '...');
      
      // Send token to your Flask backend for verification
      console.log('🔗 Sending token to backend for verification...');
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:5000'}/api/auth/firebase/verify`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ idToken })
      });

      console.log('📡 Backend response status:', response.status);
      const responseData = await response.json();
      console.log('📋 Backend response data:', responseData);

      if (response.ok) {
        // Store your backend JWT token
        localStorage.setItem('access_token', responseData.access_token);
        localStorage.setItem('refresh_token', responseData.refresh_token || '');
        
        console.log('✅ Firebase authentication successful');
        console.log('🔍 Response data for redirect:', responseData);
        
        // Update auth state immediately
        setAuthState(prev => ({
          ...prev,
          user,
          loading: false,
          error: null
        }));
        
        // Trigger a manual page reload to ensure AuthContext picks up the new token
        // This is a workaround for authentication state synchronization
        setTimeout(() => {
          console.log('🔄 Triggering auth context refresh...')
          window.dispatchEvent(new Event('storage'))
        }, 500)
        
        return { success: true, user, backendData: responseData };
      } else {
        const errorMessage = responseData.error || 'Backend authentication failed';
        console.error('❌ Backend authentication failed:', errorMessage);
        throw new Error(errorMessage);
      }
    } catch (error: any) {
      setAuthState(prev => ({
        ...prev,
        error: error.message,
        loading: false
      }));
      return { success: false, error: error.message };
    }
  };

  const signOut = async () => {
    try {
      await firebaseSignOut(auth);
      localStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');
      return { success: true };
    } catch (error: any) {
      setAuthState(prev => ({
        ...prev,
        error: error.message
      }));
      return { success: false, error: error.message };
    }
  };

  return {
    ...authState,
    signInWithGoogle,
    signOut
  };
}
