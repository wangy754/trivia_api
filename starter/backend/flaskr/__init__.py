import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10

def paginate_questions(request, selection):
  page = request.args.get('page', 1, type=int)
  start =  (page - 1) * QUESTIONS_PER_PAGE
  end = start + QUESTIONS_PER_PAGE

  questions = [question.format() for question in selection]
  current_questions = questions[start:end]

  return current_questions


def create_app(test_config=None):
  # create and configure the app
  app = Flask(__name__)
  setup_db(app)

 
  """
  Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
  """
  CORS(app, resources={"/": {"origins": "*"}})
  """
  Use the after_request decorator to set Access-Control-Allow
  """

  @app.after_request
  def after_request(response):
      """
      Sets access control.
      """
      response.headers.add(
          "Access-Control-Allow-Headers", "Content-Type,Authorization,true"
      )
      response.headers.add(
          "Access-Control-Allow-Methods", "GET,PUT,POST,DELETE,OPTIONS"
      )
      return response

  """
  Create an endpoint to handle GET requests 
  for all available categories.
  """

  @app.route("/categories")
  def get_categories():
      """
      Handles GET requests for getting all categories.
      """
      categories = Category.query.all()
      categories_dict = {}
      for category in categories:
        categories_dict[category.id] = category.type

      if len(categories_dict) == 0:
        abort(404)

      return jsonify({"success": True, "categories": categories_dict})

  """
  Create an endpoint to handle GET requests for questions, 
  including pagination (every 10 questions). 
  This endpoint should return a list of questions, 
  number of total questions, current category, categories. 

  TEST: At this point, when you start the application
  you should see questions and categories generated,
  ten questions per page and pagination at the bottom of the screen for three pages.
  Clicking on the page numbers should update the questions. 
  """
  @app.route('/questions', methods=['GET'])
  def get_questions():
    questions = Question.query.all()
    paginated_questions = paginate_questions(request, questions)

    if len(paginated_questions) == 0:
        abort(404)
    
    categories = Category.query.all()
    cat_dict = {}

    for category in categories:
        cat_dict[category.id] = category.type

    return jsonify({
        'success': True,
        'total_questions': len(questions),
        'categories': cat_dict,
        'questions': paginated_questions
    })

  """
  Create an endpoint to DELETE question using a question ID. 

  TEST: When you click the trash icon next to a question, the question will be removed.
  This removal will persist in the database and when you refresh the page. 
  """

  @app.route('/questions/<int:question_id>', methods=['DELETE'])
  def delete_question(question_id):
    try:
      question = Question.query.filter(Question.id == question_id).one_or_none()

      if question is None:
        abort(404)

      question.delete()
      selection = Question.query.order_by(Question.id).all()
      current_questions = paginate_questions(request, selection)

      return jsonify({
        'success': True,
        'deleted': question_id,
        'questions': current_questions,
        'total_questions': len(Question.query.all())
      })

    except:
      abort(422)

  """
  Create an endpoint to POST a new question, 
  which will require the question and answer text, 
  category, and difficulty score.

  TEST: When you submit a question on the "Add" tab, 
  the form will clear and the question will appear at the end of the last page
  of the questions list in the "List" tab.  
  """
  @app.route('/questions', methods=['POST'])
  def add_question():
    body = request.get_json()
    new_question = body.get('question', None)
    new_answer = body.get('answer', None)
    new_difficulty = body.get('difficulty', None)
    new_category = body.get('category', None)
    if new_question is None or new_answer is None or new_difficulty is None or new_category is None:
      abort(422)  
    try:
      question = Question(question=new_question, answer=new_answer, difficulty=new_difficulty, category=new_category)
      question.insert()

      selection = Question.query.order_by(Question.id).all()
      current_questions = paginate_questions(request, selection)

      return jsonify({
        'success': True,
        'created': question.id,
        'questions': current_questions,
        'total_questions': len(Question.query.all())
      })
    except:
      abort(422)

    
  """
  Create a POST endpoint to get questions based on a search term. 
  It should return any questions for whom the search term 
  is a substring of the question. 

  TEST: Search by any phrase. The questions list will update to include 
  only question that include that string within their question. 
  Try using the word "title" to start. 
  """
  @app.route('/questions/search', methods=['POST'])
  def search_question():
    try:
      body = request.get_json()
      search = body.get('searchTerm', None)
      if not search:
        abort(422)  
      questions = Question.query.filter(Question.question.ilike('%' + search + '%')).all()
      
      return jsonify({
        'success': True,
        'questions': [question.format() for question in questions],
        'total_questions': len(questions),
        'current_category': None
      })
    except:
      abort(422)


  """
  Create a GET endpoint to get questions based on category. 

  TEST: In the "List" tab / main screen, clicking on one of the 
  categories in the left column will cause only questions of that 
  category to be shown. 
  """
  @app.route('/categories/<int:category_id>/questions', methods=['GET'])
  def get_question_by_category(category_id):
    category = Category.query.filter(Category.id == category_id).one_or_none()
    if category is None:
      abort(404)
    try:   
      questions = Question.query.filter(Question.category == str(category_id)).all()
      return jsonify({
        'success': True,
        'questions': [question.format() for question in questions],
        'total_questions': len(questions),
        'current_category': category_id
      })
    except:
      abort(404)  

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

  @app.route('/quizzes', methods=['POST'])
  def get_quiz_question():
    previous_questions = request.get_json()['previous_questions']
    quiz_category = request.get_json()['quiz_category']['id']
    questions = None

    if quiz_category == 0:
      questions = Question.query.all()
    else:  
      questions = Question.query.filter(Question.category == str(quiz_category)).all()

    current_question = ''
    count = len(questions)
    if len(previous_questions) < count:
      used = True
      while used:
        random_q = questions[random.randrange(count)]
        if random_q.id not in previous_questions:
          current_question = random_q.format()
          used = False    

    return jsonify({
      'success':True,
      'question':current_question,
    })

    

  """
  Create error handlers for all expected errors 
  including 404 and 422. 
  """
  @app.errorhandler(400)
  def bad_request(e):
    return jsonify({
        "success": False,
        "error": 400,
        "message": "bad request"
    }), 400

  @app.errorhandler(404)
  def resource_not_found(e):
    return jsonify({
        "success": False,
        "error": 404,
        "message": "resource not found"
    }), 404

  @app.errorhandler(422)
  def unprocessable(e):
    return jsonify({
        "success": False,
        "error": 422,
        "message": "unprocessable"
    }), 422

  return app
