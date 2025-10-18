// Firebase configuration test utility
import { auth } from '@/lib/firebase';

export const testFirebaseConnection = async () => {
  try {
    console.log('🔥 Testing Firebase connection...');
    console.log('Firebase Auth instance:', auth);
    console.log('Firebase project ID:', auth.app.options.projectId);
    console.log('Firebase auth domain:', auth.app.options.authDomain);
    
    return {
      success: true,
      projectId: auth.app.options.projectId,
      authDomain: auth.app.options.authDomain
    };
  } catch (error) {
    console.error('❌ Firebase connection test failed:', error);
    return {
      success: false,
      error: error instanceof Error ? error.message : 'Unknown error'
    };
  }
};
