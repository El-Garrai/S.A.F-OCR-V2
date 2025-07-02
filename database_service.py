import psycopg2

def get_db_connection():
    conn = psycopg2.connect(
        host="timescale",
        database="RAG",
        user="rag",
        password="wecandoit"
    )
    return conn

def get_corrections():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, original_text, corrected_text, language, file_name, created_at FROM ocr_corrections ORDER BY created_at DESC")
    corrections = cur.fetchall()
    cur.close()
    conn.close()
    return corrections

def save_correction(original_text, corrected_text, language, file_name):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO ocr_corrections (original_text, corrected_text, language, file_name) VALUES (%s, %s, %s, %s)",
        (original_text, corrected_text, language, file_name)
    )
    conn.commit()
    cur.close()
    conn.close()
