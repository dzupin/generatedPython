import nltk
import re

# Load the Unicode data from the file
with open('input.txt', 'r', encoding='utf-8') as f:
    data = f.read()

# Tokenize the data into sentences
sentences = nltk.tokenize.sent_tokenize(data)

# Initialize an empty list to store the blocks
blocks = []

# Initialize a variable to store the current block
current_block = ''

# Iterate over the sentences
for sentence in sentences:
    # Add the sentence to the current block
    current_block += sentence

    # If the current block is 500 characters or less, add it to the list of blocks
    if len(current_block) <= 500:
        blocks.append(current_block)
        current_block = ''
    else:
        # If the current block is more than 500 characters, split it into two blocks
        while len(current_block) > 500:
            split_point = current_block[:500].rfind(' ')
            if split_point == -1:
                split_point = 500
            blocks.append(current_block[:split_point])
            current_block = current_block[split_point:]

# Print the sentences
print('Sentences:')
for sentence in sentences:
    print("*** sentence ***")
    print(sentence)

# Print the blocks
print('\nBlocks:')
for block in blocks:
    print("*** block ***")
    print(block)