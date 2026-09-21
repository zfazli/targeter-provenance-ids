from gensim.models import Word2Vec
import numpy as np
import torch
import random
import re

def clean_path(path: str) -> str:
    # حذف اولین بخش که فقط عدد است
    cleaned_path = re.sub(r'/\d+/', '/', path)  # برای حالت `/proc/320/something`
    cleaned_path = re.sub(r'/\d+', '', cleaned_path)  # برای حالت `/etc/apt/apt.conf.d/01autoremove`
    return cleaned_path

def tokenize(sentence: str):
    # جدا کردن رشته به لیست
    sentence = clean_path(sentence)
    parts = sentence.split()
    trimmed_text = " ".join(parts[:10])
    return (trimmed_text.replace(':',' : ').replace('.',' . ').replace('/',' / ')).split()

def get_sentences(data):
    corpus = []
    for line in data:
        tokens = tokenize( line)
        corpus.append(tokens)
    return corpus





# 2️⃣ آموزش مدل Word2Vec
def train(sentences, embedding_size=128, window=5, min_count=1, epochs=100):
    Seed = 42  # هر عددی باشد مهم نیست، فقط ثابت بماند.
    random.seed(Seed)
    np.random.seed(Seed)
    torch.manual_seed(Seed)
    torch.cuda.manual_seed_all(Seed)  # برای GPU اگر استفاده می‌کنی
    torch.backends.cudnn.deterministic = True
    torch.backends.cudnn.benchmark = False
    model = Word2Vec(sentences, vector_size=embedding_size, window=window, min_count=min_count, workers=4, sg=1, seed= Seed)
    model.train(sentences, total_examples=len(sentences), epochs=epochs)
    return model


def train_word2vec(courpus , dataset , embedding_size):
    print(embedding_size)
    print('new')
    sentences = get_sentences(courpus)
    model = train(sentences, embedding_size=embedding_size)
    model.save(f'./models/{dataset}/word2vec-embedding_{embedding_size}.model')