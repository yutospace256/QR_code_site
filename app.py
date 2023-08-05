from flask import Flask, render_template, request, redirect, url_for, session, flash, get_flashed_messages
import random
from datetime import date
from datetime import datetime, timedelta
import mysql.connector
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import json
import dbconfig

app = Flask(__name__)

app.secret_key = 'jKtZuPqEhXrMnLbVgYf'
app.permanent_session_lifetime = timedelta(minutes=10)


def add_user_to_data(username):
    cnx = mysql.connector.connect(user=dbconfig.user3, password=dbconfig.user_pass, host=dbconfig.sql_host, database=dbconfig.db_name)
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
    cnx = mysql.connector.connect(user=dbconfig.user1, password=dbconfig.user_pass, host=dbconfig.sql_host, database=dbconfig.db_name)
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
    cnx = mysql.connector.connect(user=dbconfig.user1, password=dbconfig.user_pass, database=dbconfig.db_name)
    cursor = cnx.cursor()

    # Execute the query
    query = "SELECT * FROM users WHERE username = %s"
    cursor.execute(query, (username, ))

    # Fetch the column names
    column_names = cursor.column_names

    # Fetch the user data
    user_data = cursor.fetchone()

    user_dict = None
    
    if user_data != None:
        # Create a dictionary using column names as keys
        user_dict = dict(zip(column_names, user_data))

    # Close the cursor and connection
    cursor.close()
    cnx.close()

    return user_dict

def get_random_username():
    while True:
        username = str(random.randint(1000, 9999))
        if get_user_by_username(username) is None:
            return username


def game_start(username, game_time):

    cnx = mysql.connector.connect(user=dbconfig.user1, password=dbconfig.user_pass, database=dbconfig.db_name)
    cursor = cnx.cursor()
    game_upd = ("UPDATE users "
                  "SET game_played = %s, game_time = %s "
                  "WHERE username = %s")
    cursor.execute(game_upd, (True, game_time, username, ))

    cnx.commit()

    cursor.close()
    cnx.close()

def get_logs(username):
    cnx = mysql.connector.connect(user=dbconfig.user1, password=dbconfig.user_pass, database=dbconfig.db_name)
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

    cnx = mysql.connector.connect(user=dbconfig.user3, password=dbconfig.user_pass, host=dbconfig.sql_host, database=dbconfig.db_name)
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
    cnx = mysql.connector.connect(user=dbconfig.user1, password=dbconfig.user_pass, database=dbconfig.db_name)
    cursor = cnx.cursor()
    update_query = "UPDATE users SET points = points + %s WHERE username = %s"
    cursor.execute(update_query, (earned_points, username))

    cnx.commit()

    cursor.close()
    cnx.close()

def average_points_fn():
    # Establish a connection to the MySQL database
    cnx = mysql.connector.connect(user=dbconfig.user3, password=dbconfig.user_pass, database=dbconfig.db_name)
    cursor = cnx.cursor()

    # Execute the query
    query = "SELECT AVG(points) FROM users WHERE points > 0"
    cursor.execute(query)

    # Fetch the average points
    average_points = cursor.fetchone()[0]
    average_points = round(average_points, 3)

    # Execute another query to get the count of users with points > 1
    count_query = "SELECT COUNT(*) FROM users WHERE points > 0"
    cursor.execute(count_query)

    # Fetch the count
    user_count = cursor.fetchone()[0]

    # Close the cursor and connection
    cursor.close()
    cnx.close()

    return average_points, user_count

def show_user_data():
    cnx = mysql.connector.connect(user=dbconfig.user3, password=dbconfig.user_pass, host=dbconfig.sql_host, database=dbconfig.db_name)
    cursor = cnx.cursor()

    # Fetch the user data from the MySQL table
    query = "SELECT * FROM users ORDER BY game_time DESC"
    cursor.execute(query)
    user_data = cursor.fetchall()

    column_names = cursor.column_names

    i = 0
    recent_data = []
    for user in user_data:
        if user[4] == None:
            break
        user_dict = dict(zip(column_names, user))
        recent_data.append(user_dict)
        i +=1
        if i > 39:
            break

    cursor.close()
    cnx.close()
    return recent_data

