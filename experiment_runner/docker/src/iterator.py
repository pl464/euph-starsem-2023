import os
import logging
from train import run_trainer
from manifest import manifest

logging.basicConfig(format='[%(name)s] [%(levelname)s] %(asctime)s %(message)s')

corpus_dir = os.getenv('CORPUS_DIR')
model_dir = os.getenv('MODEL_DIR')

os.environ['MODEL_NAME'] = 'roberta-base'

for item in manifest:
    # define train and test directories
    traindir = os.path.join(corpus_dir, item['trainfile'])
    testdir = os.path.join(corpus_dir, item['testfile'])
    model_output_dir = os.path.join(model_dir, item['model_name'])
    # make model output dir
    os.system(f'mkdir -p {model_output_dir}')
    
    # make sure train and test files exist
    if not all(os.path.exists(i) for i in [traindir, testdir, model_output_dir]):
        logging.critical('missing dataset file(s) for model', item['model_name'])
    else:
        # define logger
        # Create and configure logger
        logger = logging.getLogger(item['model_name'])
        logger.setLevel(logging.INFO)
        
        # run trainer
        model = run_trainer(traindir, 
                            testdir, 
                            model_output_dir, 
                            logger)
        
        del model
    