import random


def get_random_filter():
    # Define available audiogram styles
    return random.choice(["style1", "style2", "style3"])  # Replace with actual styles


def get_random_text():
    texts = ["Sample Text 1", "Sample Text 2", "Sample Text 3"]
    return random.choice(texts)


def get_random_dynamic_text():
    dynamic_texts = ["Dynamic Text 1", "Dynamic Text 2", "Dynamic Text 3"]
    return random.choice(dynamic_texts)