def change_user_data(username, column, new_data):
    cnx = mysql.connector.connect(user=dbconfig.user1, password=dbconfig.user_pass, host=dbconfig.sql_host, database=dbconfig.db_name)
    cursor = cnx.cursor()
    # Change the value of the users table in mysql
    change_query = "UPDATE users SET {} = %s WHERE username = %s".format(column)
    cursor.execute(change_query, (new_data, username, ))

    cnx.commit()
    cursor.close()
    cnx.close()

def check_column(column, new_data):
    # Check if the data type of the column is correct.
    if column == "points":
        try:
            new_data = int(new_data)
        except ValueError:
            return False
    # Check if the data type of game_played is BOOLEAN type
    elif column == "game_played":
        if new_data.lower() not in ["0", "1"]:
            return False
    # Check if the data type of game_time is datetime type
    elif column == "game_time":
        try:
            datetime.strptime(new_data, "%Y-%m-%d %H:%M:%S")
        except ValueError:
            return False
    elif column == "nickname":
        if len(new_data) > 20:
            return False
    else:
        return False

    return True

def get_site_data(site_number):
    cnx = mysql.connector.connect(user=dbconfig.user1, password=dbconfig.user_pass, host=dbconfig.sql_host, database=dbconfig.db_name)
    cursor = cnx.cursor()

    # site_number takes the value of site_number from the site_data table
    query = "SELECT * FROM site_data WHERE site_number = %s"
    cursor.execute(query, (site_number, ))
    site_data = cursor.fetchone()

     # Fetch the column names
    column_names = cursor.column_names

    # Create a dictionary with column names and values
    site_data = dict(zip(column_names, site_data))

    cursor.close()
    cnx.close()
    
    return site_data

def insert_site_data():
    cnx = mysql.connector.connect(user=dbconfig.user1, password=dbconfig.user_pass, host=dbconfig.sql_host, database=dbconfig.db_name)
    cursor = cnx.cursor()

    # Refer to the site_number column from the logs table and count how many have the same value
    query = "SELECT site_number, COUNT(*) FROM logs GROUP BY site_number"
    cursor.execute(query)
    site_data = cursor.fetchall()
    
    # Count the non-zeor number in the points column of the logs table by site_number column
    query = "SELECT site_number, COUNT(*) FROM logs WHERE points != 0 GROUP BY site_number"
    cursor.execute(query)
    site_data_2 = cursor.fetchall()

    # Assign the above site_data to the get_count column of the site_data table
    for site in site_data:
        update_query = "UPDATE site_data SET get_count = %s WHERE site_number = %s"
        values = (site[1], site[0])
        cursor.execute(update_query, values)
    
    # Difference of counts from site_data, site_data_2 by site_number
    for site in site_data_2:
        update_query = "UPDATE site_data SET correct_count = %s WHERE site_number = %s"
        values = (site[1], site[0])
        cursor.execute(update_query, values)
    
    cnx.commit()
    cursor.close()
    cnx.close()

def dev_create_site_data(site_type, points, title):
    cnx = mysql.connector.connect(user=dbconfig.user3, password=dbconfig.user_pass, host=dbconfig.sql_host, database=dbconfig.db_name)
    cursor = cnx.cursor()

    # Get the site_number and the site_type of the data whose site_type is site_type in the site_data table.
    query = "SELECT site_number, site_type FROM site_data WHERE site_type = %s"
    cursor.execute(query, (site_type, ))
    site_data = cursor.fetchall()
    # Create new site_number
    if len(site_data) == 0:
        new_site_number = site_type + "01"
    else:
        new_site_number = int(site_data[-1][0]) + 1
    
    # Insert the new_site_number and site_type into the site_data table
    # Columns and values are site_type=site_type, site_number=new_site_number,poitns=points,correct_count=0,get_count=0,title=title, hp=1,question="",choices =[]].
    insert_query = "INSERT INTO site_data (site_type, site_number, points, correct_count, get_count, title, hp, question, choices) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"
    values = (site_type, new_site_number, points, 0, 0, title, 1, "", "[]")
    cursor.execute(insert_query, values)

    cnx.commit()
    cursor.close()
    cnx.close()

    return new_site_number

