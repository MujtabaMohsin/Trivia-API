import os
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
    @TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
    DONE
    '''
    CORS(app, resources={'/': {'origins': '*'}})

    '''
    @TODO: Use the after_request decorator to set Access-Control-Allow
    DONE
    '''

    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,true')
        response.headers.add('Access-Control-Allow-Methods', 'GET,POST,DELETE')
        return response

    '''
    @TODO: 
    DONE
    Create an endpoint to handle GET requests 
    for all available categories.
    '''

    @app.route('/categories')
    def categories():
        # get them from database
        categories = Category.query.all()

        if categories is None:
            abort(500);

        # print(categories)

        categories_dict = {}

        for category in categories:
            categories_dict[category.id] = category.type

        return jsonify({
            'success': True,
            'categories': categories_dict
        })

    '''
    DONE
    @TODO: 
    Create an endpoint to handle GET requests for questions, 
 
    '''

    def get_page_questions(request):
        # default page is 1
        page = request.args.get('page', 1, type=int)
        start = QUESTIONS_PER_PAGE * (page - 1)
        end = start + QUESTIONS_PER_PAGE
        questions = Question.query.all()
        # get the quesions for this page
        return questions[start:end]

    @app.route('/questions')
    def get_questions():
        all_questions = Question.query.all()

        questions = get_page_questions(request)

        # print(questions)
        categories = Category.query.all()

        # if no questions or categories available
        if len(questions) == 0 or categories is None:
            abort(404)

        # format the questions
        questions_list = []
        for question in questions:
            questions_list.append(question.format())

        # print(questions_list)

        # get the categories
        categories_list = {}

        for category in categories:
            categories_list[category.id] = category.type

        # get the current categories

        current_categories = set()
        for question in questions_list:
            current_categories.add(question['category'])

        # convert the set to a list
        current_categories_list = list(current_categories);

        return jsonify({
            'success': True,
            'total_questions': len(all_questions),
            'current categories': current_categories_list,
            'categories': categories_list,
            'questions': questions_list

        })

    '''
    DONE
    @TODO:
    Create an endpoint to POST a new question,

    '''

    '''
    DONE
    @TODO: 
    Create a POST endpoint to get questions based on a search term. 

    '''

    @app.route('/questions', methods=['POST'])
    def create_question():
        data = request.get_json()

        # Search
        if data.get('searchTerm'):
            search_term = data.get('searchTerm')

            term_questions = Question.query.filter(Question.question.ilike(f'%{search_term}%')).all()

            # questions = get_page_questions(request, term_questions)

            # format the questions
            questions_list = []
            for question in term_questions:
                questions_list.append(question.format())

            return jsonify({
                'success': True,
                'questions': questions_list
            })

        # add a new question
        else:
            answer = data.get('answer')
            question = data.get('question')
            difficulty = data.get('difficulty')
            category = data.get('category')

            if question is None or answer is None or category is None or difficulty is None:
                abort(404)

            # add the question
            new_question = Question(question=question, answer=answer, difficulty=difficulty, category=category)

            # insert to the database
            new_question.insert()

            return jsonify({
                'success': True,
                'question': new_question.question

            })

    '''
    @TODO: 
    DONE
    Create a GET endpoint to get questions based on category. 

    '''

    @app.route('/categories/<int:c_id>/questions', methods=['GET'])
    def get_categories_questions(c_id):

        category = Category.query.get(c_id)
        if category is None:
            abort(404)
        # get the questions
        questions = Question.query.filter(Question.category == c_id).all()

        # format the questions
        questions_list = []
        for question in questions:
            questions_list.append(question.format())

        return jsonify({
            'success': True,
            'questions': questions_list
        }), 200

    '''
    @TODO: 
    Create an endpoint to DELETE question using a question ID. 
 
    '''

    @app.route('/questions/<int:q_id>', methods=['DELETE'])
    def delete_question(q_id):
        # get the question you want to delete
        question = Question.query.filter_by(id=q_id).first()

        if question is None:
            abort(422)

        question.delete()

        return jsonify({
            'success': True,
            'message': "question is deleted"
        }), 200

    '''
    @TODO: 
    Create a POST endpoint to get questions to play the quiz. 
    DONE
    '''

    @app.route('/quizzes', methods=['POST'])
    def play_quiz():
        data = request.get_json()
        category = data.get('quiz_category')
        previous_questions = data.get('previous_questions')

        all_categories = ['Science', 'Art', 'Geography', 'History', 'Entertainment', 'Sports']

        # check if the selected category is in the list
        if category in all_categories:

            # get the category object
            selected_category = Category.query.filter_by(type=category).one_or_none()

            # Now get all questions of this category
            questions = Question.query.filter_by(category=selected_category.id)
        else:

            # if no category selected then get all questions
            questions = Question.query.all()

        questions_list = []

        for question in questions:
            if question.id not in previous_questions:
                questions_list.append(question)

        # get a random number from 0 to total_questions length
        total_questions = len(questions_list) - 1
        random_num = random.randint(0, total_questions)

        new_question = questions_list[random_num].format()

        return jsonify({
            'question': new_question,
            'success': True
        })

    '''
    @TODO: 
    Create error handlers for all expected errors 
    including 404 and 422. 
    '''

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

    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({
            "success": False,
            "error": 400,
            "message": "bad request"
        }), 400

    @app.errorhandler(405)
    def not_found(error):
        return jsonify({
            "success": False,
            "error": 405,
            "message": "method not allowed"
        }), 405

    return app
