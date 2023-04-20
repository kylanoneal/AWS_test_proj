from sagemaker.huggingface.model import HuggingFaceModel
from sagemaker.serverless import ServerlessInferenceConfig
from sagemaker.huggingface.model import HuggingFacePredictor


def invoke_endpoint(input_text):
    predictor = HuggingFacePredictor(endpoint_name="bart-large-cnn-more-mem")
    prediction = predictor.predict({'inputs': input_text})
    return prediction[0]['summary_text']


def create_endpoint(endpoint_name, model_name, memory_size):
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
        memory_size_in_mb=memory_size, max_concurrency=1,
    )

    # deploy the serverless endpoint
    return huggingface_model.deploy(
        serverless_inference_config=serverless_config, endpoint_name=endpoint_name
    )


if __name__ == "__main__":
    create_endpoint("t5-base-4-20", "t5-base", 3072)