def change_site_data(site_number, column, new_data):
    cnx = mysql.connector.connect(user=dbconfig.user1, password=dbconfig.user_pass, host=dbconfig.sql_host, database=dbconfig.db_name)
    cursor = cnx.cursor()
    if column == "choices":
        # Retrieve the existing JSON value from the column
        query = "SELECT choices FROM site_data WHERE site_number = %s"
        cursor.execute(query, (site_number, ))
        choices = cursor.fetchone()[0]
        # Convert the existing JSON value to a Python list
        choices = json.loads(choices)
        # Add the new entry to the existing list
        choices.append(new_data)
        # Convert the list to JSON
        choices = json.dumps(choices)
        # Make the data in the column of site_number=site_number in the site_data table choices
        change_query = "UPDATE site_data SET choices = %s WHERE site_number = %s"
        cursor.execute(change_query, (choices, site_number, ))
    else:
        # Make the data in the column of site_number=site_number in the site_data table new_data
        change_query = "UPDATE site_data SET {} = %s WHERE site_number = %s".format(column)
        cursor.execute(change_query, (new_data, site_number, ))

    cnx.commit()
    cursor.close()
    cnx.close()

def get_all_site_data():
    cnx = mysql.connector.connect(user=dbconfig.user1, password=dbconfig.user_pass, host=dbconfig.sql_host, database=dbconfig.db_name)
    cursor = cnx.cursor()

    # Fetch the user data from the MySQL table
    query = "SELECT * FROM site_data ORDER BY site_number ASC"
    cursor.execute(query)
    site_data = cursor.fetchall()

    cursor.close()
    cnx.close()

    return site_data

def generate_ranking_data():
    cnx = mysql.connector.connect(user=dbconfig.user3, password=dbconfig.user_pass, host=dbconfig.sql_host, database=dbconfig.db_name)
    cursor = cnx.cursor()

    # Fetch the user data from the MySQL table
    query = "SELECT * FROM users ORDER BY points DESC"
    cursor.execute(query)
    user_data = cursor.fetchall()

    ranking_data = []
    rank = 0
    prev_points = None

    for user in user_data:
        points = user[2]
        if points == 0:
            continue
        if prev_points is None or points < prev_points:
            rank += 1
        if rank <= 5:
            username = user[1]
            game_played = user[3]
            game_time = user[4]
            nickname = user[5]
            ranking_data.append({
                "rank": rank,
                "username": username,
                "points": points,
                "game_played": game_played,
                "game_time": game_time,
                "nickname": nickname
            })
        else:
            break
        prev_points = points

    # Store the ranking data in the MySQL table
    truncate_query = "TRUNCATE TABLE ranking"
    cursor.execute(truncate_query)

    insert_query = ("INSERT INTO ranking "
                    "(`ranking`, username, points, game_played, game_time, nickname) "
                    "VALUES (%s, %s, %s, %s, %s, %s)")

    for rank_data in ranking_data:
        values = (rank_data["rank"], rank_data["username"], rank_data["points"], rank_data["game_played"], rank_data["game_time"], rank_data["nickname"])
        cursor.execute(insert_query, values)

    cnx.commit()

    cursor.close()
    cnx.close()

    return ranking_data

