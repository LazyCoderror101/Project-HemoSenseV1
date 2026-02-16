import streamlit as st
from datetime import datetime, timedelta
from config.app_config import SESSION_TIMEOUT_MINUTES
import json

class SessionManager:
    @staticmethod
    def init_session():
        """Initialize or validate session."""
        # Initialize session only once per browser session
        if 'session_initialized' not in st.session_state:
            st.session_state.session_initialized = True
            # Try to restore session from persistent storage
            SessionManager._restore_from_storage()
            
        if 'auth_service' not in st.session_state:
            from auth.auth_service import AuthService
            st.session_state.auth_service = AuthService()
        
        # Check session timeout
        if 'last_activity' in st.session_state:
            idle_time = datetime.now() - st.session_state.last_activity
            if idle_time > timedelta(minutes=SESSION_TIMEOUT_MINUTES):
                SessionManager.clear_session_state()
                st.error("Session expired. Please log in again.")
                st.rerun()
        
        # Update last activity
        st.session_state.last_activity = datetime.now()
        
        # Validate token and user data
        if 'user' in st.session_state:
            user_data = st.session_state.auth_service.validate_session_token()
            if not user_data:
                SessionManager.clear_session_state()
                st.error("Invalid session. Please log in again.")
                st.rerun()
    
    @staticmethod
    def _restore_from_storage():
        """Restore session from persistent storage."""
        try:
            # Inject storage script to enable localStorage functionality
            SessionManager._inject_storage_script()
            
            # The actual restoration happens in AuthService.try_restore_session()
            # which uses Supabase's built-in session persistence
            
        except Exception:
            pass  # Ignore errors during restoration
    
    @staticmethod
    def _inject_storage_script():
        """Inject JavaScript for persistent storage management."""
        storage_script = """
        <script>
        // Check if user data exists in localStorage on page load
        window.addEventListener('DOMContentLoaded', function() {
            const storedAuth = localStorage.getItem('hemosense_auth');
            if (storedAuth) {
                try {
                    const authData = JSON.parse(storedAuth);
                    // Set a flag that Python can check
                    window.hemosense_auth_data = authData;
                } catch (e) {
                    localStorage.removeItem('hemosense_auth');
                }
            }
        });
        
        // Function to save auth data
        window.saveAuthData = function(authData) {
            localStorage.setItem('hemosense_auth', JSON.stringify(authData));
        };
        
        // Function to clear auth data
        window.clearAuthData = function() {
            localStorage.removeItem('hemosense_auth');
        };
        
        // Function to get auth data
        window.getAuthData = function() {
            const stored = localStorage.getItem('hemosense_auth');
            return stored ? JSON.parse(stored) : null;
        };
        </script>
        """
        st.markdown(storage_script, unsafe_allow_html=True)

    @staticmethod
    def clear_session_state():
        """Clear all session state data."""
        # Clear persistent storage
        SessionManager._clear_persistent_storage()
        
        keys_to_keep = ['session_initialized']
        for key in list(st.session_state.keys()):
            if key not in keys_to_keep:
                del st.session_state[key]
    
    @staticmethod
    def _clear_persistent_storage():
        """Clear persistent storage."""
        clear_script = """
        <script>
        if (typeof window.clearAuthData === 'function') {
            window.clearAuthData();
        }
        </script>
        """
        st.markdown(clear_script, unsafe_allow_html=True)
    
    @staticmethod
    def _save_to_persistent_storage(user_data, auth_token):
        """Save authentication data to persistent storage."""
        auth_data = {
            'user': user_data,
            'auth_token': auth_token,
            'timestamp': datetime.now().isoformat()
        }
        
        save_script = f"""
        <script>
        if (typeof window.saveAuthData === 'function') {{
            window.saveAuthData({json.dumps(auth_data)});
        }}
        </script>
        """
        st.markdown(save_script, unsafe_allow_html=True)

    @staticmethod
    def is_authenticated():
        """Check if user is authenticated."""
        return bool(st.session_state.get('user'))
    
    @staticmethod
    def create_chat_session():
        """Create a new chat session."""
        if not SessionManager.is_authenticated():
            return False, "Not authenticated"
        return st.session_state.auth_service.create_session(
            st.session_state.user['id']
        )
    
    @staticmethod
    def get_user_sessions():
        """Get user's chat sessions."""
        if not SessionManager.is_authenticated():
            return False, []
        return st.session_state.auth_service.get_user_sessions(
            st.session_state.user['id']
        )
    
    @staticmethod
    def delete_session(session_id):
        """Delete a chat session."""
        if not SessionManager.is_authenticated():
            return False, "Not authenticated"
        return st.session_state.auth_service.delete_session(session_id)
    
    @staticmethod
    def logout():
        """Logout user and clear session."""
        if 'auth_service' in st.session_state:
            st.session_state.auth_service.sign_out()
        SessionManager.clear_session_state()
    
    @staticmethod
    def login(email, password):
        """Handle user login."""
        if 'auth_service' not in st.session_state:
            from auth.auth_service import AuthService
            st.session_state.auth_service = AuthService()
            
        success, user_data = st.session_state.auth_service.sign_in(email, password)
        
        # If login successful, save to persistent storage
        if success and 'auth_token' in st.session_state:
            SessionManager._save_to_persistent_storage(
                user_data, 
                st.session_state.auth_token
            )
            
        return success, user_data
