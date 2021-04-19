import os
from distutils.command.config import config
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random
from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)
    '''
  @DONE: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
  '''
    CORS(app)

    '''
  @DONE: Use the after_request decorator to set Access-Control-Allow
  '''

    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
        response.headers.add('Access-Control-Allow-Methods', 'GET,PATCH,POST,DELETE,OPTIONS')
        return response

    '''
  @DONE: 
  Create an endpoint to handle GET requests 
  for all available categories.
  '''

    @app.route("/categories", methods=['GET'])
    def fetch_categories():
        try:
            all_categories = Category.query.all()
            categories = categories_to_dict(all_categories)

            return jsonify({
                'success': True,
                'categories': categories
            })
        except:
            abort(404)

    '''
  @DONE: 
  Create an endpoint to handle GET requests for questions, 
  including pagination (every 10 questions). 
  This endpoint should return a list of questions, 
  number of total questions, current category, categories. 
  '''
    '''
    TEST: At this point, when you start the application **********************************************
  you should see questions and categories generated,
  ten questions per page and pagination at the bottom of the screen for three pages.
  Clicking on the page numbers should update the questions. 
  '''

    @app.route('/questions', methods=['GET'])
    def fetch_questions():
        try:
            all_categories = Category.query.all()
            categories = categories_to_dict(all_categories)

            questions = Question.query.all()
            format_questions = paginate_questions(request, questions)

            if len(format_questions) == 0:
                abort(404)

            return jsonify({
                "success": True,
                "questions": format_questions,
                "total_questions": len(questions),
                "categories": categories,
                "current_category": None
            })

        except:
            abort(404)

    def paginate_questions(request, questions):
        page = request.args.get("page", 1, type=int)

        start = (page - 1) * QUESTIONS_PER_PAGE
        end = start + QUESTIONS_PER_PAGE

        formatted = [question.format() for question in questions]
        current_questions = formatted[start:end]

        return current_questions

    '''
  @DONE: 
  Create an endpoint to DELETE question using a question ID.      
  '''

    @app.route('/questions/<int:question_id>', methods=['DELETE'])
    def delete_question(question_id):
        question = Question.query.get(question_id)
        question.delete()

        all_categories = Category.query.all()
        categories = categories_to_dict(all_categories)

        questions = Question.query.all()
        format_questions = paginate_questions(request, questions)

        return jsonify({
            "success": True,
            "questions": format_questions,
            "total_questions": len(questions),
            "categories": categories,
            "current_category": None
        })

    '''  
  TEST: When you click the trash icon next to a question **********************************************
  , the question will be removed. 
  This removal will persist in the database and when you refresh the page. 
    '''

    '''
  @DONE: 
  Create an endpoint to POST a new question, 
  which will require the question and answer text, 
  category, and difficulty score.
  '''
    '''
     TEST: When you submit a question on the "Add" tab,  **********************************************
     the form will clear and the question will appear at the end of the last page
     of the questions list in the "List" tab.  
     '''

    @app.route('/questions', methods=['POST'])
    def create_question():
        searchTerm = request.get_json().get('searchTerm')
        if searchTerm is not None:

            search = "%{}%".format(searchTerm.strip())
            all_questions = Question.query.filter(Question.question.ilike(search)).all()
            questions = question_to_list(all_questions)

            return jsonify({
                'success': True,
                'questions': questions,
                'total_questions': len(questions),
                'current_category': None
            })

        else:

            question = request.get_json().get('question')
            answer = request.get_json().get('answer')
            difficulty = request.get_json().get('difficulty')
            category = request.get_json().get('category')

            if question is not None and answer is not None and difficulty is not None and category is not None:
                c = Category.query.get(category)
                question_id = len(Question.query.all()) * random.randint(2, 9)
                q = Question(question_id, question, answer, c.type, difficulty)
                q.insert()

                return jsonify({
                    'success': True
                }), 200

            else:
                abort(500)

    '''
  TEST: Search by any phrase. The questions list will update to include  **********************************************
  only question that include that string within their question. 
  Try using the word "title" to start. 
  '''

    '''
  @DONE: 
  Create a GET endpoint to get questions based on category. 
    '''

    @app.route('/categories/<int:category_id>/questions', methods=['GET'])
    def get_category(category_id):
        category = Category.query.get(category_id)

        if category is None:
            abort(404)

        all_questions = Question.query.filter_by(category=category.type).all()
        questions = question_to_list(all_questions)

        return jsonify({
            "success": True,
            "questions": questions,
            "total_questions": len(questions),
            "current_category": category.id
        })

    '''
  TEST: In the "List" tab / main screen, clicking on one of the  **********************************************
  categories in the left column will cause only questions of that 
  category to be shown. 
  '''

    '''
  @DONE: 
  Create a POST endpoint to get questions to play the quiz. 
  This endpoint should take category and previous question parameters 
  and return a random questions within the given category, 
  if provided, and that is not one of the previous questions. 
    '''

    @app.route('/quizzes', methods=['POST'])
    def play():
        quiz_category = request.get_json()['quiz_category']
        previous_questions = request.get_json().get('previous_questions')

        if quiz_category is None or previous_questions is None:
            return

        all_questions = None
        if quiz_category['id'] == 0:
            print('----------------- all')
            all_questions = Question.query.all()
        else:
            # category_id = int()
            # category = Category.query.get(quiz_category['id'])
            all_questions = Question.query.filter_by(category=quiz_category['type']).all()

        question = get_new_question(all_questions, previous_questions)
        return jsonify({
            'success': True,
            'question': question
        })

    def get_new_question(all_questions, previous_questions):
        for q in all_questions:

            if q.id not in previous_questions:
                return {
                    'id': q.id,
                    'question': q.question,
                    'answer': q.answer,
                    'category': q.category,
                    'difficulty': q.difficulty
                }

        return None

    '''
  TEST: In the "Play" tab, after a user selects "All" or a category, **********************************************
  one question at a time is displayed, the user is allowed to answer
  and shown whether they were correct or not. 
  '''

    '''
  @DONE: 
  Create error handlers for all expected errors 
  including 404 and 422. 
  '''

    @app.errorhandler(404)
    def not_found(e):
        return jsonify({
            "success": False,
            "error": 404,
            "message": "The Page Not Found :("
        }), 404

    @app.errorhandler(422)
    def not_found(e):
        return jsonify({
            "success": False,
            "error": 422,
            "message": "Something Wrong :("
        }), 422

    @app.errorhandler(500)
    def not_found(e):
        return jsonify({
            "success": False,
            "error": 500,
            "message": "Server Error :("
        }), 500

    # helper functions

    def question_to_list(all_questions):
        questions = []

        for q in all_questions:
            questions.append({
                'id': q.id,
                'question': q.question,
                'answer': q.answer,
                'category': q.category,
                'difficulty': q.difficulty
            })

        return questions

    def categories_to_dict(all_categories):
        categories = {}
        for category in all_categories:
            categories[category.id] = category.type

        return categories

    return app
