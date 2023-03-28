# install dependencies
python3 -m pip install --upgrade pip
python3 -m pip install \
    torch \
    torchvision \
    torchaudio \
    --extra-index-url https://download.pytorch.org/whl/cu116

python3 -m pip install --no-cache-dir -r requirements.txt

export MODEL_DIR=models
export CORPUS_DIR=corpora

mkdir -p $MODEL_DIR
mkdir -p $CORPUS_DIR

python3 src/iterator.py
