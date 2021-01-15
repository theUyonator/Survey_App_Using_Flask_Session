from flask import Flask, request, render_template, redirect, session, flash
from flask_debugtoolbar import DebugToolbarExtension
from surveys import surveys

# We are going to be saving our responses in memory in the browser cookie using Flask session.
# To do this, we'll need a key value pair, our consistent response key is given below
RESPONSE_KEY = "responses"

app = Flask(__name__)

app.config["SECRET_KEY"] = "SURVEY"

app.config["DEBUG_TB_INTERCEPT_REDIRECTS"] = False

debug = DebugToolbarExtension(app)


@app.route("/")
def survey_home():
    """This function shows the homepage for the survey"""

    satisfaction = surveys["satisfaction"]

    return render_template("root.html", title = satisfaction.title, instruction = satisfaction.instructions)

@app.route("/begin", methods=["POST"])
def begin():
    """This function redirects the user to the first question in the survey and makes sure there is nothing saved in the session"""

    session[RESPONSE_KEY] = []

    return redirect("/questions/0")

@app.route("/questions/<int:qid>")
def questions(qid):
    """This function shows a question in a survey and displays the options for these question, 
    it also checks if a response has been provided and moves you along if true"""

    responses = session.get(RESPONSE_KEY)
    satisfaction = surveys["satisfaction"]
    questions_list = satisfaction.questions
    # question = question_obj.question
    # choices = question_obj.choices

    if responses is None:
        """That means the user wants to start the questionaire too soon and has entered the question number directly into the URL"""
        return redirect("/")

    if len(responses) == len(questions_list):
        """That means all responses have been provided , we want to send the user to the thank you page"""
        return redirect("/final")
    
    if len(responses) != qid:
        """That means if the user wants to jump ahead to a question without answering the one ahead of it"""
        flash(f"Invalid question id: {qid}")
        return redirect(f"/questions/{len(responses)}")

    question_obj = questions_list[qid]

    return render_template("questions.html", question_id = qid, question = question_obj.question, choices = question_obj.choices)

@app.route("/answer", methods= ["POST"])
def answer_saved():
    """This function should append answer to the reponses list and redirect the user to the next question"""

    choice = request.form["choice"]
    satisfaction = surveys["satisfaction"]
    questions_list = satisfaction.questions
    responses = session.get(RESPONSE_KEY)
    responses.append(choice)
    session[RESPONSE_KEY] = responses

    if len(responses) == len(questions_list):
        """The user is done answerign all the questions and should be redirected to the final page"""
        return redirect("/final")

    else:
        """The user isn't done with all the questions and will move on to the next question"""
        return redirect(f"/questions/{len(responses)}")

    # return redirect("questions.html")

@app.route("/final")
def final():
    """This function shows the final page of the survey"""
    satisfaction = surveys["satisfaction"]
    return render_template("final.html", title = satisfaction.title)