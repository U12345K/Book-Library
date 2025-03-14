# Import necessary libraries
import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime
import time
import random
import plotly.express as px
import plotly.graph_objects as go
from streamlit_lottie import st_lottie
import requests

# Set page configuration
st.set_page_config(
    page_title="Library Management System",
    page_icon=":books:",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Add custom CSS styling
st.markdown(
    """
    <style>
        .main-header {
            font-size: 3rem !important;
            color: #1E3A8A;
            font-weight: 700;
            margin-bottom: 1rem;
            text-align: center;
            text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.1);
        }
        .sub-header {
            font-size: 1.8rem !important;
            color: #3B82F6;
            font-weight: 600;
            margin-top: 1rem;
            margin-bottom: 1rem;
        }
        .success-message {
            padding: 1rem;
            background-color: #ECFDF3;
            border-left: 5px solid #10B981;
            border-radius: 0.375rem;
        }
        .warning-message {
            padding: 1rem;
            background-color: #FEF3E2;
            border-left: 5px solid #F59E0B;
            border-radius: 0.375rem;
        }
        .book-card {
            background-color: #F9FAFB;
            border: 1px solid #E5E7EB;
            border-radius: 0.5rem;
            padding: 1rem;
            margin-bottom: 1rem;
            border-left: 5px solid #3B82F6;
            transition: transform 0.3s ease-in-out;
        }
        .book-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
        }
        .read-badge {
            background-color: #ECFDF3;
            color: white;
            padding: 0.25rem 0.75rem;
            border-radius: 1rem;
            font-size: 0.875rem;
            font-weight: 600;
        }
        .unread-badge {
            background-color: #FEF3E2;
            color: white;
            padding: 0.25rem 0.75rem;
            border-radius: 1rem;
            font-size: 0.875rem;
            font-weight: 600;
        }
        .action-button {
            margin-right: 0.5rem;
        }
        .stButton>button {
            border-radius: 0.375rem;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

# Function to load Lottie animations from URL
def load_lottieurl(url):
    try:
        r = requests.get(url)
        if r.status_code != 200:
            return None
        return r.json()
    except:
        return None

# Initialize session state variables
if "Library" not in st.session_state:
    st.session_state.Library = []

if "search_results" not in st.session_state:
    st.session_state.search_results = []

if "book_added" not in st.session_state:
    st.session_state.book_added = False

if "book_removed" not in st.session_state:
    st.session_state.book_removed = False

if "current_view" not in st.session_state:
    st.session_state.current_view = "library"

# Function to load the library data
def load_library():
    try:
        if os.path.exists("library.json"):
            with open("library.json", "r") as file:
                st.session_state.Library = json.load(file)
            return True
        return False
    except Exception as e:
        st.error(f"Error loading library: {e}")
        return False

# save library data
def save_library():
    try:
        with open("library.json", "w") as file:
            json.dump(st.session_state.Library, file)
        return True
    except Exception as e:
        st.error(f"Error saving library: {e}")
        return False

#read book data
def read_book(title, author, publication_year, read_status):
    book = {
        "title": title,
        "author": author,
        "publication_year": publication_year,
        "read_status": read_status,
        "added_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }
    st.session_state.Library.append(book)
    save_library()
    st.session_state.book_added = True
    time.sleep(0.5)

# remove book
def remove_book(index):
    if 0 <= index < len(st.session_state.Library):
        del st.session_state.Library[index]
        save_library()
        st.session_state.book_removed = True
        return True
    return False

#search book
def search_book(search_term, search_by):
    search_term = search_term.lower()
    results = []
    for book in st.session_state.Library:
        if search_by == "Title" and search_term in book["title"].lower():
            results.append(book)
        elif search_by == "Author" and search_term in book["author"].lower():
            results.append(book)
        elif search_by == "Genre" and search_term in book["genre"].lower():
            results.append(book)
    st.session_state.search_results = results

#calculate library stats
def get_library_stats():
    total_books = len(st.session_state.Library)
    read_books = sum(1 for book in st.session_state.Library if book["read_status"])
    percent_read = round((read_books / total_books) * 100) if total_books > 0 else 0

    genres = {}
    authors = {}
    decades = {}

    for book in st.session_state.Library:
        if book["genre"] in genres:
            genres[book["genre"]] += 1
        else:
            genres[book["genre"]] = 1

        if book["author"] in authors:
            authors[book["author"]] += 1
        else:
            authors[book["author"]] = 1

        decade = (book["publication_year"] // 10) * 10
        if decade in decades:
            decades[decade] += 1
        else:
            decades[decade] = 1
    genres = dict(sorted(genres.items(), key=lambda x: x[1], reverse=True))
    authors = dict(sorted(authors.items(), key=lambda x: x[1], reverse=True))
    decades = dict(sorted(decades.items(), key=lambda x: x[0]))

    return {
        "total_books": total_books,
        "read_books": read_books,
        "percent_read": percent_read,
        "genres": genres,
        "authors": authors,
        "decades": decades,
    }

# Streamlit UI Implementation
def main():
    st.markdown("<h1 class='main-header'>Library Management System</h1>", unsafe_allow_html=True)

    # Load library data
    if not load_library():
        st.warning("No library data found. Start by adding some books!")

    # Sidebar navigation
    st.sidebar.title("Navigation")
    view_options = ["Library", "Add Book", "Search", "Library Stats"]
    selected_view = st.sidebar.radio("Go to:", view_options)

    # Set current view based on user selection
    st.session_state.current_view = selected_view

    # Display corresponding section
    if selected_view == "Library":
        display_library()
    elif selected_view == "Add Book":
        add_book()
    elif selected_view == "Search":
        search_section()
    elif selected_view == "Library Stats":
        display_library_stats()


# Display library contents
def display_library():
    st.markdown("<h2 class='sub-header'>Library</h2>", unsafe_allow_html=True)

    if len(st.session_state.Library) == 0:
        st.info("Your library is empty. Add some books to get started!")
    else:
        for index, book in enumerate(st.session_state.Library):
            st.markdown(f"""
            <div class='book-card'>
                <h3>{book['title']}</h3>
                <p><strong>Author:</strong> {book['author']}</p>
                <p><strong>Publication Year:</strong> {book['publication_year']}</p>
                <p><strong>Status:</strong> {"Read" if book['read_status'] else "Unread"}</p>
                <button class="action-button">Remove</button>
            </div>
            """, unsafe_allow_html=True)
            if st.button("Remove", key=f"remove_{index}"):
                if remove_book(index):
                    st.success(f"Book '{book['title']}' removed successfully!")


# Add a new book to the library
def add_book():
    st.markdown("<h2 class='sub-header'>Add a New Book</h2>", unsafe_allow_html=True)

    title = st.text_input("Book Title")
    author = st.text_input("Author")
    publication_year = st.number_input("Publication Year", min_value=0, value=2023, step=1)
    read_status = st.radio("Have you read this book?", ["Yes", "No"]) == "Yes"

    if st.button("Add Book"):
        if title and author:
            read_book(title, author, publication_year, read_status)
            st.success(f"Book '{title}' added to your library!")
        else:
            st.warning("Please fill in all fields before adding the book.")


# Search for a book in the library
def search_section():
    st.markdown("<h2 class='sub-header'>Search Library</h2>", unsafe_allow_html=True)

    search_term = st.text_input("Enter search term")
    search_by = st.selectbox("Search By", ["Title", "Author", "Genre"])

    if st.button("Search"):
        if search_term:
            search_book(search_term, search_by)
            if len(st.session_state.search_results) > 0:
                for book in st.session_state.search_results:
                    st.markdown(f"""
                    <div class='book-card'>
                        <h3>{book['title']}</h3>
                        <p><strong>Author:</strong> {book['author']}</p>
                        <p><strong>Publication Year:</strong> {book['publication_year']}</p>
                        <p><strong>Status:</strong> {"Read" if book['read_status'] else "Unread"}</p>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.info("No matching books found.")
        else:
            st.warning("Please enter a search term.")


# Display library statistics
def display_library_stats():
    st.markdown("<h2 class='sub-header'>Library Statistics</h2>", unsafe_allow_html=True)

    stats = get_library_stats()
    st.metric(label="Total Books", value=stats["total_books"])
    st.metric(label="Books Read", value=stats["read_books"])
    st.metric(label="Percent Read", value=f"{stats['percent_read']}%")

    st.write("**Books by Genre:**")
    st.bar_chart(stats["genres"])

    st.write("**Books by Author:**")
    st.bar_chart(stats["authors"])

    st.write("**Books by Decade:**")
    st.bar_chart(stats["decades"])


if __name__ == "__main__":
    main()


