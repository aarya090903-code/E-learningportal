from flask import Flask, render_template, request, send_from_directory, session, redirect
import mysql.connector

app = Flask(__name__)
app.secret_key = "elearning123"

# ---------------- DATABASE CONNECTION ----------------

db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    database="elearning"
)

cursor = db.cursor(dictionary=True)

# ---------------- HOME ----------------

@app.route("/")
def home():
    return render_template("index.html")


# ---------------- REGISTER ----------------

@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        name = request.form["name"]
        email = request.form["email"]
        password = request.form["password"]

        sql = "INSERT INTO students(name, email, password) VALUES(%s, %s, %s)"
        cursor.execute(sql, (name, email, password))
        db.commit()

        return render_template("login.html")

    return render_template("register.html")


# ---------------- LOGIN ----------------

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        email = request.form["email"]
        password = request.form["password"]

        sql = "SELECT * FROM students WHERE email=%s AND password=%s"
        cursor.execute(sql, (email, password))

        user = cursor.fetchone()

        if user:
         session["student"] = user
         return redirect("/dashboard")
        else:
            return "Invalid Email or Password"

    return render_template("login.html")


# ---------------- DASHBOARD ----------------

@app.route("/dashboard")
def dashboard():
    return render_template("dashboard.html")

@app.route("/admin", methods=["GET", "POST"])
def admin():

    if request.method == "POST":

        username = request.form["username"]
        password = request.form["password"]

        if username == "admin" and password == "admin123":
            return redirect("/admin_dashboard")

        return "Invalid Admin Login"

    return render_template("admin_login.html")

@app.route("/admin_dashboard")
def admin_dashboard():

    cursor.execute("SELECT COUNT(*) AS total FROM students")
    total_students = cursor.fetchone()["total"]

    cursor.execute("SELECT COUNT(*) AS total FROM courses")
    total_courses = cursor.fetchone()["total"]

    cursor.execute("SELECT COUNT(*) AS total FROM notes")
    total_notes = cursor.fetchone()["total"]

    cursor.execute("SELECT COUNT(*) AS total FROM videos")
    total_videos = cursor.fetchone()["total"]

    cursor.execute("SELECT COUNT(*) AS total FROM quiz")
    total_quiz = cursor.fetchone()["total"]

    return render_template(
        "admin_dashboard.html",
        total_students=total_students,
        total_courses=total_courses,
        total_notes=total_notes,
        total_videos=total_videos,
        total_quiz=total_quiz
    )

@app.route("/add_course", methods=["GET", "POST"])
def add_course():

    if request.method == "POST":

        course_name = request.form["course_name"]
        description = request.form["description"]
        image = request.form["image"]

        sql = """
        INSERT INTO courses(course_name, description, image)
        VALUES(%s,%s,%s)
        """

        cursor.execute(sql, (course_name, description, image))
        db.commit()

        return redirect("/admin_dashboard")

    return render_template("add_course.html")

@app.route("/admin/add_note", methods=["GET", "POST"])
def add_note():

    if request.method == "POST":

        title = request.form["title"]
        filename = request.form["filename"]

        sql = "INSERT INTO notes(title, filename) VALUES(%s,%s)"
        cursor.execute(sql, (title, filename))
        db.commit()

        return redirect("/admin_dashboard")

    return render_template("add_notes.html")

@app.route("/admin/add_video", methods=["GET", "POST"])
def add_video():

    if request.method == "POST":

        title = request.form["title"]
        youtube_link = request.form["video_url"]

        sql = "INSERT INTO videos(title, youtube_link) VALUES(%s,%s)"
        cursor.execute(sql, (title, youtube_link))
        db.commit()

        return redirect("/admin_dashboard")

    return render_template("add_video.html")

@app.route("/admin/add_quiz", methods=["GET", "POST"])
def add_quiz():

    if request.method == "POST":

        question = request.form["question"]
        option1 = request.form["option1"]
        option2 = request.form["option2"]
        option3 = request.form["option3"]
        option4 = request.form["option4"]
        answer = request.form["answer"]

        sql = """
        INSERT INTO quiz
        (question, option1, option2, option3, option4, answer)
        VALUES (%s,%s,%s,%s,%s,%s)
        """

        cursor.execute(sql, (
            question,
            option1,
            option2,
            option3,
            option4,
            answer
        ))

        db.commit()

        return redirect("/admin_dashboard")

    return render_template("add_quiz.html")

# ---------------- STUDENTS ----------------

@app.route("/students")
def students():

    cursor.execute("SELECT * FROM students")
    students = cursor.fetchall()

    return render_template(
        "students.html",
        students=students
    )

# ---------------- DELETE COURSE ----------------

@app.route("/delete_course/<int:id>")
def delete_course(id):

    sql = "DELETE FROM courses WHERE id=%s"

    cursor.execute(sql, (id,))
    db.commit()

    return redirect("/courses")

@app.route("/manage_courses")
def manage_courses():

    cursor.execute("SELECT * FROM courses")
    courses = cursor.fetchall()

    return render_template(
        "manage_courses.html",
        courses=courses
    )

# ---------------- COURSES ----------------

@app.route("/courses")
def courses():

    cursor.execute("SELECT * FROM courses")
    courses = cursor.fetchall()

    return render_template(
        "courses.html",
        courses=courses
    )

# ---------------- NOTES ----------------

@app.route("/notes")
def notes():

    cursor.execute("SELECT * FROM notes")
    notes = cursor.fetchall()

    return render_template("notes.html", notes=notes)


# ---------------- VIDEOS ----------------

@app.route("/videos")
def videos():

    cursor.execute("SELECT * FROM videos")
    videos = cursor.fetchall()

    return render_template("videos.html", videos=videos)


# ---------------- QUIZ ----------------

@app.route("/quiz", methods=["GET", "POST"])
def quiz():

    cursor.execute("SELECT * FROM quiz")
    questions = cursor.fetchall()

    if request.method == "POST":

        score = 0

        for q in questions:

            selected = request.form.get(f"q{q['id']}")

            print("Question:", q["question"])
            print("Selected:", selected)
            print("Correct :", q["answer"])
            print("----------------")

            if selected == q["answer"]:
                score += 1

        return render_template(
            "quiz_result.html",
            score=score,
            total=len(questions)
        )

    return render_template("quiz.html", questions=questions)


# ---------------- PROFILE ----------------

@app.route("/profile")
def profile():

    if "student" not in session:
        return redirect("/login")

    return render_template(
        "profile.html",
        student=session["student"]
    )


# ---------------- LOGOUT ----------------

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

# ---------------- DOWNLOAD NOTES ----------------

@app.route("/uploads/<filename>")
def uploaded_file(filename):
    return send_from_directory("uploads", filename)

@app.route("/edit_course/<int:id>", methods=["GET", "POST"])
def edit_course(id):

    cursor.execute(
        "SELECT * FROM courses WHERE id=%s",
        (id,)
    )

    course = cursor.fetchone()

    if request.method == "POST":

        course_name = request.form["course_name"]
        description = request.form["description"]
        image = request.form["image"]

        cursor.execute("""
        UPDATE courses
        SET course_name=%s,
            description=%s,
            image=%s
        WHERE id=%s
        """,
        (
            course_name,
            description,
            image,
            id
        ))

        db.commit()

        return redirect("/courses")

    return render_template(
        "edit_course.html",
        course=course
    )

# ---------------- DELETE COURSE ----------------


# ---------------- RUN APP ----------------

if __name__ == "__main__":
    app.run(debug=True)