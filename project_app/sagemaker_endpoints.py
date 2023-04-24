from sagemaker.huggingface.model import HuggingFaceModel
from sagemaker.serverless import ServerlessInferenceConfig
from sagemaker.huggingface.model import HuggingFacePredictor

endpoint_dict = {'news': {'t5': "flan-t5-base-4-24", 'bart': "bart-large-cnn-more-mem", 'pegasus': "pegasus-cnn-4-24"},
            'scientific': {'t5': "flan-t5-base-4-24", 'bart': "bart-large-cnn-more-mem", 'pegasus': "pegasus-cnn-4-24"},
            'fiction': {'t5': "flan-t5-base-4-24", 'bart': "bart-large-cnn-more-mem", 'pegasus': "pegasus-cnn-4-24"}}

def invoke_endpoint(input_text, genre_choice, model_choice):
    predictor = HuggingFacePredictor(endpoint_name=endpoint_dict[genre_choice][model_choice])
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
    endpoints_to_create = {'bart-cnn-4-24.0': ("facebook/bart-large-cnn", 6144, 5),
                           'flan-t5-4-24.0': ("google/flan-t5-base", 6144, 5),
                           'pegasus-cnn-4-24.0': ("google/pegasus-cnn_dailymail", 6144, 5)}

    for key in endpoints_to_create.keys():
        model_name, mem, max_concurrency = endpoints_to_create[key]
        create_endpoint(key, model_name, mem, max_concurrency)


