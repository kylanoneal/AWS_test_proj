import textwrap
import torch
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer
from datasets import load_dataset


def save_model(model_name):
    model = AutoModelForSeq2SeqLM.from_pretrained(model_name)
    model.save_pretrained(model_name + ".pt")


def get_summ_from_pretrained(model_name, article):
    device = "cuda" if torch.cuda.is_available() else "cpu"

    is_t5 = True if model_name[:2] == "t5" else False
    prefix = "summarize: " if is_t5 else ""
    truncate = not is_t5
    max_length = None if is_t5 else 1024

    if model_name[:14] == "google/pegasus":
        model = AutoModelForSeq2SeqLM.from_pretrained(model_name, max_position_embeddings=1024).to(device)
        tokenizer = AutoTokenizer.from_pretrained(model_name)
    else:
        model = AutoModelForSeq2SeqLM.from_pretrained(model_name).to(device)
        tokenizer = AutoTokenizer.from_pretrained(model_name)

    inputs = tokenizer(prefix + article, truncation=truncate, padding=False, return_tensors="pt",
                       max_length=max_length).to(device)

    summary_ids = model.generate(**inputs, max_new_tokens=500)
    output_text = tokenizer.batch_decode(summary_ids, skip_special_tokens=True, clean_up_tokenization_spaces=False)[0]

    return output_text.replace("<n>", '\n')


# Get some sample outputs for some leading pre-trained summarization models
if __name__ == "__main__":
    # save_model("t5-base")
    cnn_dataset = load_dataset("cnn_dailymail", "3.0.0", split='train[:1%]')

    wrapper = textwrap.TextWrapper(width=75)
    end_str = "\n\n\n########################\n\n\n"
    model_names = ["t5-small", "t5-large", "google/pegasus-xsum", "google/pegasus-cnn_dailymail",
                   "facebook/bart-large-xsum", "facebook/bart-large-cnn"]

    # Change index for a new article
    ex_article = cnn_dataset["article"][6]

    outputs = [wrapper.wrap("Original article: " + ex_article)]

    for name in model_names:
        summ = get_summ_from_pretrained(name, ex_article)
        outputs.append(wrapper.wrap(name + ": " + summ))

    for text in outputs:
        for line in text:
            print(line)
        print(end_str)
