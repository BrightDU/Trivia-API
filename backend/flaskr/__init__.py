import os
import sys
from tracemalloc import start
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category

# define db
db = SQLAlchemy()

QUESTIONS_PER_PAGE = 10

# pagination handler
def do_paginate_questions(request, all_questions):
    page = request.args.get('page', 1, type=int) # get the page default index
    start_paginate_index = (page - 1) * QUESTIONS_PER_PAGE
    end_paginate_index =  start_paginate_index + QUESTIONS_PER_PAGE
    questions = [question.format() for question in all_questions]
    
    # retrieve the current set of questions
    current_questions = questions[start_paginate_index:end_paginate_index]
    
    return current_questions

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)
 
    # Setting up CORS for * origins
    cors = CORS(app, resources={r"/api/v1.0/*": {"origins":"*"}})
    
    
    # Setting up ACCESS-CONTROL-ALLOW HEADERS
    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Headers',
                             'Content-Type, Authorization, true')
        response.headers.add('Access-Control-Allow-Methods',
                             'GET, POST, PATCH, DELETE, OPTIONS')
        
        #return response
        return response
    
    
    # Route to handle GET requests for all available categories
    @app.route('/categories')
    def get_categories():
        
        # retrieve all categories and add to dict
        categories = Category.query.all()
        
        available_categories = {}
        
        # format the categories data
        for category in categories:
            available_categories[category.id] = category.type

        # If no categories, abort the request
        if (len(available_categories) == 0):
            abort(404)

        # return category response object to frontend
        return jsonify({
            'success': True,
            'categories': available_categories
        })


    # Retrieve(GET) the questions using the pagination value 
    @app.route('/questions')
    def get_questions():
        # Retrieve questions and paginate
        all_questions = Question.query.all()
        
        # get the count of questions
        total_questions = len(all_questions)
        
        # get current questions
        get_current_questions = do_paginate_questions(request, all_questions)

        # If no questions, abort the request
        if (len(get_current_questions) == 0):
            abort(404)


        # Handle possible errors
        try:
            # get categories
            categories = Category.query.all()
            
            categories_collection = {}
            
            # format the categories data
            for category in categories:
                categories_collection[category.id] = category.type

            # return reponse object to frontend
            return jsonify({
                'success': True,
                'questions': get_current_questions,
                'total_questions': total_questions,
                'categories': categories_collection
            })
        except:
            db.session.rollback()
            print(sys.exc_info())
            abort(422)
        finally:
            db.session.close() # close the db
    
    
    """
    TEST: At this point, when you start the application
    you should see questions and categories generated,
    ten questions per page and pagination at the bottom of the screen for three pages.
    Clicking on the page numbers should update the questions.
    """

    """
    @TODO:
    Create an endpoint to DELETE question using a question ID.

    TEST: When you click the trash icon next to a question, the question will be removed.
    This removal will persist in the database and when you refresh the page.
    """

    """
    @TODO:
    Create an endpoint to POST a new question,
    which will require the question and answer text,
    category, and difficulty score.

    TEST: When you submit a question on the "Add" tab,
    the form will clear and the question will appear at the end of the last page
    of the questions list in the "List" tab.
    """

    """
    @TODO:
    Create a POST endpoint to get questions based on a search term.
    It should return any questions for whom the search term
    is a substring of the question.

    TEST: Search by any phrase. The questions list will update to include
    only question that include that string within their question.
    Try using the word "title" to start.
    """

    """
    @TODO:
    Create a GET endpoint to get questions based on category.

    TEST: In the "List" tab / main screen, clicking on one of the
    categories in the left column will cause only questions of that
    category to be shown.
    """

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

    """
    @TODO:
    Create error handlers for all expected errors
    including 404 and 422.
    """

    return app

