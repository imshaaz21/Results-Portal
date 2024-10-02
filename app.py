import streamlit as st
import os
import datetime
from utils.auth import AdminAuth
from utils.data_processor import DataProcessor

# Set page configuration
st.set_page_config(page_title="Results of Focus Stride 2024", layout="centered", initial_sidebar_state="collapsed")

# Define path to save uploaded file
UPLOADED_FILE_PATH = "uploaded_results.xlsx"


def display_last_updated():
    """Displays the last updated time of the uploaded file."""
    try:
        if os.path.exists(UPLOADED_FILE_PATH):
            last_modified_time = os.path.getmtime(UPLOADED_FILE_PATH)
            last_updated = datetime.datetime.fromtimestamp(last_modified_time)
            st.info(
                f"Last updated: {last_updated.strftime('%Y-%m-%d %H:%M')}")
        else:
            st.warning("No uploaded file found.")
    except Exception as e:
        st.error(f"An error occurred while retrieving the last updated time: {e}")


def display_admin_section(processor):
    """Displays the Admin upload section and zone summary if the file is uploaded successfully."""
    st.subheader("Admin Section: Upload Results Excel")
    display_last_updated()
    uploaded_file = st.file_uploader("Upload Excel File", type=["xlsx"], key="file_uploader")

    if uploaded_file:
        try:
            with open(UPLOADED_FILE_PATH, "wb") as f:
                f.write(uploaded_file.getbuffer())
            processor.upload_file(UPLOADED_FILE_PATH)
            st.success("File uploaded successfully!", icon="✅")
        except ValueError as ve:
            st.error(f"File upload error: {ve}")
        except FileNotFoundError as fe:
            st.error(f"File not found: {fe}")
        except Exception as e:
            st.error(f"An unexpected error occurred: {e}")


def display_student_section(processor):
    """Displays the Student result search section if data is available."""
    st.subheader("Student Section: Search Results")

    if processor.has_data():
        zones = processor.extract_zones()
        student_zone = st.selectbox("Select Zone", zones, key="student_zone_select")
        student_index_no = st.text_input("Enter Index Number", key="student_index_input")

        if st.button("Search Results", key="student_search_button"):
            try:
                result = processor.search_results(student_zone, student_index_no)
                if result is not None:
                    st.write("Student Result:")
                    st.table(result)
                else:
                    st.warning("No results found for the given index number and zone.")
            except ValueError as ve:
                st.error(f"Search error: {ve}")
            except KeyError as ke:
                st.error(f"Key error: {ke}")
            except Exception as e:
                st.error(f"An unexpected error occurred during search: {e}")
    else:
        st.warning("No data available. Please contact the administrator.")


def admin_login(auth, processor):
    """Handles Admin login functionality and shows upload section after successful login."""
    if 'admin_logged_in' not in st.session_state:
        st.session_state.admin_logged_in = False

    # Admin Login Section
    if not st.session_state.admin_logged_in:
        st.subheader("Admin Login")
        username = st.text_input("Username", key="admin_username_input")
        password = st.text_input("Password", type="password", key="admin_password_input")

        if st.button("Login", key="admin_login_button"):
            try:
                if auth.login(username, password):
                    st.session_state.admin_logged_in = True
                    st.success("Logged in successfully!", icon="✅")
                    display_admin_section(processor)  # Show upload section immediately after login
                else:
                    st.error("Invalid username or password!")
            except Exception as e:
                st.error(f"An error occurred during login: {e}")
    else:
        # If already logged in, show the logout button
        st.success("You are logged in as Admin.")
        if st.button("Logout", key="admin_logout_button"):
            st.session_state.admin_logged_in = False
            st.success("Logged out successfully!", icon="✅")
            st.rerun()  # Rerun the app to refresh the state

        # Display the upload section for logged-in admin
        display_admin_section(processor)


def main():
    st.title("Results of Focus Stride 2024")

    # Initialize authentication and data processor
    try:
        auth = AdminAuth()
        processor = DataProcessor()
    except Exception as e:
        st.error(f"An error occurred during initialization: {e}")
        return

    # If uploaded file exists, load the data
    if os.path.exists(UPLOADED_FILE_PATH):
        try:
            processor.upload_file(UPLOADED_FILE_PATH)
        except ValueError as ve:
            st.error(f"File format error: {ve}")
        except FileNotFoundError as fe:
            st.error(f"File not found: {fe}")
        except Exception as e:
            st.error(f"An unexpected error occurred during file loading: {e}")

    # Initialize session state for navigation
    if 'page' not in st.session_state:
        st.session_state.page = "Search Results"  # Default page is Search Results

    # Sidebar Navigation Buttons
    with st.sidebar:
        st.write("# Navigation")
        if st.button("Search Results", key="nav_search_results_button"):
            st.session_state.page = "Search Results"
        if st.button("Admin Login", key="nav_admin_login_button"):
            st.session_state.page = "Admin Login"

    # Show the appropriate page based on the selected navigation option
    if st.session_state.page == "Admin Login":
        admin_login(auth, processor)

    elif st.session_state.page == "Search Results":
        # If no data has been uploaded, prompt the user to contact the admin
        if not os.path.exists(UPLOADED_FILE_PATH):
            st.warning("No data available. Please contact the administrator.")
        else:
            display_student_section(processor)


if __name__ == "__main__":
    main()
