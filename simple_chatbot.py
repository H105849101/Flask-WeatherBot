from chatterbot import ChatBot
from chatterbot.trainers import ListTrainer
from chatterbot.trainers import ChatterBotCorpusTrainer
import requests

my_bot = ChatBot(name="PyBot")

my_bot = ChatBot(
name="PyBot",
 read_only=True,
 logic_adapters=["chatterbot.logic.MathematicalEvaluation",
 "chatterbot.logic.BestMatch"]
)

small_talk = [
    "Hello",
    "Hi there!",
    "How are you doing?",
    "I'm doing great.",
    "That is good to hear",
    "Thank you.",
    "You're welcome."
]

math_talk_1 = [
    'pythagorean theorem',
    'a squared plus b squared equals c squared.'
]


list_trainer = ListTrainer(my_bot)


corpus_trainer = ChatterBotCorpusTrainer(my_bot)
corpus_trainer.train('chatterbot.corpus.english')

print("Type 'exit' to quit.")
while True:
    user_input = input("You: ")

    if user_input.lower() == "exit":
        print("Goodbye!")
        break





