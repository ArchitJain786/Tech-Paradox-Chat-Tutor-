import sqlite3
import json
from datetime import datetime
import os

DB_FILE = "chats.db"

def init_db():
    """Initialize database for storing chats"""
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    
    # Create chat sessions table
    c.execute('''CREATE TABLE IF NOT EXISTS chat_sessions
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  title TEXT NOT NULL,
                  subject TEXT,
                  mode TEXT,
                  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
    
    # Create messages table
    c.execute('''CREATE TABLE IF NOT EXISTS messages
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  session_id INTEGER,
                  role TEXT NOT NULL,
                  content TEXT NOT NULL,
                  timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                  FOREIGN KEY (session_id) REFERENCES chat_sessions(id))''')
    
    # Create notes table
    c.execute('''CREATE TABLE IF NOT EXISTS notes
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  session_id INTEGER,
                  content TEXT NOT NULL,
                  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                  FOREIGN KEY (session_id) REFERENCES chat_sessions(id))''')
    
    # Create progress table
    c.execute('''CREATE TABLE IF NOT EXISTS progress
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  session_id INTEGER,
                  quiz_taken INTEGER DEFAULT 0,
                  correct_answers INTEGER DEFAULT 0,
                  total_questions INTEGER DEFAULT 0,
                  score REAL DEFAULT 0.0,
                  FOREIGN KEY (session_id) REFERENCES chat_sessions(id))''')
    
    conn.commit()
    conn.close()

def create_session(title, subject="", mode="Interactive Q&A"):
    """Create a new chat session"""
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("INSERT INTO chat_sessions (title, subject, mode) VALUES (?, ?, ?)",
              (title, subject, mode))
    session_id = c.lastrowid
    
    # Initialize progress for this session
    c.execute("INSERT INTO progress (session_id) VALUES (?)", (session_id,))
    
    conn.commit()
    conn.close()
    return session_id

def get_all_sessions():
    """Get all chat sessions"""
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT id, title, subject, mode, created_at FROM chat_sessions ORDER BY updated_at DESC")
    sessions = c.fetchall()
    conn.close()
    return sessions

def get_session_messages(session_id):
    """Get all messages for a session"""
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT role, content FROM messages WHERE session_id = ? ORDER BY timestamp", (session_id,))
    messages = c.fetchall()
    conn.close()
    return [{"role": msg[0], "content": msg[1]} for msg in messages]

def save_message(session_id, role, content):
    """Save a message to database"""
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("INSERT INTO messages (session_id, role, content) VALUES (?, ?, ?)",
              (session_id, role, content))
    c.execute("UPDATE chat_sessions SET updated_at = CURRENT_TIMESTAMP WHERE id = ?", (session_id,))
    conn.commit()
    conn.close()

def delete_session(session_id):
    """Delete a chat session"""
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("DELETE FROM messages WHERE session_id = ?", (session_id,))
    c.execute("DELETE FROM notes WHERE session_id = ?", (session_id,))
    c.execute("DELETE FROM progress WHERE session_id = ?", (session_id,))
    c.execute("DELETE FROM chat_sessions WHERE id = ?", (session_id,))
    conn.commit()
    conn.close()

def add_note(session_id, content):
    """Add a note to session"""
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("INSERT INTO notes (session_id, content) VALUES (?, ?)", (session_id, content))
    conn.commit()
    conn.close()

def get_notes(session_id):
    """Get all notes for a session"""
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT id, content, created_at FROM notes WHERE session_id = ? ORDER BY created_at",
              (session_id,))
    notes = c.fetchall()
    conn.close()
    return notes

def delete_note(note_id):
    """Delete a note"""
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("DELETE FROM notes WHERE id = ?", (note_id,))
    conn.commit()
    conn.close()

def update_progress(session_id, correct=0, total=0):
    """Update progress for a session"""
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("UPDATE progress SET correct_answers = correct_answers + ?, total_questions = total_questions + ? WHERE session_id = ?",
              (correct, total, session_id))
    conn.commit()
    conn.close()

def get_progress(session_id):
    """Get progress for a session"""
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT correct_answers, total_questions FROM progress WHERE session_id = ?", (session_id,))
    result = c.fetchone()
    conn.close()
    if result:
        correct, total = result
        if total > 0:
            score = (correct / total) * 100
        else:
            score = 0
        return {"correct": correct, "total": total, "score": score}
    return {"correct": 0, "total": 0, "score": 0}

# Initialize database on import
init_db()
