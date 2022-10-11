from crypt import methods
import os
import sys
# from tracemalloc import start
from flask import Flask, flash, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
# from flask_cors import CORS
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
    # cors = CORS(app, resources={r"/api/v1.0/*": {"origins":"*"}})
    
    
    # Setting up ACCESS-CONTROL-ALLOW HEADERS
    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Headers',
                             'Content-Type, Authorization, true')
        response.headers.add('Access-Control-Allow-Methods',
                             'GET, POST, PATCH, DELETE, OPTIONS')
        
        # return response
        return response
    
    
     # Route to handle GET requests for all available categories, GET by default
    @app.route('/')
    def initial():
        
        # return category response object to frontend
        return jsonify({
            'success': True,
            'message': "this is working"
        })

    
    # Route to handle GET requests for all available categories, GET by default
    @app.route('/categories', methods=['GET'])
    def get_categories():
        
        # retrieve all categories 
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

  


    # DELETES A QUESTION USING QUESTION ID
    @app.route('/questions/<question_id>', methods=['DELETE'])
    def delete_question_by_id(question_id):
        try:
            # get answer by id, suing one_or_none()
            question = Question.query.filter_by(id=id).one_or_none()

            # if question not found abort operation
            if question is None:
                abort(404)

            # delete 
            question.delete()

            # return success message to frontend
            return jsonify({
                'success': True,
                'deleted': id
            })
            
            
        except:
            
            #  if there's a problem deleting the question abort operation
            abort(422)
    
    """
    
    TEST: When you click the trash icon next to a question, the question will be removed.
    This removal will persist in the database and when you refresh the page.
    """

    @app.route('/question', methods=['POST'])
    def create_new_question():
        
        # get the request body
        body = request.get_json()
        
        # check if the needed arguments are presents
        if not ('question' in body and 'answer' in body and 'difficulty' in body and 'category' in body):
            abort(422)
            
        # collect the arguments from the body
        get_question = body.get('question')
        get_answer = body.get('answer')
        get_difficulty = body.get('difficulty')
        get_category = body.get('category')
        
        # validate fields
        if ((get_question is None) or (get_answer is None) or
                (get_difficulty is None) or (get_category is None)):
            flash("Make sure all fields are filled")
            abort(422)
            
        try: 
            # Create a new question
            new_question = Question(question=get_question, answer=get_answer,
                                difficulty=get_difficulty,
                                category=get_category)
            # insert the record
            new_question.insert()

            # get all questions and paginate
            get_selection = Question.query.order_by(Question.id).all()
            current_questions = do_paginate_questions(request, get_selection)

            # return a response object
            return jsonify({
                'success': True,
                'created': new_question.id,
                'question_created': new_question.question,
                'questions': current_questions,
                'total_questions': len(Question.query.all())
            })
        except:
               abort(422)
    
    """
    TEST: When you submit a question on the "Add" tab,
    the form will clear and the question will appear at the end of the last page
    of the questions list in the "List" tab.
    """


    # Search Questions
    @app.route('/questions/search', methods=['POST'])
    def search_for_questions():
        
        # Retrieve user input
        request_body = request.get_json()
        
        #Retrieve search string
        request_search_term = request_body.get('searchTerm', None)

        # Using a search term provided to search and filter out the results
        try:
            if request_search_term:
                get_selection = Question.query.filter(Question.question.ilike
                                                  (f'%{request_search_term}%')).all()

            # Retrieve paginated results
            get_paginated_results = do_paginate_questions(request, get_selection)

            return jsonify({
                'success': True,
                'questions':  get_paginated_results,
                'total_questions': len(get_selection),
                'current_category': None
            })
        except:
            abort(404)
    
    
    
    """
    TEST: Search by any phrase. The questions list will update to include
    only question that include that string within their question.
    Try using the word "title" to start.
    """
    
    
    # GET QUESTIONS BASED ON CATEGORIES
    
    @app.route('/categories/<int:id>/questions')
    def get_questions_by_categories(id):
        
        # Get category by id, try get questions from matching category
        get_category = Category.query.filter_by(id=id).one_or_none()

        try:
            # Retrieve questions matching the category
            get_selection = Question.query.filter_by(category=get_category.id).all()

            # Return paginated results
            get_paginated = do_paginate_questions(request, get_selection)

            return jsonify({
                'success': True,
                'questions': get_paginated,
                'total_questions': len(Question.query.all()),
                'current_category': get_category.type
            })
        except:
            abort(400)

    """
    TEST: In the "List" tab / main screen, clicking on one of the
    categories in the left column will cause only questions of that
    category to be shown.
    """

    # Quiz route based on Category, return a randomized value
    @app.route('/quiz', methods=['POST'])
    def get_quiz():
        try:
            
            # get an instance of request body
            request_body = request.get_json()

            # get category and proevious questions from request body
            get_quiz_category = request_body.get('quiz_category')
            get_previous_question = request_body.get('previous_questions')

            # Filter available Questions when 'ALL' categories is 'clicked', 
            if get_quiz_category['id'] == 0:
                available_questions = Question.query.all()
                
            # Filter available questions by chosen category & unused questions
            else:
                available_questions = Question.query.filter_by(
                    category=get_quiz_category['id']).filter(
                        Question.id.notin_((get_previous_question))).all()

            # randomly get the next question from available the questions
            get_new_question = available_questions[random.randrange(
                0, len(available_questions)-1)].format() if len(
                    available_questions) > 0 else None

            return jsonify({
                'success': True,
                'question': {
                     "answer": get_new_question.answer,
                        "category": get_new_question.category,
                        "difficulty": get_new_question.difficulty,
                        "id": get_new_question.id,
                        "question": get_new_question.question
                },
                  'previousQuestion': get_previous_question
            })
        except Exception as e:
            print(e)
            abort(422)
            
    """
    TEST: In the "Play" tab, after a user selects "All" or a category,
    one question at a time is displayed, the user is allowed to answer
    and shown whether they were correct or not.
    """

    # Handle errors
    @app.errorhandler(400)
    def bad_request_error(error):
        return jsonify({
            "success": False,
            "error": 400,
            "message": "bad request"
        }), 400

    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            "success": False,
            "error": 404,
            "message": "resource not found"
        }), 404

    @app.errorhandler(422)
    def unprocessable(error):
        return jsonify({
            "success": False,
            "error": 422,
            "message": "unprocessable"
        }), 422

    @app.errorhandler(500)
    def internal_server_error(error):
        return jsonify({
            "success": False,
            "error": 500,
            "message": "internal server error"
        }), 422

    return app

