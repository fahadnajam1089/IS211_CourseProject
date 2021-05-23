from flask import *
import os, re, sqlite3
import requests
from logging import FileHandler, WARNING


app = Flask(__name__)
app.secret_key = ('pass')

user_id = -1
if not app.debug:
    file_handler = FileHandler('log.log')
    file_handler.setLevel(WARNING)
    app.logger.addHandler(file_handler)
l = []
@app.route('/')
def index():
    return redirect(url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    global user_id
    if request.method == 'POST':
        #print("Here2")
        path = os.path.dirname(os.path.abspath(__file__))
        conn = sqlite3.connect(path+'/books.db')
        cur = conn.cursor()
        sql = "SELECT * FROM users where user_name = '%s' and user_password = '%s'"%(request.form['username'],request.form['password'])
        #print(sql)
        cur.execute(sql)
        info_user = cur.fetchall()
        #print(info_user)
        #if request.form['username'] != 'admin' or request.form['password'] != 'password':
        if len(info_user) != 1:
            error = 'Invalid Username or Password.'
            print("Here")
            app.logger.info('failed to log in admin')
            return render_template('/login.html', error=error)
        else:
            # add grades table when it is in db
            '''sql2 = "DELETE FROM USERS";
            cur.execute(sql2)
            cur.execute("INSERT INTO users ( user_name, user_password) VALUES ('admin','password')")
            cur.execute("INSERT INTO users ( user_name, user_password) VALUES ('Fahad','password')")

            conn.commit()
            '''
            user_id = info_user[0][0]
            print(user_id)
            session['logged_in'] = True      #start a session
            if session.get('logged_in') != None:
                print('session started')
            app.logger.info('logged in successfully admin')
            return redirect('/dashboard')
    else:
        app.logger.info('failed to log in admin')
        return render_template('/login.html', error=error)



@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    l = []
    path = os.path.dirname(os.path.abspath(__file__))
    conn = sqlite3.connect(path+'/books.db')
    cur = conn.cursor()
    # add grades table when it is in db

    print("USER",user_id)
    cur.execute("SELECT book_id, book_author, book_title, book_page,book_rating FROM books where user_id = (?)",(user_id,))
    info = cur.fetchall()   #introduce argument in render_template
    cur.execute("Select * From books")
    print(cur.fetchall())
    app.logger.info('Data Fetching successful')
    return render_template('/dashboard.html', info=info)



@app.route('/book_add', methods=['GET','POST'])
def book_add():
    if request.method == 'GET':
        return render_template('book_add.html')
    elif request.method == 'POST':
        book_author = request.form["book_author"]
        book_title = request.form["book_title"]
        book_page = request.form["book_page"]
        book_rating = request.form["book_rating"]
        try: 
            path = os.path.dirname(os.path.abspath(__file__))
            conn = sqlite3.connect(path+'/books.db')
            cur = conn.cursor()
            #print("###########")
            cur.execute("INSERT INTO books (user_id , book_author, book_title, book_page,book_rating) VALUES (?,?,?,?,?)",(user_id,book_author,book_title,book_page, book_rating))
            #print("**************")
            conn.commit()
            return render_template('dashboard.html')
        except:
            flash('Request Failed: Try Again')
            print("Error: NOT ADDED TRY AGAIN")
        finally:
            cur.execute("SELECT * From books")
            info_user = cur.fetchall()
            print(info_user)
            flash('New quiz successfully added')
            return redirect(url_for('dashboard'))

@app.route('/search', methods=['GET','POST'])
def search():
    if request.method == 'GET':
        global l
        l = []
        return render_template('search.html')
    elif request.method == 'POST':
        isbn = request.form["ISBN"]
        try:
            url = 'https://www.googleapis.com/books/v1/volumes?q=isbn:'+isbn
            #print(url)
            response = requests.get(url)
            #print(response.status_code)
            data = response.json()
            #print(data)
            
            for k,v in data.items():
                if k == 'items':
                    l.append((v[0]["id"],v[0]["volumeInfo"]["authors"],v[0]["volumeInfo"]["title"],v[0]["volumeInfo"]['pageCount'],None))
            return render_template('/search_result.html', info=l)
        except:
            
            flash('Request Failed: Try Again')
            print("Error: NOT Found TRY AGAIN")
        '''finally:
            cur.execute("SELECT * From books")
            info_user = cur.fetchall()
            print(info_user)
            flash('New quiz successfully added')
            return redirect(url_for('dashboard'))'''

@app.route('/delete_book', methods=['GET','POST'])
def delete_book():
    if request.method == 'GET':
        return render_template('delete_book.html')
    elif request.method == 'POST':
        book_id = request.form["book_id"]
        try:
            path = os.path.dirname(os.path.abspath(__file__))
            conn = sqlite3.connect(path+'/books.db')
            cur = conn.cursor()
            #print("Delete From books where book_id = %s"%(book_id))
            cur.execute("Delete From books where book_id = %s"%(book_id))
            conn.commit()
            return render_template('/dashboard.html')
        except:
            
            flash('Request Failed: Try Again')
            print("Error: DELETING TRY AGAIN")
        finally:
            return redirect(url_for('dashboard'))

@app.route('/add', methods=['GET', 'POST'])
def add():
    if request.method == 'POST':
        for key in request.form:
            button_id = key
        for i in l:
            if i[0] == button_id:
                book_author = ''    
                for j in i[1]:
                    book_author += j + ','
                book_author = book_author[:-1]
                book_title= i[2]
                book_page = i[3]
                book_rating = None
                #print(user_id,book_author,book_title,book_page, book_rating)
                try:
                    path = os.path.dirname(os.path.abspath(__file__))
                    conn = sqlite3.connect(path+'/books.db')
                    cur = conn.cursor()
                    cur.execute("INSERT INTO books (user_id , book_author, book_title, book_page,book_rating) VALUES (?,?,?,?,?)",(user_id,book_author,book_title,book_page, book_rating))
                    conn.commit()
                    return dashboard()
                except:
                    print("connection faliur")
    else:
        return render_template('search.html')



if __name__== '__main__' :
    app.run()


