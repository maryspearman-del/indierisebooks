import streamlit as st
import supabase
from streamlit_authenticator import Authenticate
import os
from datetime import datetime
import pandas as pd  # For simple data handling in MVP

# Supabase setup (free tier) - Add your actual keys in Streamlit secrets
supabase_url = st.secrets.get("SUPABASE_URL", "your_supabase_url_here")
supabase_key = st.secrets.get("SUPABASE_KEY", "your_supabase_key_here")
supabase_client = supabase.create_client(supabase_url, supabase_key)

# Page config
st.set_page_config(page_title="IndieRise", layout="wide", page_icon="📚")

# Enhanced Authentication with Admin Role
# Mock users database (migrate to Supabase for production)
users = {
    "mary@stockittome.com": {"name": "Mary Spearman", "password": "indie123", "role": "admin"},
    "test@author.com": {"name": "Test Author", "password": "test123", "role": "author"},
}

# Mock books database (use Supabase table for real)
if 'books' not in st.session_state:
    st.session_state.books = []  # List of dicts: {'author_email': email, 'title': str, 'description': str, 'cover_url': str, 'trailer_url': str, 'approved': True}

if 'users' not in st.session_state:
    st.session_state.users = users  # For admin management

# Session state for user
if 'user' not in st.session_state:
    st.session_state.user = None

def login():
    st.sidebar.header("Author Login / Sign Up")
    email = st.sidebar.text_input("Email")
    password = st.sidebar.text_input("Password", type="password")
    if st.sidebar.button("Login"):
        if email in st.session_state.users and st.session_state.users[email]["password"] == password:
            st.session_state.user = st.session_state.users[email]
            st.session_state.user['email'] = email  # Add email to session
            st.success(f"Welcome back, {st.session_state.user['name']}!")
        else:
            st.error("Wrong credentials")
    if st.sidebar.button("Sign Up"):
        # Simple signup - in real, use Supabase auth
        if email and password and email not in st.session_state.users:
            st.session_state.users[email] = {"name": email.split('@')[0], "password": password, "role": "author"}
            st.success("Account created! Please log in.")
        else:
            st.error("Email already exists or invalid.")

def logout():
    st.session_state.user = None
    st.rerun()

# Legal Disclaimers and Content Policy
def show_disclaimers():
    st.markdown("""
    ### Legal Disclaimers and Content Policy
    - **Content Limits**: IndieRise is a family-friendly platform. No X-rated, pornographic, explicit, violent, political, or offensive content allowed. All submissions are reviewed for compliance. Violations lead to immediate removal and account suspension.
    - **Safe Space**: This is a hub for pure, wholesome books suitable for all ages, especially families and children.
    - **User Agreement**: By using IndieRise, you agree to our terms: No liability for user-generated content; we reserve the right to moderate/remove anything. Report issues to admin@indierise.app.
    - **DMCA/Copyright**: We respect intellectual property. Report infringements via email.
    - **Disclaimer**: IndieRise provides tools 'as-is' without warranties. Use at your own risk.
    """)

# Public Buyer Landing Page (no login required)
def buyer_landing_page():
    st.title("📚 Welcome to IndieRise - Discover Independent Books!")
    st.subheader("Shop wholesome, family-friendly stories from indie authors")
    show_disclaimers()  # Show on public page
    
    # Search and filter
    search_query = st.text_input("Search books by title, author, or genre")
    
    # Display approved books
    filtered_books = [book for book in st.session_state.books if book['approved']]
    if search_query:
        filtered_books = [book for book in filtered_books if search_query.lower() in book['title'].lower() or search_query.lower() in book['author_email'].lower()]
    
    if not filtered_books:
        st.info("No books yet! Authors are adding more every day.")
    else:
        cols = st.columns(3)
        for i, book in enumerate(filtered_books):
            with cols[i % 3]:
                if book.get('cover_url'):
                    st.image(book['cover_url'], width=200)
                st.markdown(f"**{book['title']}** by {book['author_email'].split('@')[0]}")
                st.write(book['description'][:100] + "...")
                if book.get('trailer_url'):
                    st.video(book['trailer_url'])
                st.button("Buy Now →", key=f"buy_{i}")

