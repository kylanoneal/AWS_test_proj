from sagemaker.huggingface.model import HuggingFaceModel
from sagemaker.serverless import ServerlessInferenceConfig
from sagemaker.huggingface.model import HuggingFacePredictor

# endpoint_dict = {'news': {'bart-large-cnn-25-6-5': "Bart-Large-CNN", 'pegasus-cnn-25-6-5': "Pegasus-Large-CNN", 'flan-t5-base-25-6-5': "Flan-T5-Base"},
#             'scientific': {'bigbird-pegasus-arxiv-25-6-5': "Bigbird-Pegasus-Large-arXiv", 'bart-arxiv-25-6-5': "LSG-Bart-Base-arXiv"},
#             'fiction': {'bart-base-booksum-25-5-6': "Bart-Base-Booksum", 'bigbird-pegasus-booksum-25-6-5': "Bigbird-Pegasus-Large-Booksum",},
#             'xsum': {'bart-xsum-25-6-5': "Bart-Large-XSUM", 'pegasus-xsum-25-6-5': "Pegasus-Large-XSUM"},
#             'tutorial': {'t5-small-wikihow-25-6-5': "T5-Small-Wikihow", 'pegasus-wikihow-25-6-5': "Pegasus-Large-Wikihow"},
#             'dialogue': {'bart-samsum-25-6-5': "Bart-Large-Samsum", 'flan-t5-samsum-25-6-5': 'Flan-T5-Base-Samsum'},
#             'blog': {'pegasus-tifu-25-6-5': "Pegasus-Large-TIFU"}}

endpoint_dict = {'news': {'Bart-Large-CNN': "bart-large-cnn-25-6-5", 'Pegasus-Large-CNN': "pegasus-cnn-25-6-5", 'Flan-T5-Base': "flan-t5-base-25-6-5"},
            'scientific': {'Bigbird-Pegasus-Large-arXiv': "bigbird-pegasus-arxiv-25-6-5", 'LSG-Bart-Base-arXiv': "bart-arxiv-25-6-5"},
            'fiction': {'Bart-Base-Booksum': "bart-base-booksum-25-5-6", 'Bigbird-Pegasus-Large-Booksum': "bigbird-pegasus-booksum-25-6-5"},
            'xsum': {'Bart-Large-XSUM': "bart-xsum-25-6-5", 'Pegasus-Large-XSUM': "pegasus-xsum-25-6-5"},
            'tutorial': {'T5-Small-Wikihow': "t5-small-wikihow-25-6-5", 'Pegasus-Large-Wikihow': "pegasus-wikihow-25-6-5"},
            'dialogue': {'Bart-Large-Samsum': "bart-samsum-25-6-5", 'Flan-T5-Base-Samsum': "flan-t5-samsum-25-6-5"},
            'blog': {'Pegasus-Large-TIFU': "pegasus-tifu-25-6-5"}}

def invoke_endpoint(input_text, model_choice):
    predictor = HuggingFacePredictor(endpoint_name=model_choice)
    prediction = predictor.predict({'inputs': input_text})
    return prediction[0]['summary_text']


def create_endpoint(endpoint_name, model_name, memory_size, max_concurrency):
    # Specify Model Image_uri
    image_uri = '763104351884.dkr.ecr.us-east-1.amazonaws.com/huggingface-pytorch-inference:1.13.1-transformers4.26.0-cpu-py39-ubuntu20.04'

    # Hub Model configuration. <https://huggingface.co/models>
    hub = {
        'HF_MODEL_ID': model_name,
        'HF_TASK': 'summarization'
    }

    # create Hugging Face Model Class
    huggingface_model = HuggingFaceModel(
        env=hub,  # configuration for loading model from Hub
        role="arn:aws:iam::248874456479:role/concisely-IAM-role",
        # iam role with permissions
        transformers_version="4.26.0",  # transformers version used
        pytorch_version="1.13.1",  # pytorch version used
        py_version='py39',  # python version used
        image_uri=image_uri,  # image uri
    )

    # Specify MemorySizeInMB and MaxConcurrency
    serverless_config = ServerlessInferenceConfig(
        memory_size_in_mb=memory_size, max_concurrency=max_concurrency,
    )

    # deploy the serverless endpoint
    return huggingface_model.deploy(
        serverless_inference_config=serverless_config, endpoint_name=endpoint_name
    )


if __name__ == "__main__":

    # create_endpoint("pegasus-xsum-4-24", "google/pegasus-xsum", 6144, 5)
    # create_endpoint("bart-xsum-4-24", "facebook/bart-large-xsum", 6144, 5)

    endpoints_to_create = [("bart-cnn-25-6-5", "facebook/bart-large-cnn", 6144, 5),
                           ("flan-t5-25-6-5", "google/flan-t5-base", 6144, 5),
                           ("pegasus-cnn-25-6-5", "google/pegasus-cnn_dailymail", 6144, 5),
                           ("bigbird-pegasus-arxiv-25-6-5", "google/bigbird-pegasus-large-arxiv", 6144, 5),
                           ("bart-arxiv-25-6-5", "ccdv/lsg-bart-base-16384-arxiv", 6144, 5),
                           ("pegasus-tifu-25-6-5", "google/pegasus-reddit_tifu", 6144, 5),
                           ("bart-samsum-25-6-5", "philschmid/bart-large-cnn-samsum", 6144, 5),
                           ("flan-t5-samsum-25-6-5", "philschmid/flan-t5-base-samsum", 6144, 5),
                           ("pegasus-xsum-25-6-5", "google/pegasus-xsum", 6144, 5),
                           ("bart-xsum-25-6-5", "facebook/bart-large-xsum", 6144, 5),
                           ("t5-small-wikihow-25-6-5", "deep-learning-analytics/wikihow-t5-small", 6144, 5),
                           ("pegasus-wikihow-25-6-5", "google/pegasus-wikihow", 6144, 5),
                           ("bart-base-booksum-25-6-5", "KamilAin/bart-base-booksum", 6144, 5),
                           ("bigbird-pegasus-25-6-5", "pszemraj/bigbird-pegasus-large-K-booksum", 6144, 5)]

    for endpt, model, mem, max_concur in endpoints_to_create:
        create_endpoint(endpt, model, mem, max_concur)


