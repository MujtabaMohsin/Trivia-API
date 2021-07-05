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
    cors = CORS(app, resources={r"/*": {"origins": "*"}})

    # CORS headers
    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,true')
        response.headers.add('Access-Control-Allow-Methods', 'GET,POST,DELETE')
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
        start = QUESTIONS_PER_PAGE * (page - 1)
        end = start + QUESTIONS_PER_PAGE
        questions = Question.query.all()
        return questions[start:end]



    def reformat_data(items):
        formatted_items = []
        for item in items:
            formatted_items.append(item.format())

        return formatted_items



    @app.route('/questions')
    def get_all_questions():
        # get all questions as paginated
        all_questions = paginate_questions(request)

        #if no questions available
        if len(all_questions) == 0:
            abort(404)

        # reformat the questions to be suit for json
        formatted_questions = reformat_data(all_questions)

        #get all categories from database
        all_categories = Category.query.all()


        # reformat the categores
        categories = {}
        for category in all_categories:
            categories[category.id] = category.type

        #get the total number of questions
        total_num_questions = len(Question.query.all())

        #get the categories for the quesions of this page
        current_categories = set()
        for question in formatted_questions:
            current_categories.add(question['category'])

        current_categories_list = list(current_categories);

        return jsonify({
            'success': True,
            'total_questions': total_num_questions,
            'categories': categories,
            'categories this page': current_categories_list,
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

            #get all available parameters from the body
            searchTerm = body.get('searchTerm', None)
            answer = body.get('answer')
            question = body.get('question')
            difficulty = body.get('difficulty')
            category = body.get('category')

            '''FOR SEARCHING SOME QUESTIONS'''

            # if the operation is for search and the key found
            if searchTerm:
                # get all questions for search term
                questions = Question.query.filter(Question.question.ilike('%' + searchTerm + '%')).all()

                # reformat the questions
                searched_questions = reformat_data(questions)
                return jsonify({
                    'success': True,
                    'questions': searched_questions
                })

            '''FOR CREATING A NEW QUESTION'''

            # if some data doesn't exist return 400
            if answer is None or question is None or difficulty is None or category is None:
                abort(400)


            # if all data exist
            newQuestion = Question(
                question = Question,
                answer = answer,
                difficulty = difficulty,
                category = category
            )

            # insert to the database
            newQuestion.insert()
            return jsonify({
                'success': True
            })
        except:
            abort(400)

    @app.route('/categories/<int:category_id>/questions')
    def category_questions(category_id):

        #get the requested category
        category = Category.query.get(category_id)

        # return 404 if there is no category with this ID
        if not category:
            abort(404)

        # Now get all questions by the category
        questions = Question.query.order_by(Question.id).filter(Question.category == category_id ).all()

        #reformat data
        formatted_questions = reformat_data(questions)

        return jsonify({
            'success': True,
            'questions': formatted_questions
        })

    @app.route('/quizzes', methods=['POST'])
    def get_quiz_question():
        body = request.get_json()

        # get the data from the body
        category = body.get('quiz_category', None)
        previous_questions = body.get('previous_questions')

        all_categories = ['Science', 'Art', 'Geography', 'History', 'Entertainment', 'Sports']

        # check if the selected category is in the list
        if category in all_categories:
            # get the category object
            selected_category = Category.query.filter_by(type=category).one_or_none()

            if not selected_category:
                abort(404)
            # Now get all questions of this category
            questions = Question.query.filter_by(category=selected_category.id)

        else:
            # if no category selected then get all questions
            questions = Question.query.all()

        # array to add all remaining questions;
        remaining_questions = []

        for question in questions:
            found = False
            for previous in previous_questions:
                # if the current question is the previous questions
                if previous == question.id:
                    found = True
                    break
            if not found:
                #if the current question is in the previous question entered by the user then don't append it.
                remaining_questions.append(question)

        # get a random number from 0 to the number remaining questions
        random_num = random.randint(0, len(remaining_questions)-1)

        new_question = remaining_questions[random_num].format()

        return jsonify({
            'question': new_question,
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
