from flask import Flask, render_template, request, redirect, url_for, session 
import json
import random
import requests
from datetime import date
from datetime import datetime, timedelta
from flask_session import Session
import mysql.connector
from urllib.parse import urlparse

app = Flask(__name__)





app.secret_key = 'jKtZuPqEhXrMnLbVgYf'
app.permanent_session_lifetime = timedelta(minutes=10)

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_PORT'] = 3306
app.config['MYSQL_DB'] = 'user_db'

LOG_FILE_PATH = 'logs.json'
DATA_FILE_PATH = "data.json"
RANKING_FILE_PATH = "ranking.json"
TODAYS_RANKING_FILE = "todays_ranking.json"

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_PORT'] = 3306
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'Yuto0712yutoMySQL'
app.config['MYSQL_DB'] = 'user_db'


def connect_to_database():
    connection = mysql.connector.connect(
        host=app.config['MYSQL_HOST'],
        port=app.config['MYSQL_PORT'],
        user=app.config['MYSQL_USER'],
        password=app.config['MYSQL_PASSWORD'],
        database=app.config['MYSQL_DB']
    )
    return connection

def add_user_to_data(username):
    cnx = mysql.connector.connect(user='user03', password='YUTO0712yuto', host='localhost', database='user_db')
    cursor = cnx.cursor()
    add_user = ("INSERT INTO users "
                "(username, points, game_played, game_time, nickname)"
                "VALUES (%s, %s, %s, %s, %s)")
    new_user = (username, 0, False,  None, None)

    cursor.execute(add_user, new_user)
    
    cnx.commit()
    
    cursor.close()
    cnx.close()
    
def change_nickname(username, nickname):
    cnx = mysql.connector.connect(user='user01', password='YUTO0712yuto', host='localhost', database='user_db')
    cursor = cnx.cursor()
    update_nickname = ("UPDATE users "
                       "SET nickname = %s "
                       "WHERE username = %s")
    cursor.execute(update_nickname, (nickname, username, ))

    cnx.commit()

    cursor.close()
    cnx.close()


def get_user_by_username(username):
    # Establish a connection to the MySQL database
    cnx = mysql.connector.connect(user='user01', password='YUTO0712yuto', database='user_db')
    cursor = cnx.cursor()

    # Execute the query
    query = "SELECT * FROM users WHERE username = %s"
    cursor.execute(query, (username, ))

    # Fetch the user data
    user_data = cursor.fetchone()

    # Close the cursor and connection
    cursor.close()
    cnx.close()

    return user_data

def get_random_username():
    while True:
        username = str(random.randint(1000, 9999))
        if get_user_by_username(username) is None:
            return username


def game_start(username, game_time):

    cnx = mysql.connector.connect(user='user01', password='YUTO0712yuto', database='user_db')
    cursor = cnx.cursor()
    game_upd = ("UPDATE users "
                  "SET game_played = %s, game_time = %s "
                  "WHERE username = %s")
    cursor.execute(game_upd, (True, game_time, username, ))

    cnx.commit()

    cursor.close()
    cnx.close()

def get_logs(username):
    cnx = mysql.connector.connect(user='user01', password='YUTO0712yuto', database='user_db')
    cursor = cnx.cursor()
    get_logs_query = "SELECT * FROM logs WHERE username = %s"
    cursor.execute(get_logs_query, (username, ))

    column_names = cursor.column_names
    user_logs = cursor.fetchall()

    cursor.close()
    cnx.close()

    return [dict(zip(column_names, row)) for row in user_logs]


def add_logs_list(username, points_earned, nickname, site_number):
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    cnx = mysql.connector.connect(user='user03', password='YUTO0712yuto', host='localhost', database='user_db')
    cursor = cnx.cursor()
    add_logs = ("INSERT INTO logs "
                "(username, points, time, nickname, site_number)"
                "VALUES (%s, %s, %s, %s, %s)")
    new_log = (username, points_earned, current_time, nickname, site_number)
    cursor.execute(add_logs, new_log)
    cnx.commit()
    
    cursor.close()
    cnx.close()


def add_points_to_user(username, earned_points):
    cnx = mysql.connector.connect(user='user01', password='YUTO0712yuto', database='user_db')
    cursor = cnx.cursor()
    update_query = "UPDATE users SET points = points + %s WHERE username = %s"
    cursor.execute(update_query, (earned_points, username))

    cnx.commit()

    cursor.close()
    cnx.close()

def return_userdata(username):
    with open('data.json', 'r') as json_file:
        data = json.load(json_file)
    for user in data['users']:
        if user['username'] == username:
            userdata= user
            break
        else:
            userdata = None
    return userdata

def average_points_fn():
    with open('data.json', 'r') as json_file:
        data = json.load(json_file)
    total_points = 0
    user_count = 0
    for user in data['users']:
        if user["points"] == 0:
            continue
        total_points += user['points']
        user_count += 1
    average_points = total_points / user_count
    average_points = round(average_points, 3)
    return average_points, user_count