def analyze_and_generate_graphs(user_count):
    cnx = mysql.connector.connect(user=dbconfig.user1, password=dbconfig.user_pass, host=dbconfig.sql_host, database=dbconfig.db_name)
    cursor = cnx.cursor()

    # Retrieve data from the site_data table
    query = "SELECT * FROM site_data ORDER BY site_number ASC"
    cursor.execute(query)
    site_data = cursor.fetchall()


    cursor.close()
    cnx.close()

    # Separate site numbers, correct counts, and get minus correct counts
    site_numbers = [str(site[2]) for site in site_data]
    correct_counts = [site[4] for site in site_data]
    incorrect_counts = [site[5] - site[4] for site in site_data]
    data_labels = [site[5] for site in site_data]

    # Create the bar graph
    fig, ax = plt.subplots()
    x = range(len(site_numbers))  # Use numerical values for the x-axis
    ax.bar(x, correct_counts, label='Correct', color='blue')
    ax.bar(x, incorrect_counts, bottom=correct_counts, label='Incorrect', color='red')

    # Add data labels. If 0, do not display.
    for i, v in enumerate(data_labels):
        if v != 0:
            ax.text(i, v, str(v), ha='center', va='bottom')

    ax.set_xlabel('Site Number')
    ax.set_ylabel('Count')
    ax.set_title('Site Data Analysis')
    ax.set_ylim(0, user_count)
    ax.set_xticks(x)  # Use numerical values for the x-axis
    ax.set_xticklabels(site_numbers, rotation=40)

    ax.legend()

    # Save the bar graph
    graph_path = 'static/img/bar_graph.png'
    fig.savefig(graph_path)
    plt.close()


    # Create pie charts for each site_number
    pie_images = []
    for site_number, correct_count, incorrect_count in zip(site_numbers, correct_counts, incorrect_counts):
        if correct_count == 0 and incorrect_count == 0:
            continue
        else:
            # Conditional branching when the first character of site_number is 2
            if site_number[0] == '2':
                fig, ax = plt.subplots()
                ax.pie([correct_count, incorrect_count], labels=['Correct', 'Incorrect'], autopct='%1.1f%%', colors=['blue', 'red'])
                ax.set_title('Site Number: ' + site_number)
                ax.legend()
                pie_path = 'static\img\pie_graphs/pie_' + site_number + '.png'
                fig.savefig(pie_path)
                plt.close()
                pie_images.append(pie_path)

    return pie_images

def generate_todays_data():
    cnx = mysql.connector.connect(user=dbconfig.user3, password=dbconfig.user_pass, host=dbconfig.sql_host, database=dbconfig.db_name)
    cursor = cnx.cursor()

    # Fetch the user data from the MySQL table
    query = "SELECT * FROM users ORDER BY points DESC"
    cursor.execute(query)
    user_data = cursor.fetchall()

    todays_data = []
    today = date.today()
    today_str = today.strftime("%Y-%m-%d")
    rank = 0
    prev_points = None

    for user in user_data:
        points = user[2]
        if points == 0:
            continue
        game_time_obj = user[4]
        game_time_str = game_time_obj.strftime("%Y-%m-%d")
        if game_time_str == today_str:
            if prev_points is None or points < prev_points:
                rank += 1
            if rank <= 5:
                username = user[1]
                game_played = user[3]
                game_time = user[4]
                nickname = user[5]
                todays_data.append({
                    "rank": rank,
                    "username": username,
                    "points": points,
                    "game_played": game_played,
                    "game_time": game_time,
                    "nickname": nickname
                })
            else:
                break
            prev_points = points
            
        # Store the ranking data in the MySQL table
    truncate_query = "TRUNCATE TABLE ranking"
    cursor.execute(truncate_query)

    insert_query = ("INSERT INTO todays_ranking "
                    "(ranking, username, points, game_played, game_time, nickname) "
                    "VALUES (%s, %s, %s, %s, %s, %s)")

    for rank_data in todays_data:
        values = (rank_data["rank"], rank_data["username"], rank_data["points"], rank_data["game_played"], rank_data["game_time"], rank_data["nickname"])
        cursor.execute(insert_query, values)

    cnx.commit()

    cursor.close()
    cnx.close()

    return todays_data

def log_check(username, site_number):
    cnx = mysql.connector.connect(user=dbconfig.user1, password=dbconfig.user_pass, database=dbconfig.db_name)
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
    if username == "DEVELOPER":
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
    points = user["points"] if user else 0
    game_played = user["game_played"] if user else False
    nickname = user["nickname"] if user else None
    if request.method == 'POST' and 'gamestart' in request.form:
        start_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        game_start(username, start_time)
        return redirect(url_for('game', user=username))
    return render_template("personal.html", username=username, points=points, game_played=game_played, ranking=ranking_data, nickname=nickname)

