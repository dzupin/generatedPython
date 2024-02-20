import nltk
from nltk.tokenize import sent_tokenize

# Ensure you have downloaded the Punkt Tokenizer Models using nltk.download('punkt')

def read_unicode_file(filename):
    with open(filename, 'r', encoding='utf-8') as file:
        return file.read()

def group_sentences(sentences, max_length=500):
    blocks = []
    block = ''
    for sentence in sentences:
        if len(block) + len(sentence) > max_length:
            blocks.append(block)
            block = ''
        else:
            if block:
                block += ' '
            block += sentence
    if block:
        blocks.append(block)
    return blocks

# Read Unicode text file
text = read_unicode_file('input.txt')

# Tokenize into sentences
sentences = sent_tokenize(text)
print("Sentences:")
for sentence in sentences:
    print(sentence)

#Group sentences into blocks
blocks = group_sentences(sentences)
print("\nBlocks:")
for i, block in enumerate(blocks):
    print(f"Block {i+1}: {block}")