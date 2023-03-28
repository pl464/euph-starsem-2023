# VET_Experiment

## Setup
Make sure that you have Docker installed before proceeding if you're running locally on a Mac. Docker should already be installed on Linux.

## To Run
Simply run the following command:
```sh
make run
```

To change which models to train on what datasets, edit `src/manifest.py`. It should look like this:

```python3
manifest = [{'model_name': 'finetuned_model_1', 
             'trainfile': 'train_1.csv', 
             'testfile': 'test_1.csv'}, 
            {'model_name': 'finetuned_model_2',
             'trainfile': 'train_2.csv', 
             'testfile': 'test_2.csv'}]
```

To set which model to fine-tune, edit `MODEL_NAME` environment variable set in `iterator.py`.

All train and test files must be in .CSV format and put in the `corpora` folder. All model outputs will be in `models` after the trainer is finished.