@app.route('/game')
def game():
    username = request.args.get('user')
    user = get_user_by_username(username)
    points = user["points"] if user else 0
    start_time = user["game_time"] if user else 0
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
    nickname = user["nickname"] if user else None
    site_data = get_site_data(site_number)
    value = site_data["points"]
    char_name = site_data["title"]
    
    if request.method == 'POST':
        earned = log_check(username, site_number)
        if earned == False:
            points_earned = int(request.form.get('points', 0))
            add_logs_list(username, points_earned, nickname, site_number)
            add_points_to_user(username, points_earned)
            return render_template('points_sites/add_points.html', username=username, value=value, char_name=char_name, site_number=site_number, points_earned=points_earned, nickname=nickname)
        else:
            error = "二回目以降はポイント獲得できません！"
            points_earned = "0"
            return render_template('points_sites/add_points.html', username=username, site_number=site_number, value=value, char_name=char_name, points_earned=points_earned, error=error)

    return render_template('points_sites/add_points.html', username=username, site_number=site_number, value=value, char_name=char_name, points_earned=None)


@app.route('/quiz_points', methods=['GET', 'POST'])
def quiz_points():
    site_number = request.args.get('site')
    username = request.args.get('user')
    user = get_user_by_username(username)
    nickname = user["nickname"] if user else None
    site_data = get_site_data(site_number)
    value = site_data["points"]
    char_name = site_data["title"]
    question = site_data["question"]
    choices_json = site_data["choices"]
    choices = json.loads(choices_json)
               
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
            return render_template("points_sites/quiz_points.html", username=username, site_number=site_number, value=value, char_name=char_name, question=question, choices=choices, points_earned=points_earned, quiz_correct=quiz_correct)
        else:
            error = "二回目以降はポイント獲得できません！"
            points_earned = "0"
            quiz_correct = False
            return render_template("points_sites/quiz_points.html", username=username, site_number=site_number, value=value, char_name=char_name, question=question, choices=choices, points_earned=points_earned, quiz_correct=quiz_correct, error=error)

    return render_template("points_sites/quiz_points.html", username=username, site_number=site_number, value=value, char_name=char_name, question=question, choices=choices, points_earned=None, quiz_correct=None)


@app.route('/hp_points', methods=['GET', 'POST'])
def hp_points():
    site_number = request.args.get('site')
    username = request.args.get('user')
    user = get_user_by_username(username)
    nickname = user["nickname"] if user else None
    site_data = get_site_data(site_number)
    value = site_data["points"]
    char_name = site_data["title"]
    hp = site_data["hp"]

    if request.method == 'POST':
        earned = log_check(username, site_number)
        if earned == False:
            points_earned = int(request.form.get('points', 0))
            add_logs_list(username, points_earned, nickname, site_number)
            add_points_to_user(username, points_earned)

            return render_template("points_sites/hp_points.html", username=username, site_number=site_number, value=value, char_name=char_name, hp=hp, points_earned=points_earned)
        else:
            error = "二回目以降はポイント獲得できません！"
            points_earned = "0"
            return render_template("points_sites/hp_points.html", username=username, site_number=site_number, value=value, char_name=char_name, hp=hp, points_earned=points_earned, error=error)

    return render_template("points_sites/hp_points.html", username=username, site_number=site_number, value=value, char_name=char_name, hp=hp)

@app.route("/develop", methods=['GET', 'POST'])
def develop():
    average_points, user_count = average_points_fn()
    insert_site_data()
    # Call the analyze_and_generate_graphs function
    pie_images = analyze_and_generate_graphs(user_count)

    if request.method == 'POST':
        entered_user = request.form['entered_user']
        userdata = get_user_by_username(entered_user)
        if userdata:
            return render_template('develop.html', userdata=userdata, average_points=average_points, user_count=user_count, entered_user=entered_user, filepaths=pie_images)
        else:
            error = "No user has this username."
            return render_template('develop.html', average_points=average_points, user_count=user_count, error=error, filepaths=pie_images)
       
    return render_template('develop.html', average_points=average_points, user_count=user_count, filepaths=pie_images)

