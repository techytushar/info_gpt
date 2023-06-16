from info_gpt.chat import ask, load_model

result = ask("What are the basic features of peak platform", load_model())

print(result)
