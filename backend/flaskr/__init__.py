import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10


def paginate_questions(request, Choice):
    page = request.args.get("page", 1, type=int)
    start = (page - 1) * QUESTIONS_PER_PAGE
    end = start + QUESTIONS_PER_PAGE
    questions = [question.format() for question in Choice]
    pg_que = questions[start:end]
    return pg_que


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)

    """
    @TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
    """
    res = {r"/*": {"origins": "*"}}
    CORS(app, resources=res)

    """
    @TODO: Use the after_request decorator to set Access-Control-Allow
    """

    @app.after_request
    def after_request(response):
        response.headers.add(
            "Access-Control-Allow-Headers", "Content-Type,Authorization,true"
        )
        response.headers.add(
            "Access-Control-Allow-Methods", "GET,PUT,POST,DELETE,OPTIONS"
        )
        response.headers.add("Access-Control-Allow-Credentials", "true")

        return response

    """
    @TODO:
    Create an endpoint to handle GET requests
    for all available categories.
    """

    @app.get("/categories")
    def available_categories():
        try:
            AllCategories = Category.query.all()
            if AllCategories is None:
                abort(404)

            listALl = {}
            for category in AllCategories:
                listALl[category.id] = category.type
            return {"success": True, "categories": listALl}

        except:
            abort(404)

    """
    @TODO:
    Create an endpoint to handle GET requests for questions,
    including pagination (every 10 questions).
    This endpoint should return a list of questions,
    number of total questions, current category, categories.
    

    TEST: At this point, when you start the application
    you should see questions and categories generated,
    ten questions per page and pagination at the bottom of the screen for three pages.
    Clicking on the page numbers should update the questions.
    """

    @app.get("/questions")
    def get_question():
        try:

            all_questions = Question.query.order_by(Question.id).all()
            total_questions = len(all_questions)
            pg_que = paginate_questions(request, all_questions)

            if len(pg_que) == 0:
                abort(404)

            AllCategories = Category.query.all()
            if AllCategories is None:
                abort(404)

            listALl = {}
            for category in AllCategories:
                listALl[category.id] = category.type
            return {
                "success": True,
                "questions": pg_que,
                "total_questions": total_questions,
                "categories": listALl,
                "current_category": None,
            }

        except Exception as E:
            print(E)
            abort(404)

    """
    @TODO:
    Create an endpoint to DELETE question using a question ID.

    TEST: When you click the trash icon next to a question, the question will be removed.
    This removal will persist in the database and when you refresh the page.
    """

    @app.delete("/questions/<int:id>")
    def delete_question(id):
        try:
            question = Question.query.filter_by(id=id).first()
            if question is None:
                abort(404)

            question.delete()
            list_question = Question.query.order_by(Question.id).all()
            pg = paginate_questions(request, list_question)

            return jsonify(
                {
                    "success": True,
                }
            )
        except:
            abort(404)

    """
    @TODO:
    Create an endpoint to POST a new question,
    which will require the question and answer text,
    category, and difficulty score.

    TEST: When you submit a question on the "Add" tab,
    the form will clear and the question will appear at the end of the last page
    of the questions list in the "List" tab.
    """

    @app.post("/questions")
    def insert_question():
        body = request.get_json()

        new_question = body.get("question", None)
        new_answer = body.get("answer", None)
        new_category = body.get("category", None)
        new_difficulty = body.get("difficulty", None)

        # try:
        record = Question(
            question=new_question,
            answer=new_answer,
            category=new_category,
            difficulty=new_difficulty,
        )
        record.insert()
        list_question = Question.query.order_by(Question.id).all()
        pg = paginate_questions(request, list_question)
        total_questions = len(list_question)

        return jsonify(
            {
                "success": True,
            }
        )

    """
    @TODO:
    Create a POST endpoint to get questions based on a search term.
    It should return any questions for whom the search term
    is a substring of the question.

    TEST: Search by any phrase. The questions list will update to include
    only question that include that string within their question.
    Try using the word "title" to start.
    """

    @app.post("/search")
    def search_term():
        body = request.get_json()
        search = body.get("searchTerm")
        questions = Question.query.filter(
            Question.question.ilike("%" + search + "%")
        ).all()

        if questions:
            total_queations = len(questions)
            pg = paginate_questions(request, questions)
            return jsonify(
                {
                    "success": True,
                    "questions": pg,
                    "total_questions": total_queations,
                    "current_category": None,
                }
            )
        else:
            abort(404)

    """
    @TODO:
    Create a GET endpoint to get questions based on category.

    TEST: In the "List" tab / main screen, clicking on one of the
    categories in the left column will cause only questions of that
    category to be shown.
    """

    @app.get("/categories/<int:id>/questions")
    def get_category(id):
        get_cate = Category.query.filter_by(id=id).first()
        if get_cate:
            questionsInCat = Question.query.filter_by(category=get_cate.id).all()
            total_queations = len(questionsInCat)
            pg = paginate_questions(request, questionsInCat)
            return jsonify(
                {
                    "success": True,
                    "questions": pg,
                    "total_questions": total_queations,
                    "current_category": get_cate.type,
                }
            )
        else:
            abort(404)

    """
    @TODO:
    Create a POST endpoint to get questions to play the quiz.
    This endpoint should take category and previous question parameters
    and return a random questions within the given category,
    if provided, and that is not one of the previous questions.

    TEST: In the "Play" tab, after a user selects "All" or a category,
    one question at a time is displayed, the user is allowed to answer
    and shown whether they were correct or not.
    """

    @app.post("/quizzes")
    def quiz():
        body = request.get_json()
        quizCategory = body.get("quiz_category")
        previousQuestion = body.get("previous_question")
        quiz_by_category = (
            Question.query.all()
            if quizCategory.get("id") == 0
            else Question.query.filter_by(category=quizCategory.get("id")).all()
        )

        random_index = random.randint(0, len(quizCategory) - 1)
        question = None
        if quiz_by_category:
            question = quiz_by_category[random_index]
        return {"question": question.format()}

    """
    @TODO:
    Create error handlers for all expected errors
    including 404 and 422.
    """

    @app.errorhandler(404)
    def not_for_found(error):
        return (
            jsonify(
                {"success": False, "error": 404, "message": "Page or Data Not Found"}
            ),
            404,
        )

    @app.errorhandler(422)
    def unprocessable(error):
        return (
            jsonify({"success": False, "error": 422, "message": "unprocessable"}),
            422,
        )

    return app
