from flask import url_for, session, request
from twilio.twiml.messaging_response import MessagingResponse

from glogic import app, db
from glogic.models import BaselineAnswers, BaselineQuestions, User
from .gresponses import Dictionary

# view for collecting organisation details
from .send_airtime import send_airtime_after_survey

@app.route('/baseline', methods=["GET", "POST"])
def baseline():
    session['View'] = 'baseline'
    response = MessagingResponse()

    num = request.form.get('From')
    num = num.replace('whatsapp:', '')

    if 'question_id' in session:
        return answers(session['question_id'], response, num)
    # else:
    #     first_question = redirect_to_first_question(response)
    #     response.message(first_question.content)

    else:
        # response.message("Please type _only the number_ of your answer.")
        if "yes" not in request.form.get('Body').lower():
            response.message(Dictionary["welcome3"])

        else:
            response.message("Please wait a few seconds between responses. If there is no reply, wait 30 seconds and try agan. If the problem persists, please notify us at digital@genesis-analytics.com")
            first_question = redirect_to_first_question(response)
            response.message(first_question.content)

    return str(response)








def answers(question_id, response, num):
    question = BaselineQuestions.query.get(question_id)

    incoming_msg = request.form.get('Body').lower()
    next_question = question.next()

    # skip logic (hopefully)
    if question_id == 3 or question_id == 5:
        if '3' not in incoming_msg:
            next_question = next_question.next()

    if question_id == 15 and len(incoming_msg) >1 and '5' in incoming_msg:
        response.message("Your answer is invalid. If you have answered *5*, you cannot select any other options. Please reply again with your answer.")
        return str(response)

    if question_id == 14:
        if len(incoming_msg) > 1:
            incoming_msg = "6 - " + incoming_msg
        else:
            response.message("Please respond with your elaboration.")
            return str(response)

    else:
        for i in incoming_msg:
            if i == " " or i == ',':
                continue
            else:
                try:
                    int(i)
                except ValueError:
                    response.message("Please respond with the number of your response. Separate multiple options with a space or a comma only.")
                    return str(response)
                else:
                    if int(i) > question.num_ops:
                        response.message("Your answer is invalid. Please respond with one of the given options.")
                        return str(response)



    db.save(BaselineAnswers(content=incoming_msg,
                            question=question,
                            user=User.query.filter(User.number == num).first()))

    if next_question:
        response.message(questions(next_question.id))

    else:
        # user = User.query.filter(User.number == num).first()
        # user.registered = 1
        # db.session.commit()
        #TODO ^^
        airtime = send_airtime_after_survey(num)
        # airtime = 0

        response.message("You are now registered for our monthly surveys and we kindly ask you to complete the 3 "
                         "question survey every month to receive R17. If you answer the monthly surveys for 4 months "
                         "in a row you will earn an additional R20. You will be notified when a new survey is "
                         "available.")

        response.message("If you want to stop receiving the surveys, please send *STOP*.")
        del (session['question_id'])
        # del session['view']
        session['view'] = 'survey'
    return str(response)


def questions(question_id):
    question = BaselineQuestions.query.get(question_id)
    session['question_id'] = question.id
    return question.content


# goes to question view and finds first question
def redirect_to_first_question(response):
    session['question_id'] = 1
    return BaselineQuestions.query.first()
