'''
#Some References {
  https://github.com/Louis95/Trivia-Api
}
'''
import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category

from utils import get_paginated_questions

QUESTIONS_PER_PAGE = 10

def create_app(test_config=None):
  # create and configure the app
  app = Flask(__name__)
  setup_db(app)
  
  '''
  @TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
  '''
  CORS(app, resources={'/': {'origins': '*'}})

  '''
  @TODO: Use the after_request decorator to set Access-Control-Allow
  '''
  @app.after_request
  def after_request(response):
    ''' Set Access Control '''
    response.headers.add(
      'Access-Control-Allow-Headers',
      'Content-Type, Authorization, true')
    response.headers.add(
      'Access-Control-Allow-Methods',
      'GET, POST, PATCH, DELETE, OPTIONS')
    return response

  '''
  @TODO: 
  Create an endpoint to handle GET requests 
  for all available categories.
  '''
  @app.route('/categories')
  def get_all_categories():
    try:
      categories = Category.query.all()
      categories_dict = {}
      for category in categories:
        categories_dict[category.id] = category.type
      return jsonify({
        'success': True,
        'categories': categories_dict
      }), 200
    except Exception:
      abort(500)

  '''
  @TODO: 
  Create an endpoint to handle GET requests for questions, 
  including pagination (every 10 questions). 
  This endpoint should return a list of questions, 
  number of total questions, current category, categories. 

  TEST: At this point, when you start the application
  you should see questions and categories generated,
  ten questions per page and pagination at the bottom of the screen for three pages.
  Clicking on the page numbers should update the questions. 
  '''
  @app.route('/questions')
  def get_questions():
    questions = Question.query.order_by(Question.id).all()
    total_questions = len(questions)
    categories = Category.query.order_by(Category.id).all()

    current_questions = get_paginated_questions(request, questions,QUESTIONS_PER_PAGE)

    if (len(current_questions) == 0):
      abort(404)

    categories_dict = {}
    for category in categories:
      categories_dict[category.id] = category.type

    return jsonify({
      'success': True,
      'total_questions': total_questions,
      'categories': categories_dict,
      'questions': current_questions
    }), 200

  '''
  @TODO: 
  Create an endpoint to DELETE question using a question ID. 

  TEST: When you click the trash icon next to a question, the question will be removed.
  This removal will persist in the database and when you refresh the page. 
  '''
  @app.route('/questions/<int:id>', methods=['DELETE'])
  def delete_question(id):
    try:
      question = Question.query.get(id)
      question.delete()

      return jsonify({
        'success': True,
        'message': "Question successfully deleted"
      }), 200
    except Exception:
      abort(422)

  '''
  @TODO: 
  Create an endpoint to POST a new question, 
  which will require the question and answer text, 
  category, and difficulty score.

  TEST: When you submit a question on the "Add" tab, 
  the form will clear and the question will appear at the end of the last page
  of the questions list in the "List" tab.  
  '''
  @app.route('/questions', methods=['POST'])
  def create_question():
    data = request.get_json()
    question = data.get('question', '')
    answer = data.get('answer', '')
    difficulty = data.get('difficulty', '')
    category = data.get('category', '')

    if ((question == '') or (answer == '') or (difficulty == '') or (category == '')):
      abort(422)

    try:
      question = Question(question=question,answer=answer,difficulty=difficulty,category=category)
      question.insert()
      return jsonify({
        'success': True,
        'message': 'Question successfully created!'
      }), 201
    except Exception:
      abort(422)

  '''
  @TODO: 
  Create a POST endpoint to get questions based on a search term. 
  It should return any questions for whom the search term 
  is a substring of the question. 

  TEST: Search by any phrase. The questions list will update to include 
  only question that include that string within their question. 
  Try using the word "title" to start. 
  '''
  @app.route('/questions/search', methods=['POST'])
  def search_questions():
    data = request.get_json()
    search_term = data.get('searchTerm', '')

    if search_term == '':
      abort(422)

    try:
      questions = Question.query.filter(Question.question.ilike(f'%{search_term}%')).all()
      if len(questions) == 0:
        abort(404)
      paginated_questions = get_paginated_questions(request, questions,QUESTIONS_PER_PAGE)

      return jsonify({
        'success': True,
        'questions': paginated_questions,
        'total_questions': len(Question.query.all())
      }), 200
    except Exception:
      abort(404)

  '''
  @TODO: 
  Create a GET endpoint to get questions based on category. 

  TEST: In the "List" tab / main screen, clicking on one of the 
  categories in the left column will cause only questions of that 
  category to be shown. 
  '''
  @app.route('/categories/<int:id>/questions')
  def get_questions_by_category(id):
    category = Category.query.filter_by(id=id).one_or_none()
    if (category is None):
      abort(422)

    questions = Question.query.filter_by(category=id).all()

    paginated_questions = get_paginated_questions(request, questions,QUESTIONS_PER_PAGE)

    return jsonify({
      'success': True,
      'questions': paginated_questions,
      'total_questions': len(questions),
      'current_category': category.type
    })
  '''
  @TODO: 
  Create a POST endpoint to get questions to play the quiz. 
  This endpoint should take category and previous question parameters 
  and return a random questions within the given category, 
  if provided, and that is not one of the previous questions. 

  TEST: In the "Play" tab, after a user selects "All" or a category,
  one question at a time is displayed, the user is allowed to answer
  and shown whether they were correct or not. 
  '''
  @app.route('/quizzes', methods=['POST'])
  def play_quiz_question():
    data = request.get_json()
    previous_questions = data.get('previous_questions')
    quiz_category = data.get('quiz_category')

    if ((quiz_category is None) or (previous_questions is None)):
      abort(400)

    if (quiz_category['id'] == 0):
      questions = Question.query.all()
    else:
      questions = Question.query.filter_by(
      category=quiz_category['id']).all()

    def get_random_question():
      return questions[random.randint(0, len(questions)-1)]
    next_question = get_random_question()
    found = True

    while found:
      if next_question.id in previous_questions:
        next_question = get_random_question()
      else:
        found = False
    return jsonify({
      'success': True,
      'question': next_question.format(),
    }), 200

  '''
  @TODO: 
  Create error handlers for all expected errors 
  including 404 and 422. 
  '''
  # Error(404)
  @app.errorhandler(404)
  def not_found(error):
    return jsonify({
      'success': False,
      'error': 404,
      'message': 'Resource not found'
    }), 404

  # Error(422)
  @app.errorhandler(422)
  def unprocesable_entity(error):
    return jsonify({
      'success': False,
      'error': 422,
      'message': 'Unprocessable entity'
    }), 422

  # Error(400)
  @app.errorhandler(400)
  def bad_request(error):
    return jsonify({
      'success': False,
      'error': 400,
      'message': 'Bad request error'
    }), 400

  # Error(500)
  @app.errorhandler(500)
  def internal_server_error(error):
    return jsonify({
      'success': False,
      'error': 500,
      'message': 'An error has occured, please try again'
    }), 500

  return app