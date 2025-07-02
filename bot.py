import telebot
import random

TOKEN = 'YOUR_TOKEN_HERE'
bot = telebot.TeleBot(TOKEN)


QUIZ = [
    {
        "question": "What is the capital of France?",
        "options": ["Berlin", "Madrid", "Paris", "Rome"],
        "correct": 2
    },
    {
        "question": "Which planet is known as the Red Planet?",
        "options": ["Earth", "Mars", "Jupiter", "Saturn"],
        "correct": 1
    },
    {
        "question": "What is 5 + 7?",
        "options": ["10", "11", "12", "13"],
        "correct": 2
    }
]

user_state = {}
user_history = {}

@bot.message_handler(commands=['start'])
def start(message):
    chat_id = message.chat.id
    send_main_menu(chat_id)

def send_main_menu(chat_id):
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("Quiz", "Statistics")
    bot.send_message(chat_id, "Welcome to Quiz Bot! Choose an option:", reply_markup=markup)

@bot.message_handler(commands=['quiz'])
def quiz_start(message):
    chat_id = message.chat.id
    question_index = random.randint(0, len(QUIZ) - 1)
    user_state[chat_id] = {"score": 0, "asked": set(), "current": question_index}
    send_question(chat_id, question_index)

@bot.message_handler(commands=['score'])
def show_score(message):
    chat_id = message.chat.id
    history = user_history.get(chat_id, [])
    if history:
        text = "Your last quiz results:\n"
        for i, score in enumerate(history[-3:], 1):
            text += f"{i}. {score} out of {len(QUIZ)}\n"
        bot.send_message(chat_id, text)
    else:
        bot.send_message(chat_id, "No quiz history yet. Try /quiz to start!")

@bot.message_handler(func=lambda message: message.text == "Quiz")
def quiz_text_handler(message):
    quiz_start(message)

@bot.message_handler(func=lambda message: message.text == "Statistics")
def score_text_handler(message):
    show_score(message)

def send_question(chat_id, question_index):
    question = QUIZ[question_index]["question"]
    options = QUIZ[question_index]["options"]
    markup = telebot.types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    for i, option in enumerate(options):
        markup.add(f"{i+1}. {option}")
    bot.send_message(chat_id, question, reply_markup=markup)

@bot.message_handler(func=lambda message: message.chat.id in user_state)
def answer_handler(message):
    chat_id = message.chat.id
    state = user_state[chat_id]
    text = message.text

    if not text or not text[0].isdigit():
        bot.send_message(chat_id, "Please reply with the number of your answer.")
        return

    answer_index = int(text[0]) - 1
    current_q = state["current"]

    if answer_index == QUIZ[current_q]["correct"]:
        state["score"] += 1
        bot.send_message(chat_id, "Correct! 🎉")
    else:
        correct_option = QUIZ[current_q]["options"][QUIZ[current_q]["correct"]]
        bot.send_message(chat_id, f"Wrong! The correct answer was: {correct_option}")

    state["asked"].add(current_q)

    if len(state["asked"]) == len(QUIZ):
        score = state['score']
        bot.send_message(chat_id, f"Quiz finished! Your final score: {score} out of {len(QUIZ)}.")
        user_history.setdefault(chat_id, []).append(score)
        del user_state[chat_id]
        send_main_menu(chat_id)
    else:
        remaining = set(range(len(QUIZ))) - state["asked"]
        next_q = random.choice(list(remaining))
        state["current"] = next_q
        send_question(chat_id, next_q)

bot.polling(none_stop=True)