import nltk
import re

# Ensure you have the necessary NLTK data
nltk.download('punkt')

# Function to tokenize sentences from a Unicode text file
def tokenize_sentences(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        text = file.read()

    # Tokenize sentences using NLTK
    sentences = nltk.tokenize.sent_tokenize(text)

    return sentences

# Function to group sentences by block size
def group_sentences_by_block(sentences, block_size):
    blocks = []
    current_block = []
    current_block_size = 0

    for sentence in sentences:
        sentence_size = len(sentence)
        if current_block_size + sentence_size <= block_size:
            current_block.append(sentence)
            current_block_size += sentence_size
        else:
            blocks.append(current_block)
            current_block = [sentence]
            current_block_size = sentence_size

    if current_block:
        blocks.append(current_block)

    return blocks

# Main function
def main():
    input_file = 'input.txt'
    block_size = 500

    # Tokenize sentences
    sentences = tokenize_sentences(input_file)

    # Group sentences by block size
    blocks = group_sentences_by_block(sentences, block_size)

    # Print each sentence
    print("Sentences:")
    for sentence in sentences:
        print(sentence)

    # Print each block
    print("\nBlocks:")
    for i, block in enumerate(blocks):
        print(f"Block {i+1}:")
        for sentence in block:
            print(sentence)
        print()

if __name__ == "__main__":
    main()