def show_user_data():
    with open('data.json', 'r') as f:
        data = json.load(f)
    user_data = []
    
    sorted_data = sorted(data['users'], key=lambda x: datetime.strptime(x['game_time'], '%Y-%m-%d %H:%M:%S') if x['game_time'] else datetime.min, reverse=True)

    for entry in sorted_data[:20]:
        user_data.append({
            'username': entry['username'],
            'nickname': entry['nickname'],
            'points': entry['points'],
            'game_played': entry['game_played'],
            'game_time': entry['game_time']   
        })

    return user_data

    

def generate_ranking_data():
    with open(DATA_FILE_PATH) as file:
        user_data = json.load(file)["users"]

    sorted_users = sorted(user_data, key=lambda x: x["points"], reverse=True)
    ranking_data = []

    rank = 0
    prev_points = None

    for user in sorted_users:
        if user["points"] == 0:
            continue
        if prev_points is None or user["points"] < prev_points:
            rank += 1
        if rank <= 10:
            username = user["username"]
            points = user["points"]
            game_played = user["game_played"]
            game_time = user["game_time"]
            nickname = user.get("nickname")  # Use get() method with a default value of None
            ranking_data.append({"rank": rank, "username": username, "points": points, "game_played": game_played, "game_time": game_time, "nickname": nickname})
        else:
            break
        prev_points = user['points']

    with open(RANKING_FILE_PATH, 'w') as file:
        json.dump(ranking_data, file, indent=4)

    return ranking_data

def generate_todays_data():
    with open(DATA_FILE_PATH) as file:
        user_data = json.load(file)["users"]

    sorted_users = sorted(user_data, key=lambda x: x["points"], reverse=True)
    todays_data = []

    rank = 0
    prev_points = None

    today = date.today()

    for user in sorted_users:
        if user["points"] == 0:
            continue

        game_time_str = user.get("game_time")
        if game_time_str is not None:
            game_time = datetime.strptime(game_time_str, "%Y-%m-%d %H:%M:%S").date()
            if game_time == today:
                if prev_points is None or user["points"] < prev_points:
                    rank += 1

                if rank <= 10:
                    username = user["username"]
                    points = user["points"]
                    game_played = user["game_played"]
                    nickname = user.get("nickname")  # Use get() method with a default value of None
                    todays_data.append({"rank": rank, "username": username, "points": points, "game_played": game_played, "nickname": nickname})
                else:
                    break

                prev_points = user['points']

    with open(TODAYS_RANKING_FILE, 'w') as file:
        json.dump(todays_data, file, indent=4)

    return todays_data


def log_check(username, site_number):
    cnx = mysql.connector.connect(user='user01', password='YUTO0712yuto', database='user_db')
    cursor = cnx.cursor()

    check_query = "SELECT 1 FROM logs WHERE username = %s AND site_number = %s LIMIT 1"
    cursor.execute(check_query, (username, site_number))

    result = cursor.fetchone()

    earned = True if result else False

    cursor.close()
    cnx.close()

    return earned
        
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        if 'signin' in request.form:
            username = get_random_username()
            session['username'] = username
            add_user_to_data(username)
            return render_template('signin.html', username=username)
        elif 'login' in request.form:
            return render_template('login.html')
    return render_template('index.html')

@app.route('/login', methods=['POST'])
def login():
    username = request.form.get("username")
    if username == "SHUKUGAWA":
        return redirect(url_for("develop"))
    else:
        user = get_user_by_username(username)
        if user is not None:
            return redirect(url_for("personal", user=username))
        else:
            return render_template("login.html", error="パスワードが間違っています！半角かを確認して、もう一度入力してください")

    
@app.route('/signin', methods=['POST'])
def signin():
    username = session.get('username')
    if not username:
        return redirect(url_for('index'))
    entered_username = request.form['username']
    entered_nickname = request.form.get('nickname')  # Get the entered nickname from the form
    user = get_user_by_username(entered_username)
    if len(entered_nickname) > 10:
        return render_template('signin.html', username=username, error="10文字以内で入力してください！")
    elif user is not None:
        if entered_nickname:  # Check if a nickname was entered
            change_nickname(entered_username, entered_nickname) 
        return redirect(url_for('personal', user=entered_username))
    else:
        return render_template('signin.html', username=username, error="パスワードが間違っています！半角かを確認して、もう一度入力してください")
    
@app.route('/personal', methods=['GET', 'POST'])
def personal():
    username = request.args.get('user')
    ranking_data = generate_ranking_data()
    user = get_user_by_username(username)
    points = user[2] if user else 0
    game_played = user[3] if user else False
    nickname = user[5] if user else None
    if request.method == 'POST' and 'gamestart' in request.form:
        start_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        game_start(username, start_time)
        return redirect(url_for('game', user=username))
    return render_template("personal.html", username=username, points=points, game_played=game_played, ranking=ranking_data, nickname=nickname)