# Author-Only Hub
if st.session_state.user:
    st.sidebar.write(f"Logged in as {st.session_state.user['name']} ({st.session_state.user['role']})")
    if st.sidebar.button("Logout"):
        logout()
    
    page = st.sidebar.radio("Go to", ["Dashboard", "My Profile Editor", "Add Book", "Cross-Promo Board", "Marketing Tools", "Book Trailer Maker", "Admin Controls"] if st.session_state.user['role'] == 'admin' else ["Dashboard", "My Profile Editor", "Add Book", "Cross-Promo Board", "Marketing Tools", "Book Trailer Maker"])
    
    show_disclaimers()  # Show to authors too
    
    if page == "Dashboard":
        st.header("Your Author Dashboard")
        my_books = [book for book in st.session_state.books if book['author_email'] == st.session_state.user['email']]
        st.write(f"Books uploaded: {len(my_books)}")
        st.write("Readers reached this month: 1,248 (demo)")
        st.write("Revenue earned: $87.32 (demo)")
        if st.button("Add New Book"):
            st.session_state.page = "Add Book"  # Redirect simulation

    if page == "My Profile Editor":
        st.header("Edit Your Author Profile")
        # Password re-verification for edit (extra security)
        edit_password = st.text_input("Re-enter your password to edit", type="password")
        if edit_password == st.session_state.user['password']:
            author_name = st.text_input("Display Name", st.session_state.user['name'])
            bio = st.text_area("Bio", "Bestselling indie author...")
            if st.button("Save Profile"):
                st.session_state.user['name'] = author_name
                st.success("Profile updated!")
        else:
            st.error("Password required to edit.")

    if page == "Add Book":
        st.header("Add a New Book")
        st.warning("Remember: Keep content wholesome and family-friendly. No explicit or political material.")
        title = st.text_input("Book Title")
        description = st.text_area("Description")
        cover_url = st.text_input("Cover Image URL")
        trailer_url = st.text_input("Book Trailer URL (YouTube embed)")
        agree_policy = st.checkbox("I agree to the content policy: No X-rated, porn, violence, or politics.")
        if st.button("Submit Book") and agree_policy:
            new_book = {
                'author_email': st.session_state.user['email'],
                'title': title,
                'description': description,
                'cover_url': cover_url,
                'trailer_url': trailer_url,
                'approved': False if st.session_state.user['role'] != 'admin' else True  # Admins auto-approve, others pending
            }
            st.session_state.books.append(new_book)
            st.success("Book submitted! Pending approval if not admin.")

    if page == "Cross-Promo Board":
        st.header("Cross-Promo Opportunities")
        # ... (same as before)

    if page == "Marketing Tools":
        st.header("Marketing Toolkit")
        # ... (same as before)

    if page == "Book Trailer Maker":
        st.header("Book Trailer Maker")
        # ... (same as before)

    if page == "Admin Controls" and st.session_state.user['role'] == 'admin':
        st.header("Admin Controls")
        st.subheader("Manage Users")
        user_df = pd.DataFrame.from_dict(st.session_state.users, orient='index')
        st.dataframe(user_df)
        remove_email = st.text_input("Enter email to remove bad actor")
        if st.button("Remove User"):
            if remove_email in st.session_state.users:
                del st.session_state.users[remove_email]
                # Remove their books
                st.session_state.books = [b for b in st.session_state.books if b['author_email'] != remove_email]
                st.success(f"User {remove_email} removed.")
            else:
                st.error("User not found.")
        
        st.subheader("Approve Books")
        pending_books = [book for book in st.session_state.books if not book['approved']]
        for i, book in enumerate(pending_books):
            st.markdown(f"**{book['title']}** by {book['author_email']}")
            st.write(book['description'])
            if st.button("Approve", key=f"approve_{i}"):
                book['approved'] = True
                st.success("Approved!")
            if st.button("Reject", key=f"reject_{i}"):
                st.session_state.books.remove(book)
                st.success("Rejected!")

else:
    # Public access: Show login and buyer page
    login()
    buyer_landing_page()

st.caption("IndieRise © 2026 • Built for authors, by authors • Family-Friendly Hub")
