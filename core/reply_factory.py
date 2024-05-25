
from .constants import BOT_WELCOME_MESSAGE, PYTHON_QUESTION_LIST


def generate_bot_responses(message, session):
    bot_responses = []

    current_question_id = session.get("current_question_id")
    if not current_question_id:
        bot_responses.append(BOT_WELCOME_MESSAGE)

    success, error = record_current_answer(message, current_question_id, session)

    if not success:
        return [error]

    next_question, next_question_id = get_next_question(current_question_id)

    if next_question:
        bot_responses.append(next_question)
    else:
        final_response = generate_final_response(session)
        bot_responses.append(final_response)

    session["current_question_id"] = next_question_id
    session.save()

    return bot_responses


def record_current_answer(answer, current_question_id, session):
    '''
    Validates and stores the answer for the current question to the Django session.
    '''

    # Get the current question from the question list
    current_question = PYTHON_QUESTION_LIST.get(current_question_id)

    if current_question:
        # Validate the answer based on the question type
        if current_question['type'] == 'text':
            # For text type questions, simply store the answer
            session['user_answers'][current_question_id] = answer
        elif current_question['type'] == 'choice':
            # For choice type questions, validate the answer against the choices
            choices = current_question['choices']
            if answer in choices:
                session['user_answers'][current_question_id] = answer
            else:
                return False, "Invalid choice. Please select one of the provided options."
        else:
            # Handle other question types if needed
            pass
        return True, ""  # Successfully stored the answer
    else:
        return False, "Current question not found in the question list."



def get_next_question(current_question_id):
    '''
    Fetches the next question from the PYTHON_QUESTION_LIST based on the current_question_id.
    '''
    next_question_id = current_question_id + 1

    # Check if there is a next question available
    if next_question_id < len(PYTHON_QUESTION_LIST):
        next_question = PYTHON_QUESTION_LIST[next_question_id]
        return next_question, next_question_id
    else:
        # No more questions available
        return None, None



def generate_final_response(session):
    '''
    Creates a final result message including a score based on the answers
    by the user for questions in the PYTHON_QUESTION_LIST.
    '''
    user_answers = session.get('user_answers', {})
    total_questions = len(PYTHON_QUESTION_LIST)
    correct_answers = 0

    # Calculate the number of correct answers
    for question_id, answer in user_answers.items():
        correct_answer = PYTHON_QUESTION_LIST[question_id]['correct_answer']
        if answer == correct_answer:
            correct_answers += 1

    # Calculate the score percentage
    score_percentage = (correct_answers / total_questions) * 100

    # Generate the final response message based on the score
    if score_percentage >= 70:
        final_response = f"Congratulations! You scored {score_percentage}% in the quiz. Well done!"
    elif score_percentage >= 50:
        final_response = f"You scored {score_percentage}% in the quiz. You can do better next time."
    else:
        final_response = f"You scored {score_percentage}% in the quiz. Keep practicing!"

    return final_response

