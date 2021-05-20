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
        self.database_name = "trivia_test"
        self.database_path = "postgres://{}/{}".format(
            "localhost:5432", self.database_name
        )
        setup_db(self.app, self.database_path)
        self.new_question = {
            'question': 'In which city is The Louvre art museum located?',
            'category': 2, 
            'difficulty': 1, 
            'answer': 'paris',
        }

        self.new_question_wrong = {
            'category': 2, 
            'difficulty': 1, 
            'answer': 'paris',
        }

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
    def test_get_questions(self):
        res = self.client().get('/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(len(data['questions']))

    def test_get_paginated_questions(self):
        res = self.client().get('/questions?page=1')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['total_questions'])
        self.assertEqual(len(data['questions']), 10)
   
    def test_get_questions_beyong_valid_pages(self):
        res = self.client().get('/questions?page=101')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'resource not found')
    
    def test_get_categories(self):
        res = self.client().get('/categories')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(len(data['categories']), 6)      
    
    def test_delete_question(self):
        #there should be a question with the id
        res = self.client().delete('/questions/28')
        data = json.loads(res.data)

        question = Question.query.filter(Question.id == 28).one_or_none()

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['deleted'], 28)
        self.assertTrue(data['total_questions'])
        self.assertTrue(len(data['questions']))
        self.assertEqual(question, None)
    
    def test_delete_question_fails(self):
        # fail if the id doesn't exit
        res = self.client().delete('/questions/103')
        data = json.loads(res.data)

        self.assertEqual(data['message'], 'unprocessable')
        self.assertEqual(res.status_code, 422)

    def test_create_new_questions(self):
        res = self.client().post('/questions', json=self.new_question)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['created'])
        self.assertTrue(len(data['questions']))

    def test_create_new_questions_fails(self):
        res = self.client().post('/questions', json=self.new_question_wrong)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)
        self.assertEqual(data['success'], False)
 

    def test_get_question_by_category(self):
        res = self.client().get('/categories/1/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(len(data['questions']), 3)

    def test_get_question_by_category_fails(self):
        # fail with a wrong category
        res = self.client().get('/categories/11/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'resource not found')

    def test_search_question_with_results(self):
        res = self.client().post('/questions/search', json={'searchTerm': 'penicillin'})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['total_questions'])
        self.assertEqual(len(data['questions']), 1)
    
    def test_search_question_without_results(self):
        res = self.client().post('/questions/search', json={'searchTerm': 'applebee'})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['total_questions'], 0)
        self.assertEqual(len(data['questions']), 0)

    def test_get_quiz_question(self):
        res = self.client().post('/quizzes', json={"previous_questions": [17, 18], "quiz_category": {'type': 'History', 'id': 2}})
        data = json.loads(res.data)
        #print(data['question'])
        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['question'])

    def test_get_quiz_question_fails(self):
        res = self.client().post('/quizzes', json={"previous_questions": [17, 18], "quiz_category": {'type': 'Art', 'id': 12}})
        data = json.loads(res.data)
        #print(data['question'])
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['question'], '')

# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()