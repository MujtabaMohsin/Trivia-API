import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random
import sys

sys.path.insert(0, '..')
from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)

    # Now, enable the CORS
    CORS(app, resources={r"/api/*": {"origins": "*"}})

    '''
  @TODO: Use the after_request decorator to set Access-Control-Allow
  '''

    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Headers',
                             'Content-Type, Authorization')
        response.headers.add('Access-Control-Allow-Methods',
                             'GET, POST, PATCH, DELETE, OPTIONS')
        return response

    @app.route('/categories')
    def categories():
        categories = Category.query.all()
        # create dict
        formatted_categories = {}
        for category in categories:
            formatted_categories[category.id] = category.type
        return jsonify({
            'success': True,
            'categories': formatted_categories
        })

    def paginate_questions(request):
        page = request.args.get('page', 1, type=int)
        start = QUESTIONS_PER_PAGE*(page - 1)
        end = start + QUESTIONS_PER_PAGE
        questions = Question.query.all()
        return questions[start:end]

    def reformat_data(items):
        formatted_items = [item.format() for item in items]
        return formatted_items

    @app.route('/questions')
    def get_all_questions():
        all_questions = paginate_questions(request)
        if len(all_questions) == 0:
            abort(404)
        formatted_questions = reformat_data(all_questions)
        all_categories = Category.query.all()

        # create dict for all categories
        formatted_categories = {}
        for category in all_categories:
            formatted_categories[category.id] = category.type

        total_num_questions = len(Question.query.all())
        current_categories = set()
        for question in formatted_questions:
            current_categories.add(question['category'])

        current_categories_list = list(current_categories);

        return jsonify({
            'success': True,
            'total_questions': total_num_questions,
            'categories': formatted_categories,
            'current_category': current_categories_list,
            'questions': formatted_questions,

        })

    @app.route('/questions/<int:question_id>', methods=['DELETE'])
    def delete_question(question_id):
        #get the question you want to delete
        question = Question.query.filter_by(id=question_id).one_or_none()
        if not question:
            abort(404)

        question.delete()

        return jsonify({
            'success': True
        })

    @app.route('/questions', methods=['POST'])
    def create_question():
        try:
            body = request.get_json()

            #get the search term from the body

            searchTerm = body.get('searchTerm', None)

            # if the key found
            if searchTerm:
                #get all questions for search term
                questions = Question.query.filter(Question.question.ilike('%' + searchTerm + '%')).all()
                searched_questions = reformat_data(questions)
                return jsonify({
                    'success': True,
                    'questions': searched_questions
                })


            # if some data doesn't exist return 400
            if body.get('answer') is None or body.get('question') is None or \
                    body.get('difficulty') is None or body.get('category') is None:
                abort(400)

            # Post a new question
            # if all data exist
            newQuestion = Question(
                question = body.get('question'),
                answer = body.get('answer'),
                difficulty = int(body.get('difficulty')),
                category = body.get('category')
            )

            newQuestion.insert()
            return jsonify({
                'success': True
            })
        except:
            abort(400)

    @app.route('/categories/<int:category_id>/questions')
    def category_questions(category_id):

        #get the requested category
        category = Category.query.filter_by(id=category_id).one_or_none()

        # return 404 if there is no category
        if not category:
            abort(404)

        # Now get all questions by the category
        questions = Question.query.filter_by(category=category_id)
        formatted_questions = reformat_data(questions)

        return jsonify({
            'success': True,
            'questions': formatted_questions
        })

    @app.route('/quizzes', methods=['POST'])
    def get_quiz_question():
        body = request.get_json()
        category = body.get('quiz_category', None)

        previous_questions = body.get('previous_questions')

        all_categories = ['Science', 'Art', 'Geography', 'History', 'Entertainment', 'Sports']

        if category in all_categories:
            selected_category = Category.query.filter_by( type=category ).one_or_none()

            if not selected_category:
                abort(404)
            questions = Question.query.filter_by(category=selected_category.id)

        else:
            # if no category selected then get all questions
            questions = Question.query.all()

        # array to add all remaining questions;
        remaining_questions = []
        for question in questions:
            found = False
            for previous in previous_questions:
                #if the current question is the previous questions
                if previous == question.id:
                    found = True
                    break
            if not found:
                remaining_questions.append(question)
        random_num = random.randint(0, len(remaining_questions)-1)

        return jsonify({
            'question': remaining_questions[random_num].format(),
            'success': True
        })

    '''error handlers'''

    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            'success': False,
            'error': 404,
            'message': "Not Found"
        })

    @app.errorhandler(405)
    def not_found(error):
        return jsonify({
            'success': False,
            'error': 405,
            'message': "Not Found"
        })


    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({
            'success': False,
            'error': 400,
            'message': "bad request"
        })

    @app.errorhandler(500)
    def internal_error(error):
        return jsonify({
            'success': False,
            'error': 500,
            'message': "Internal Server error"
        })



    @app.errorhandler(422)
    def un_processable_entitiy(error):
        return jsonify({
            'success': False,
            'error': 422,
            'message': "Not Found"
        })

    app.run()
    return app


create_app()
