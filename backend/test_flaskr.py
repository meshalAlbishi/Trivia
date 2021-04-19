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
        database_password = 'mM300319'
        self.database_path = 'postgresql://postgres:{}@localhost:5432/{}'.format(database_password, database_name)

        setup_db(self.app, self.database_path)

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()

        q = {
            "category": 1,
            "difficulty": 1,
            "answer": "Java",
            "question": "What is the best programming lang.?"
        }

        self.question = q

    def tearDown(self):
        """Executed after reach test"""
        pass

    """
    TODO
    Write at least one test for each test for successful operation and for expected errors.
    """

    # test for fetch_categories
    def test_fetch_categories_success(self):
        result = self.client().get('/categories')

        self.assertEqual(result.status_code, 200)

        self.assertEqual(json.loads(result.data)['success'], True)
        self.assertTrue(json.loads(result.data)['categories'])

    def test_fetch_categories_error(self):
        result = self.client().get('/all-category')
        self.assertEqual(result.status_code, 404)
        self.assertEqual(json.loads(result.data)['success'], False)

    # test for fetch_questions
    def test_fetch_questions_success(self):
        result = self.client().get('/questions')

        self.assertEqual(result.status_code, 200)

        self.assertEqual(json.loads(result.data)['success'], True)

        self.assertTrue(json.loads(result.data)['questions'])
        self.assertTrue(json.loads(result.data)['total_questions'])

    def test_fetch_questions_error(self):
        result = self.client().get('/questions?page=500000')

        self.assertEqual(result.status_code, 404)
        self.assertEqual(json.loads(result.data)['success'], False)

    # test for delete_question
    def test_delete_question_success(self):
        question = Question.query.first()

        result = self.client().delete('/questions/' + str(question.id))

        self.assertEqual(result.status_code, 200)

        self.assertEqual(json.loads(result.data)['success'], True)

    def test_delete_question_error(self):
        result = self.client().delete('/questions/100251687')

        self.assertEqual(result.status_code, 500)

        self.assertEqual(json.loads(result.data)['success'], False)

    # test for create_question
    def test_create_question_success(self):
        result = self.client().post('/questions', json={
            'id': 500000,
            'question': 'who will finish this Nanodegree?',
            'answer': 'meshal',
            'difficulty': 1,
            'category': '1'})

        self.assertEqual(result.status_code, 200)

        self.assertEqual(json.loads(result.data)['success'], True)

    def test_create_question_error(self):
        result = self.client().post(
            '/questions', json={"questio": "who will finish this Nanodegree?"})

        self.assertEqual(result.status_code, 500)

        self.assertEqual(json.loads(result.data)['success'], False)

    # test for get_category
    def test_get_category_success(self):
        result = self.client().get('/categories/2/questions')

        self.assertEqual(result.status_code, 200)

        self.assertEqual(json.loads(result.data)['success'], True)
        self.assertTrue(json.loads(result.data)['questions'])

    def test_get_category_error(self):
        result = self.client().get('/categories/500/questions')

        self.assertEqual(result.status_code, 404)

        self.assertEqual(json.loads(result.data)['success'], False)

    # test for search
    def test_search_success(self):
        result = self.client().post('/questions', json={'searchTerm': Question.query.first().question})

        self.assertEqual(result.status_code, 200)

        self.assertEqual(json.loads(result.data)['success'], True)
        self.assertTrue(json.loads(result.data)['questions'])

    def test_search_error(self):
        result = self.client().post('/questions/')

        self.assertEqual(result.status_code, 404)
        self.assertEqual(json.loads(result.data)['success'], False)

    # test for quizzes
    def test_quizzes_success(self):
        result = self.client().post('/quizzes', json={
            'previous_questions': [],
            'quiz_category':
                {
                    'id': 1,
                    'type': 'art'
                }
        })

        self.assertEqual(result.status_code, 200)

        self.assertEqual(json.loads(result.data)['success'], True)
        self.assertTrue(json.loads(result.data)['question'])

    def test_quizzes_error(self):
        result = self.client().post('/quizzes', json={
            'previous_questions': [Question.query.first().id],
            'quiz_category': {'id': 9999}
        })

        self.assertEqual(result.status_code, 500)
        self.assertEqual(json.loads(result.data)['success'], False)


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()
