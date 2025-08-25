from flask import Flask, render_template, request, jsonify, flash, redirect, url_for, abort, session
from flask_login import LoginManager, current_user, login_user, logout_user, login_required, UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import create_engine
import argparse

def create_app(password):
    app = Flask(__name__)
    app.secret_key = 'dsci551'

    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'login'

    # Define User class
    class User:
        def __init__(self, user_id, user_name, email, password_hash):
            self.user_id = user_id
            self.user_name = user_name
            self.email = email
            self.password_hash = password_hash

        @property
        def is_authenticated(self):
            return True

        @property
        def is_active(self):
            return True

        @property
        def is_anonymous(self):
            return False

        def get_id(self):
            return str(self.user_id)
        
    @login_manager.user_loader
    def load_user(user_id):
        engine = create_engine(f'mysql+pymysql://root:{password}@localhost/nba_0')
        connection = engine.raw_connection()
        cur = connection.cursor()
        try:
            cur.execute("SELECT user_id, user_name, email, password_hash FROM user_info WHERE user_id = %s", (user_id,))
            user_data = cur.fetchone()
            
            if user_data:
                return User(user_id=user_data[0], user_name=user_data[1], email=user_data[2], password_hash=user_data[3])
        finally:
            connection.close()
        return None

    @app.route('/signup', methods=['GET', 'POST'])
    def signup():
        if request.method == 'POST':
            user_name = request.form['user_name']
            email = request.form['email']
            user_password = request.form['password']
            hashed_password = generate_password_hash(user_password)
            #print(user_name, email, hashed_password)

            engines = [
            create_engine(f'mysql+pymysql://root:{password}@localhost/nba_0'),
            create_engine(f'mysql+pymysql://root:{password}@localhost/nba_1')
            ]

            for engine in engines:
                connection = engine.raw_connection()
                cur = connection.cursor()
                cur.execute("SELECT * FROM user_info WHERE user_name = %s OR email = %s", (user_name, email))
                result = cur.fetchone()
                cur.close()
                if result:
                    flash('Username or Email already exists.')
                    return redirect(url_for('signup'))
                
                cur = connection.cursor()
                cur.execute("INSERT INTO user_info (user_name, email, password_hash) VALUES (%s, %s, %s)", (user_name, email, hashed_password))
                connection.commit()
                cur.close()
                flash('Account created successfully!')

        return render_template('signup.html')

    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if request.method == 'POST':
            email = request.form['email']
            user_password = request.form['password']
            engines = [
                create_engine(f'mysql+pymysql://root:{password}@localhost/nba_0'),
                create_engine(f'mysql+pymysql://root:{password}@localhost/nba_1')
            ]

            for engine in engines:
                    connection = engine.raw_connection()
                    cur = connection.cursor()
                    cur.execute("SELECT user_id, user_name, email, password_hash FROM user_info WHERE email = %s", (email,))
                    user_data = cur.fetchone()
                    if user_data and check_password_hash(user_data[3], user_password):
                        user = User(user_id=user_data[0], user_name=user_data[1], email=user_data[2], password_hash=user_data[3])
                        login_user(user)
                        
                        return redirect(url_for('index'))
                    else:
                        flash('Invalid email or password')
                    cur.close()
        

        return render_template('login.html')       

    @app.route('/logout')
    @login_required
    def logout():
        logout_user()
        session.clear()
        flash('You have been logged out.')
        return redirect(url_for('index'))


    @app.route('/')
    @app.route('/index')
    def index():
        player_data = []
        followed_players = session.get('followed_players', [])
        engines = [
            create_engine(f'mysql+pymysql://root:{password}@localhost/nba_0'),
            create_engine(f'mysql+pymysql://root:{password}@localhost/nba_1')
        ]

        for engine in engines:
            connection = engine.raw_connection()
            try:
                cur = connection.cursor()
                cur.execute("SELECT player_name, team_abbr, person_id, team_id FROM current_players WHERE team_abbr <> ''")
                player_info = cur.fetchall()
                player_data.extend(player_info)  # Use extend to flatten the list
                cur.close()
            finally:
                connection.close()

        return render_template('index.html', player_data=player_data, is_authenticated=current_user.is_authenticated, followed_players=followed_players)

    @app.route('/add_player', methods=['POST'])
    def add_player():
        person_id = request.form['person_id']
        player_name = request.form['player_name']
        position = request.form['position']
        height = "'" + request.form['height']
        weight = request.form['weight']
        last_attended = request.form['last_attended']
        country = request.form['country']
        team_id = request.form['team_id']
        team = request.form['team']
        pts = request.form['pts']
        dreb = request.form['dreb']
        ast = request.form['ast']
        gp = request.form['gp']

        engines = [
            create_engine(f'mysql+pymysql://root:{password}@localhost/nba_0'),
            create_engine(f'mysql+pymysql://root:{password}@localhost/nba_1')
        ]

        # Determine the engine to use based on team_id % 2
        engine_index = int(team_id) % 2
        engine = engines[engine_index]

        connection = engine.raw_connection()
        try:
            cur = connection.cursor()
            cur.execute(
                "INSERT INTO all_draft_picks (person_id, player_name, team_id, team_abbr) VALUES (%s, %s, %s, %s)",
                (person_id, player_name, team_id, team)
            )
            connection.commit()
            cur.execute("INSERT INTO current_players (person_id, player_name, team_id, team_abbr) VALUES (%s, %s, %s, %s)",
                        (person_id, player_name, team_id, team))
            connection.commit()
            cur.execute("INSERT INTO player_info (name, position, height, weight, last_attended, country) VALUES (%s, %s, %s, %s, %s, %s)",
                        (player_name, position, height, weight, last_attended, country))
            connection.commit()
            cur.execute("INSERT INTO all_players_season_stats_2023_2024 (player_name, team_id, team_abbr, PTS, DREB, AST, GP) VALUES (%s, %s, %s, %s, %s, %s, %s)",
                        (player_name, team_id, team, pts, dreb, ast, gp))
            connection.commit()
            cur.close()

        except Exception as e:
            return jsonify({'error': str(e)})
        finally:
            connection.close()
        return jsonify({'success': True})

    @app.route('/query', methods=['GET','POST'])
    @login_required
    def query():
        if request.method == 'GET':
            return render_template('query.html')
        # print('post')
        query = request.form['query']
        engines = [
            create_engine(f'mysql+pymysql://root:{password}@localhost/nba_0'),
            create_engine(f'mysql+pymysql://root:{password}@localhost/nba_1')
        ]
        result = []
        for engine in engines:
            connection = engine.raw_connection()
            try:
                cur = connection.cursor()
                cur.execute(query)
                result.append(cur.fetchall())
                cur.close()
            finally:
                connection.close()
            if result:
                break
        
        return render_template('query.html', query=query, result=result)


    @app.route('/update_player', methods=['POST'])
    @login_required
    def update_player():
        data = request.json
        playerId = data['playerId']
        playerName = data['playerName']
        teamName = data['teamName']
        # print(type(playerId), type(playerName), type(teamName))

        engines = [
            create_engine(f'mysql+pymysql://root:{password}@localhost/nba_0'),
            create_engine(f'mysql+pymysql://root:{password}@localhost/nba_1')
        ]
        for engine in engines:
            connection = engine.raw_connection()
            try:
                cur = connection.cursor()
                update_query = """
                UPDATE current_players 
                SET player_name = %s , team_abbr = %s
                WHERE person_id = %s;
                """
                cur.execute(update_query, (playerName, teamName, playerId))
                connection.commit()
                # player_info = cur.fetchall()
                # print(player_info)
                cur.close()
            finally:
                connection.close()

        return jsonify({'success': True}), 200

    @app.route('/delete_player', methods=['POST'])
    @login_required
    def delete_player():
        data = request.json
        playerId = data['playerId']
        # print(type(playerId), type(playerName), type(teamName))

        engines = [
            create_engine(f'mysql+pymysql://root:{password}@localhost/nba_0'),
            create_engine(f'mysql+pymysql://root:{password}@localhost/nba_1')
        ]
        for engine in engines:
            connection = engine.raw_connection()
            try:
                cur = connection.cursor()
                delete_query = """
                DELETE 
                FROM all_draft_picks
                WHERE person_id = %s;
                """
                cur.execute(delete_query, (playerId))
                connection.commit()
                # player_info = cur.fetchall()
                # print(player_info)
                cur.close()
            finally:
                connection.close()

        return jsonify({'success': True}), 200
        
    @app.route('/player_stats/<int:player_id>', methods=['GET', 'POST'])
    def player_stats(player_id):
        player_stat = None
        engines = [
            create_engine(f'mysql+pymysql://root:{password}@localhost/nba_0'),
            create_engine(f'mysql+pymysql://root:{password}@localhost/nba_1')
        ]

        for engine in engines:
            connection = engine.raw_connection()
            cur = connection.cursor()
            cur.execute("SELECT ps.*, cp.person_id, pi.* FROM all_players_season_stats_2023_2024 ps JOIN current_players cp ON ps.player_name = cp.player_name JOIN player_info pi ON ps.player_name = pi.name WHERE person_id = %s", (player_id,))
            player_stat = cur.fetchone()
            cur.close()
            if player_stat:
                break

        if player_stat is None:
            abort(404)  # Player not found, return 404 error

        followed_players = session.get('followed_players', [])
        is_followed = player_id in followed_players
        # print(is_followed)
        # print(is_followed)
        return render_template('player_stats.html', player_stat=player_stat, is_followed=is_followed)

    @app.route('/follow_player/<int:player_id>', methods=['POST'])
    def follow_player(player_id):
        try:
            followed_players = session.get('followed_players', [])
            if player_id not in followed_players:
                followed_players.append(player_id)
                # print(followed_players)
                session['followed_players'] = followed_players.copy()
                # print(session['followed_players'])
                session.modified = True
                return jsonify(success=True)
        except Exception as e:
            print(e)

        return jsonify(success=False)
    @app.route('/is_followed/<int:player_id>', methods=['GET'])
    def is_followed(player_id):
        followed_players = session.get('followed_players', [])
        return jsonify(is_followed=player_id in followed_players)


    @app.route('/unfollow_player/<int:player_id>', methods=['POST'])
    def unfollow_player(player_id):
        try:
            followed_players = session.get('followed_players', [])
            # print(followed_players)
            if player_id in followed_players:
                followed_players.remove(player_id)
                session['followed_players'] = followed_players.copy()
                session.modified = True
                return jsonify(success=True)
        except Exception as e:
            print(e)

        return jsonify(success=False)
    
    return app  # return app only since we're not using SQLAlchemy ORM

def main():
    parser = argparse.ArgumentParser(description='Start a Flask app with database connections.')
    parser.add_argument('password', type=str, help='Password for MySQL root user')
    args = parser.parse_args()

    # Create app with the password provided
    app = create_app(args.password)

    # Define routes and other functionality here or inside the create_app if you prefer
    
    app.run(debug=True)

if __name__ == '__main__':
    main()
