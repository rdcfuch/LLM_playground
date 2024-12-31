from unsloth import FastLanguageModel
import torch
from datasets import load_dataset
import os
import json
import re
import random
from sklearn.model_selection import train_test_split

# Configuration
max_seq_length = 2048
load_in_4bit = True  # Efficient memory usage
dtype = None

# Directory to store checkpoints
checkpoint_dir = "./outputs_Meta-Llama-3.1-8B-bnb-4bit"

def is_model_processed(model_name):
    checkpoint_path = os.path.join(checkpoint_dir, model_name.split("/")[-1], "checkpoint-500", "trainer_state.json")
    print(f"Checking checkpoint path: {checkpoint_path}")
    return os.path.exists(checkpoint_path)

def mark_model_as_processed(model_name):
    checkpoint_file = os.path.join(checkpoint_dir, f"{model_name.replace('/', '_')}.done")
    print(f"Marking model as processed: {checkpoint_file}")
    with open(checkpoint_file, 'w') as f:
        f.write("")
