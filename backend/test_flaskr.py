import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Question, Category


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        database_name = "trivia"
        database_path = "postgres://{}:{}@{}/{}".format('student', 'student', 'localhost:5432', database_name)
        setup_db(self.app, database_path)

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()

    def tearDown(self):
        """Executed after reach test"""
        pass

    """
    TODO
    Write at least one test for each test for successful operation and for expected errors.
    """

    def test_get_categories(self):
        res = self.client().get('/categories')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)


    def test_get_questions(self):
        res = self.client().get('/questions')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)


    def test_create_question(self):
        question = {
            'question': 'How are you?',
            'answer': 'fine',
            'difficulty': 1,
            'category': 1,
        }

        res = self.client().post('/questions', json=question)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)


    def test_search_question(self):
        res = self.client().post('/questions', json={'searchTerm': "Who"})
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['questions'])


    def test_delete_question(self):
        # create a question
        question = Question(question='how are you?', answer='good',
                            difficulty=1, category=1)
        question.insert()
        id = question.id

        res = self.client().delete(f'/questions/{id}')

        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)

    def test_422_invalid_delete_question(self):
        res = self.client().delete("/questions/777")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)
        self.assertEqual(data['message'], 'unprocessable')
        self.assertEqual(data['error'], 422)





    def test_404_invalid_page(self):
        res = self.client().get('/questions?page=9599')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 404)
        # self.assertEqual(data['error'], '404')
        self.assertEqual(data['message'], 'resource not found')
        self.assertEqual(data['success'], False)



    def test_get_quiz_questions(self):

        res = self.client().post('/quizzes', json={'quiz_category': "Sports", 'previous_questions': []})
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)

    def test_get_category_questions(self):
        res = self.client().get('/categories/1/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(len(data['questions']))



    def test_404_get_category_questions(self):
        res = self.client().get('/categories/3414/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data["success"], False)



# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()
