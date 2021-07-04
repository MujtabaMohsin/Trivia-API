import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random
import sys
sys.path.insert(0,'..')
from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)

    # Now, enable CORS
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
        start = (page - 1) * QUESTIONS_PER_PAGE
        end = start + QUESTIONS_PER_PAGE
        questions = Question.query.all()
        return questions[start:end]

    def reformat_data(items):
        formatted_items = [item.format() for item in items]
        return formatted_items

    @app.route('/questions')
    def get_questions():
        questions = paginate_questions(request)
        if len(questions) == 0:
            abort(404)

        # format questions
        formatted_questions = reformat_data(questions)

        # get categories
        categories1 = Category.query.all()
        formatted_categories = {}
        for category in categories1:
            formatted_categories[category.id] = category.type

        total_questions = len(Question.query.all())

        current_categories = list(set([question['category']
                                       for question in formatted_questions]))

        return jsonify({
            'success': True,
            'questions': formatted_questions,
            'total_questions': total_questions,
            'categories': formatted_categories,
            'current_category': current_categories
        })



    @app.route('/questions/<int:question_id>', methods=['DELETE'])
    def delete_question(question_id):
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

            # if search term found
            search_term = body.get('searchTerm', None)
            if search_term:

                # get all questions for search term
                questions = Question.query.filter(
                    Question.question.ilike('%'+search_term+'%')).all()

                formatted_questions = reformat_data(questions)

                return jsonify({
                    'success': True,
                    'questions': formatted_questions
                })

            # if some data not exist
            if body.get('answer') is None or body.get('question') is None or\
                    body.get('category') is None or body.get('difficulty') is None:
                abort(400)

            # Post a new question
            # if all data exist
            new_question = Question(
                question=body.get('question'),
                answer=body.get('answer'),
                category=body.get('category'),
                difficulty=int(body.get('difficulty'))
            )

            new_question.insert()
            return jsonify({
                'success': True
            })
        except:
            abort(400)



    @app.route('/categories/<int:category_id>/questions')
    def get_category_questions(category_id):
        category = Category.query.filter_by(id=category_id).one_or_none()
        if not category:
            abort(404)

        # get all questions by a category
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


        all_categories = ['Science','Art','Geography','History','Entertainment','Sports']

        if category in all_categories:
            # get category and all its questions
            categorydb = Category.query.filter_by(
                type=category).one_or_none()
            if not categorydb:
                abort(404)
            questions = Question.query.filter_by(category=categorydb.id)

        else:
            questions = Question.query.all()
        remaining_questions = []
        for question in questions:
            found = False
            for prev in previous_questions:
                if prev == question.id:
                    found = True
                    break
            if not found:
                remaining_questions.append(question)
        random_number = random.randint(0, len(remaining_questions) - 1)
        return jsonify({
            'success': True,
            'question': remaining_questions[random_number].format()
        })




    '''error handlers'''

    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            'success': False,
            'error': 404,
            'message': "Not Found"
        }), 404


    @app.errorhandler(405)
    def not_found(error):
        return jsonify({
            'success': False,
            'error': 405,
            'message': "Not Found"
        }), 405

    @app.errorhandler(422)
    def un_processable_entitiy(error):
        return jsonify({
            'success': False,
            'error': 422,
            'message': "un procesable entitiy"
        }), 422

    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({
            'success': False,
            'error': 400,
            'message': "bad request"
        }), 400

    @app.errorhandler(500)
    def internal_error(error):
        return jsonify({
            'success': False,
            'error': 500,
            'message': "Internal Server error"
        }), 500


    app.run()
    return app


create_app()