@app.route("/dev_ranking", methods=['GET', 'POST'])
def dev_ranking():
    ranking_data = generate_ranking_data()
    todays_ranking_data = generate_todays_data()
    return render_template('dev_ranking.html', ranking=ranking_data, todays_ranking=todays_ranking_data)

@app.route("/show_user", methods=['GET', 'POST'])
def show_user():
    user_data = show_user_data()
    return render_template('.html', user_data=user_data)

@app.route('/data_modify', methods=['GET', 'POST'])
def data_modify():
    username = request.args.get('user')
    userdata = get_user_by_username(username)
    if request.method == 'POST':
        username = request.form['change_user']
        column = request.form['column']
        new_data = request.form['new_data']
        if check_column(column, new_data) == False:
            flash("Data type mismatch. Please check the data type entered.", "error")
        else:
            change_user_data(username, column, new_data)
            flash("User data updated successfully.", "success")
        return redirect(url_for('data_modify', user=username))
    return render_template("data_modify.html", username=username, userdata=userdata)

@app.route('/dev_create_site', methods=['GET', 'POST'])
def dev_create_site():
    if request.method == 'POST':
        progress = request.form ['progress']
        if progress == "step1":
            site_type = request.form['site_type']
            title = request.form['title']
            points = request.form['points']
            new_site_number = dev_create_site_data(site_type, points, title)
            if site_type == "2":
                question = request.form['question']
                change_site_data(new_site_number, column="question", new_data=question)
                progress = "step2"
            elif site_type == "3":
                hp = request.form['hp']
                change_site_data(new_site_number, column="hp", new_data=hp)
                progress = "completed"
            else: 
                progress = "completed"
            current_site_data = get_site_data(new_site_number)
            choices_json = current_site_data["choices"]
            current_choices_data = json.loads(choices_json)
            return render_template("dev_create_site.html", progress=progress, new_site_number=new_site_number, current_site_data=current_site_data, current_choices_data=current_choices_data)
        
        elif progress == "step2":
            if progress != "completed":
                choice_value = request.form.getlist('choice_value')
                choice_text = request.form.getlist('choice_text')
                new_site_number = request.form['new_site_number']
                # Make a dictionary of choice_value and choice_text and a list of them as choices_data.
                
                combined_dict = {'value': choice_value[0], 'choice': choice_text[0]}
                change_site_data(new_site_number, column="choices", new_data=combined_dict)

                current_site_data = get_site_data(new_site_number)
                choices_json = current_site_data["choices"]
                current_choices_data = json.loads(choices_json)
                return render_template("dev_create_site.html", progress=progress, new_site_number=new_site_number, current_site_data=current_site_data, current_choices_data=current_choices_data)
            
        elif progress == "completed":
            new_site_number = request.form['new_site_number']
            current_site_data = get_site_data(new_site_number)
            choices_json = current_site_data["choices"]
            current_choices_data = json.loads(choices_json)
            return render_template("dev_create_site.html", progress=progress, new_site_number=new_site_number, current_site_data=current_site_data, current_choices_data=current_choices_data)
        return render_template("dev_create_site.html", progress=progress)
    progress = "step1"
    all_site_data = get_all_site_data()
    return render_template("dev_create_site.html", progress=progress, all_site_data=all_site_data)

@app.route('/dev_site_modify', methods=['GET', 'POST'])
def dev_site_modify():
    site_number = request.args.get('site')
    current_site_data = get_site_data(site_number)
    if site_number[0] == "2":
        choices_json = current_site_data["choices"]
        current_choices_data = json.loads(choices_json)
        return render_template("dev_site_modify.html", site_number=site_number, current_site_data=current_site_data, current_choices_data=current_choices_data)

    return render_template("dev_site_modify.html", site_number=site_number, current_site_data=current_site_data)

if __name__ == '__main__':
    app.run(debug=True)
