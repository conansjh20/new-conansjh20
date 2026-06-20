import os
import pymysql
from flask import Blueprint, jsonify, request

engcross_bp = Blueprint('engcross_bp', __name__)

def get_engcross_db_connection():
    host = os.environ.get('ENGCROSS_DB_HOST', 'conansjh20.mysql.pythonanywhere-services.com')
    user = os.environ.get('ENGCROSS_DB_USER', 'conansjh20')
    password = os.environ.get('ENGCROSS_DB_PASS', 'P020673#1')
    db_name = os.environ.get('ENGCROSS_DB_NAME', 'conansjh20$english')

    return pymysql.connect(
        host=host,
        user=user,
        password=password,
        database=db_name,
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor
    )

def check_new_rank(level):
    try:
        conn = get_engcross_db_connection()
        with conn.cursor() as cursor:
            cursor.execute("SELECT name, score FROM engcross_leaderboard WHERE level = %s ORDER BY score DESC", (level,))
            rows = cursor.fetchall()
            new_result = {row['name']: row['score'] for row in rows}
            return jsonify(new_result)
    except Exception as e:
        print("Engcross DB Error:", e)
        return jsonify({"error": str(e)}), 500
    finally:
        if 'conn' in locals() and conn.open:
            conn.close()

def update_new_rank(level):
    if request.method == 'POST':
        data = request.get_json(silent=True) or {}
        name = data.get("name")
        password = data.get("password")
    else:
        name = request.args.get("name")
        password = request.args.get("password")

    if not name or not password:
        return "Missing name or password", 400

    try:
        conn = get_engcross_db_connection()
        with conn.cursor() as cursor:
            cursor.execute("SELECT password, score FROM engcross_leaderboard WHERE level = %s AND name = %s", (level, name))
            user = cursor.fetchone()

            if user:
                if str(password) == str(user['password']):
                    new_score = user['score'] + 1
                    cursor.execute("UPDATE engcross_leaderboard SET score = %s WHERE level = %s AND name = %s", (new_score, level, name))
                    conn.commit()
                    return "updated"
                else:
                    return "wrongPass"
            else:
                cursor.execute("INSERT INTO engcross_leaderboard (level, name, password, score) VALUES (%s, %s, %s, %s)", (level, name, password, 1))
                conn.commit()
                return "new"
    except Exception as e:
        print("Engcross DB Error:", e)
        return f"Error: {str(e)}", 500
    finally:
        if 'conn' in locals() and conn.open:
            conn.close()

@engcross_bp.route('/engcross/newrankelementary', methods=['GET'])
def check_new_rank_elementary():
    return check_new_rank('1')

@engcross_bp.route('/engcross/newrankmiddlehigh', methods=['GET'])
def check_new_rank_middlehigh():
    return check_new_rank('2')

@engcross_bp.route('/engcross/newranktoeic', methods=['GET'])
def check_new_rank_toeic():
    return check_new_rank('3')

@engcross_bp.route('/engcross/newrankofficer', methods=['GET'])
def check_new_rank_officer():
    return check_new_rank('4')

@engcross_bp.route('/engcross/newone', methods=['GET', 'POST'])
def new_update_rankE():
    return update_new_rank('1')

@engcross_bp.route('/engcross/newtwo', methods=['GET', 'POST'])
def new_update_rankM():
    return update_new_rank('2')

@engcross_bp.route('/engcross/newthree', methods=['GET', 'POST'])
def new_update_rankT():
    return update_new_rank('3')

@engcross_bp.route('/engcross/newfour', methods=['GET', 'POST'])
def new_update_rankO():
    return update_new_rank('4')

@engcross_bp.route('/engcross/wordsearch/categories', methods=['GET'])
def get_wordsearch_categories():
    try:
        conn = get_engcross_db_connection()
        with conn.cursor() as cursor:
            cursor.execute("SELECT code, name_ko AS name FROM wordsearch_category")
            categories = cursor.fetchall()
            return jsonify(categories)
    except Exception as e:
        print("Category DB Error:", e)
        return jsonify({"error": str(e)}), 500
    finally:
        if 'conn' in locals() and conn.open:
            conn.close()

@engcross_bp.route('/engcross/wordsearch/words', methods=['GET'])
def get_wordsearch_words():
    category_code = request.args.get('category')
    if not category_code:
        return jsonify({"error": "Missing category parameter"}), 400

    try:
        conn = get_engcross_db_connection()
        with conn.cursor() as cursor:
            sql = """
                SELECT w.ko, w.en
                FROM wordsearch_word w
                JOIN wordsearch_category c ON w.category_id = c.id
                WHERE c.code = %s
            """
            cursor.execute(sql, (category_code,))
            words = cursor.fetchall()
            return jsonify(words)
    except Exception as e:
        print("Word DB Error:", e)
        return jsonify({"error": str(e)}), 500
    finally:
        if 'conn' in locals() and conn.open:
            conn.close()
