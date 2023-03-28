from datasets import load_dataset
from transformers import (AutoTokenizer,
                          AutoModelForSequenceClassification,
                          TrainingArguments, 
                          Trainer)

import numpy as np
import evaluate
import logging
import os
from typing import Union

def run_trainer(trainfile: str, 
                testfile: str, 
                output_dir: str, 
                logger: Union[logging.Logger, None], 
                seed: int = 41) -> AutoModelForSequenceClassification:
    """Runs trainer

    Args:
        trainfile (str): Train file (.csv)
        testfile (str): Test file (.csv)
        output_dir (str): Output directory
        logger Union[logging.Logger, None], optional: Logger to use

    Returns:
        AutoModelForSequenceClassification: Trained model
    """
    
    log = logging.getLogger(__name__) if logger is None else logger
    
    # sanity checks
    for i in [trainfile, testfile, output_dir]:
        assert os.path.exists(i), f"File/Directory {i} does not exist"
    
    log.info('loading dataset...')
    dataset = load_dataset("csv", data_files={"train": trainfile, 
                                              "test": testfile})

    # define tokenizer and tokenize datasets
    log.info('loading tokenizer...')
    tokenizer = AutoTokenizer.from_pretrained(os.getenv('MODEL_NAME'), max_length=512)

    def tokenize_function(examples):
        return tokenizer(examples["text"], padding="max_length", truncation=True)

    log.info('tokenizing datasets...')
    tokenized_datasets = dataset.map(tokenize_function, batched=True)

    # load model
    log.info('loading model...')
    model = AutoModelForSequenceClassification.from_pretrained(os.getenv('MODEL_NAME'))

    # define training args
    training_args = TrainingArguments(output_dir=output_dir, 
                                      evaluation_strategy="epoch", 
                                      num_train_epochs=10, 
                                      learning_rate=1e-5, 
                                      per_device_train_batch_size=16,
                                      logging_strategy = 'epoch',
                                      logging_first_step = True,
                                      save_strategy = 'epoch',
                                      load_best_model_at_end = True,
                                      metric_for_best_model = 'f1')

    # define evaluation metrics
    metric_f1 = evaluate.load("f1")
    metric_pr = evaluate.load("precision")
    metric_re= evaluate.load("recall")
    # metric_2 = evaluate.load("accuracy")

    def compute_metrics(eval_pred):
        logits, labels = eval_pred
        predictions = np.argmax(logits, axis=-1)
        
        f1 = metric_f1.compute(predictions=predictions, 
                               references=labels, 
                               average='macro')
        
        recall = metric_re.compute(predictions=predictions, 
                                   references=labels)
        
        precision = metric_pr.compute(predictions=predictions, 
                                      references=labels)
        
        return {'f1': f1, 
                'precision': precision, 
                'recall': recall}

    # define test and train splits
    train_dataset = tokenized_datasets["train"].shuffle(seed=seed).select(range(len(tokenized_datasets["train"])))
    test_dataset = tokenized_datasets["test"].shuffle(seed=seed).select(range(len(tokenized_datasets["test"])))

    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=train_dataset,
        eval_dataset=test_dataset,
        compute_metrics=compute_metrics
    )

    trainer.train()

    # save model
    trainer.save_model(output_dir)
    
    return model
