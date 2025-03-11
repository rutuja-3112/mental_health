import json
import pickle
import random
import numpy as np
from nltk.stem import WordNetLemmatizer
from keras.models import Sequential
from keras.layers import Dense, Dropout
from keras.optimizers import SGD
import nltk
# Initialize lemmatizer and random seed
lemmatizer = WordNetLemmatizer()
nltk.download('punkt')
nltk.download('wordnet')
# Load intents JSON
with open("intents.json", "r") as file:
    intents = json.load(file)

# Prepare data
words = []
classes = []
documents = []
ignore_words = ["?", "!", ".", ","]
for intent in intents["intents"]:
    for pattern in intent["patterns"]:
        # Tokenize each word
        word_list = nltk.word_tokenize(pattern)
        words.extend(word_list)
        documents.append((word_list, intent["tag"]))

    # Add the tag to the classes if not already present
    if intent["tag"] not in classes:
        classes.append(intent["tag"])

# Lemmatize and lower each word, remove duplicates
words = sorted(set([lemmatizer.lemmatize(w.lower()) for w in words if w not in ignore_words]))
classes = sorted(set(classes))

# Save words and classes for future use
pickle.dump(words, open("texts.pkl", "wb"))
pickle.dump(classes, open("labels.pkl", "wb"))
# Create training data
training = []
output_empty = [0] * len(classes)

for doc in documents:
    # Initialize bag of words
    bag = [1 if w in [lemmatizer.lemmatize(word.lower()) for word in doc[0]] else 0 for w in words]
    
    # Output is 1 for the corresponding class
    output_row = list(output_empty)
    output_row[classes.index(doc[1])] = 1

    training.append([bag, output_row])

# Shuffle and convert to numpy arrays
random.shuffle(training)
train_x = np.array([item[0] for item in training], dtype=np.float32)
train_y = np.array([item[1] for item in training], dtype=np.float32)

# Build the model
model = Sequential()
model.add(Dense(128, input_shape=(len(train_x[0]),), activation="relu"))
model.add(Dropout(0.5))
model.add(Dense(64, activation="relu"))
model.add(Dropout(0.5))
model.add(Dense(len(classes), activation="softmax"))

# Compile the model
sgd = SGD(learning_rate=0.01, momentum=0.9, nesterov=True)
model.compile(loss="categorical_crossentropy", optimizer=sgd, metrics=["accuracy"])

# Train the model
model.fit(train_x, train_y, epochs=500, batch_size=8, verbose=1)

# Save the trained model
model.save("model.h5")
print("Model trained and saved!")