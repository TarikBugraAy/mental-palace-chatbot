import tensorflow_datasets as tfds
import pandas as pd

# Load GoEmotions dataset
dataset = tfds.load("goemotions")

# Convert dataset to Pandas DataFrame
def dataset_to_df(tf_dataset):
    df = tfds.as_dataframe(tf_dataset)
    return df

# Convert splits to DataFrames
train_df = dataset_to_df(dataset["train"])
valid_df = dataset_to_df(dataset["validation"])
test_df = dataset_to_df(dataset["test"])

# Show dataset structure
print(train_df.head())

from transformers import AutoTokenizer
import torch
from sklearn.preprocessing import MultiLabelBinarizer

# Load DistilBERT tokenizer
tokenizer = AutoTokenizer.from_pretrained("distilbert-base-uncased")

# Convert labels to multi-label one-hot encoding
LABELS = [
    "admiration", "amusement", "anger", "annoyance", "approval", "caring", "confusion",
    "curiosity", "desire", "disappointment", "disapproval", "disgust", "embarrassment",
    "excitement", "fear", "gratitude", "grief", "joy", "love", "nervousness", "optimism",
    "pride", "realization", "relief", "remorse", "sadness", "surprise", "neutral"
]

mlb = MultiLabelBinarizer(classes=LABELS)

# Tokenize dataset
def preprocess_data(df):
    encodings = tokenizer(df["comment_text"].tolist(), padding=True, truncation=True, max_length=128, return_tensors="pt")
    labels = mlb.fit_transform(df["labels"])
    return encodings, torch.tensor(labels, dtype=torch.float32)

train_encodings, train_labels = preprocess_data(train_df)
valid_encodings, valid_labels = preprocess_data(valid_df)
test_encodings, test_labels = preprocess_data(test_df)

# Verify tensor shapes
print(train_encodings["input_ids"].shape, train_labels.shape)

from transformers import AutoModelForSequenceClassification

# Load BERT with correct output labels
model = AutoModelForSequenceClassification.from_pretrained(
    "distilbert-base-uncased", num_labels=len(LABELS)
)

from transformers import TrainingArguments, Trainer

# Training arguments
training_args = TrainingArguments(
    output_dir="./bert_model",
    evaluation_strategy="epoch",
    save_strategy="epoch",
    logging_dir="./logs",
    per_device_train_batch_size=16,
    per_device_eval_batch_size=16,
    num_train_epochs=3,
    learning_rate=2e-5,
    weight_decay=0.01,
)

# Define Trainer
trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=train_encodings,
    eval_dataset=valid_encodings,
)

# Train the model
trainer.train()

# Evaluate on test dataset
results = trainer.evaluate(eval_dataset=test_encodings)
print("Test Results:", results)

model.save_pretrained("bert_emotion_model")
tokenizer.save_pretrained("bert_emotion_model")
