 
from flask import Flask, render_template, request, redirect, session
import mysql.connector

import pickle
import numpy as np
popular_df=pickle.load(open('popular.pkl','rb'))
pt=pickle.load(open('pt.pkl','rb'))
books=pickle.load(open('books.pkl','rb'))
similarity_scores=pickle.load(open('similarity_scores.pkl','rb'))
course_pop_df=pickle.load(open('course.pkl','rb'))
import os
 
app = Flask(__name__, template_folder='templates', static_folder='static')
app.secret_key=os.urandom(24)  

conn=mysql.connector.connect(host="localhost", user="root", database="lmsdata", password="")
cursor=conn.cursor()
@app.route('/')
def mainpage():
    return render_template('index.html')

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/signup')
def signup():
    return render_template('signup.html')

@app.route('/home')
def home():
        if 'user_id' in session:
            return render_template('home.html',book_name=list(popular_df['Book-Title'].values),
                           author=list(popular_df['Book-Author'].values),
                           image=list(popular_df['Image-URL-M'].values),
                           votes=list(popular_df['num_ratings'].values),
                           rating=list(popular_df['avg_rating'].values),)
        else:
             return redirect('login.html')



@app.route('/login_validation', methods=['POST'])
def login_validation():
    email=request.form.get('email')
    password=request.form.get('password')

    cursor.execute("""SELECT * FROM `users` WHERE `email` LIKE '{}' AND `password` LIKE '{}' """
                   .format(email,password))
    users=cursor.fetchall()
    if len(users)>0:
         session['user_id']=users[0][0]
         return redirect('home')
    else:
         return redirect('/')


@app.route('/add_user',methods=['POST'])
def add_user():
     name=request.form.get('aname')
     email=request.form.get('aemail')
     password=request.form.get('apassword')

     cursor.execute("""INSERT INTO `users` (`user_id`,`name`,`email`,`password` ) VALUES 
     (NULL,'{}','{}','{}')""".format(name,email,password))
     conn.commit()

     cursor.execute("""SELECT * FROM `users` WHERE `email` LIKE '{}' """.format(email))
     myuser=cursor.fetchall()
     session['user_id']=myuser[0][0]
     return redirect('/login')
                   

@app.route('/logout')
def logout():
     session.pop('user_id')
     return redirect('/')
     

@app.route('/home')
def index():
    return render_template('home.html',
                           book_name=list(popular_df['Book-Title'].values),
                           author=list(popular_df['Book-Author'].values),
                           image=list(popular_df['Image-URL-M'].values),
                           votes=list(popular_df['num_ratings'].values),
                           rating=list(popular_df['avg_rating'].values),)
                              
@app.route('/recommend')
def recommend_ui():
    return render_template('recommend.html')
@app.route('/recommend_books',methods=['post'])
def recommend():
    user_input = request.form.get('user_input')
    
    index = np.where(pt.index == user_input)[0][0]
    similar_items = sorted(list(enumerate(similarity_scores[index])), key=lambda x: x[1], reverse=True)[1:5]

    data = []
    for i in similar_items:
        item = []
        temp_df = books[books['Book-Title'] == pt.index[i[0]]]
        item.extend(list(temp_df.drop_duplicates('Book-Title')['Book-Title'].values))
        item.extend(list(temp_df.drop_duplicates('Book-Title')['Book-Author'].values))
        item.extend(list(temp_df.drop_duplicates('Book-Title')['Image-URL-M'].values))

        data.append(item)

    print(data)

    return render_template('recommend.html',data=data)


@app.route('/courses')
def courses():
         return render_template('courses.html',course_name=list(course_pop_df['Course Name'].values),
                           University=list(course_pop_df['University'].values),
                           link=list(course_pop_df['Course URL'].values),
                           ratings=list(popular_df['num_ratings'].values),)
                           


# @app.route('/login')
# def login():
#     return render_template('login.html')

# @app.route('/signup')
# def signup():
#     return render_template('signup.html')

# @app.route('/home')
# def home():
#     # if 'user_id' in session:
#         return render_template('home.html')
    # else:
    #     return redirect('/')

# @app.route('/login_validation', methods=['post'])
# def login_validation():
#     email=request.form.get('email')
#     password=request.form.get('password')

#     cursor.execute("""SELECT * FROM `users` WHERE `email` LIKE '{}' AND `password` LIKE '{}'"""
#                    .format(email,password))
#     users=cursor.fetchall()
#     if len(users)>0:
#         session['user_id']=users[0][0]
#         return redirect ('home')
#     else:
#         return redirect ('/')
    
# @app.route('/add_user',methods=['post'])
# def add_user():
#     name=request.form.get('aname')
#     email=request.form.get('aemail')
#     password=request.form.get('apassword')

#     cursor.execute("""INSERT INTO `users` (`user_id`,`name`,`email`,`password`) VALUES
#     (NULL,'{}','{}','{}')""".format(name,email,password))
#     conn.commit()
#     return " success"
#     cursor.execute("""SELECT * FROM `users` WHERE `email` LIKE '{}'""".format(email))
#     myuser=cursor.fetchall()
#     session['user_id']=myuser[0][0]
#     return redirect('/home')

# @app.route('/logout')
# def logout():
#     session.pop('user_id')
#     return redirect('/')
 

if __name__=='__main__':
    app.run(debug = True)