@app.route('/game')
def game():
    username = request.args.get('user')
    user = get_user_by_username(username)
    points = user[2] if user else 0
    start_time = user[4] if user else 0
    remaining_time = timedelta(minutes=7) - (datetime.now() - start_time)
    time_sec = remaining_time.seconds
    user_logs = get_logs(username)

    if remaining_time > timedelta():
        return render_template('game.html', message='QRコードを見つけよう！', points=points, log_list=user_logs, remaining_time=remaining_time, timedelta=timedelta, username=username, time_sec=time_sec)
    elif remaining_time < timedelta():
        return render_template('game.html', message='ゲーム終了！', points=points, log_list=user_logs, remaining_time=remaining_time, timedelta=timedelta, username=username, time_sec=time_sec)
    else:
        session.pop('start_time')
        return redirect(url_for('personal', user=username))


@app.route('/add_points', methods=['GET', 'POST'])
def add_points():
    site_number = request.args.get('site')
    username = request.args.get('user')
    user = get_user_by_username(username)
    nickname = user[5] if user else None
    
    if request.method == 'POST':
        earned = log_check(username, site_number)
        if earned == False:
            points_earned = int(request.form.get('points', 0))
            add_logs_list(username, points_earned, nickname, site_number)
            add_points_to_user(username, points_earned)

            template_name = f'add_points/add_points_{site_number}.html'
            return render_template(template_name, username=username, site_number=site_number, points_earned=points_earned, nickname=nickname)

        else:
            error = "二回目以降はポイント獲得できません！"
            points_earned = "0"
            template_name = f'add_points/add_points_{site_number}.html'
            return render_template(template_name, username=username, site_number=site_number, points_earned=points_earned, error=error)


        
    template_name = f'add_points/add_points_{site_number}.html'
    return render_template(template_name, username=username, site_number=site_number, points_earned=None)


@app.route('/quiz_points', methods=['GET', 'POST'])
def quiz_points():
    site_number = request.args.get('site')
    username = request.args.get('user')
    user = get_user_by_username(username)
    nickname = user[5] if user else None
    
    points_earned = None  # Assign a default value to points_earned
    if request.method == 'POST':
        earned = log_check(username, site_number)
        if earned == False:
            selected_answer = request.form.get('answer')
            if selected_answer == '0':  # Check if the selected answer is correct
                quiz_correct = True
                points_earned = int(request.form.get('points', 0))
            else:
                points_earned = 0
                quiz_correct = False 
            add_logs_list(username, points_earned, nickname, site_number)
            add_points_to_user(username, points_earned)

            points_earned = int(request.form.get('points', 0))
            template_name = f'add_points/quiz_points_{site_number}.html'
            return render_template(template_name, username=username, site_number=site_number, points_earned=points_earned, quiz_correct=quiz_correct)
        else:
            error = "二回目以降はポイント獲得できません！"
            points_earned = "0"
            quiz_correct = False
            template_name = f'add_points/quiz_points_{site_number}.html'
            return render_template(template_name, username=username, site_number=site_number, points_earned=points_earned, quiz_correct=quiz_correct, error=error)

    template_name = f'add_points/quiz_points_{site_number}.html'
    return render_template(template_name, username=username, site_number=site_number, points_earned=None, quiz_correct=None)


@app.route('/hp_points', methods=['GET', 'POST'])
def hp_points():
    site_number = request.args.get('site')
    username = request.args.get('user')
    user = get_user_by_username(username)
    nickname = user[5] if user else None

    if request.method == 'POST':
        earned = log_check(username, site_number)
        if earned == False:
            points_earned = int(request.form.get('points', 0))
            add_logs_list(username, points_earned, nickname, site_number)
            add_points_to_user(username, points_earned)

            template_name = f'add_points/hp_points_{site_number}.html'
            return render_template(template_name, username=username, site_number=site_number, points_earned=points_earned)
        else:
            error = "二回目以降はポイント獲得できません！"
            points_earned = "0"
            template_name = f'add_points/hp_points_{site_number}.html'
            return render_template(template_name, username=username, site_number=site_number, points_earned=points_earned, error=error)

    template_name = f'add_points/hp_points_{site_number}.html'
    return render_template(template_name, username=username, site_number=site_number)

@app.route("/develop", methods=['GET', 'POST'])
def develop():
    average_points, user_count = average_points_fn()
    if request.method == 'POST':

            entered_user = request.form['entered_user']
            userdata = return_userdata(entered_user)
            if userdata:
                return render_template('develop.html', userdata=userdata, average_points=average_points, user_count=user_count, entered_user=entered_user)
            else:
                error = "No user has this username."
                return render_template('develop.html', average_points=average_points, user_count=user_count, error=error)
       
    return render_template('develop.html', average_points=average_points, user_count=user_count)

@app.route("/dev_ranking", methods=['GET', 'POST'])
def dev_ranking():
    ranking_data = generate_ranking_data()
    todays_ranking_data = generate_todays_data()
    return render_template('dev_ranking.html', ranking=ranking_data, todays_ranking=todays_ranking_data)

@app.route("/show_user", methods=['GET', 'POST'])
def show_user():
    user_data = show_user_data()
    return render_template('show_user.html', user_data=user_data)

@app.route("/data_modify", methods=['GET', 'POST'])
def data_modify():
    username = request.args.get('user')
    userdata = return_userdata(username)
       
    return render_template('data_modify.html', userdata=userdata)


if __name__ == '__main__':
    app.run(debug=True)
