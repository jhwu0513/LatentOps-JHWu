import os
import math

from datasets import load_from_disk, Dataset, concatenate_datasets
from transformers import AutoModelForPreTraining,AutoTokenizer,AutoModelForMaskedLM
from transformers import DataCollatorForLanguageModeling
from transformers import Trainer, TrainingArguments
from transformers import LineByLineTextDataset
from transformers import PreTrainedTokenizerFast
from transformers import BertConfig, BertModel

def tokenize_function(example):
    return tokenizer(example["content"], padding="max_length", truncation=True, max_length=128)


# train_file = "train_corpus.txt"
# eval_file = "test_corpus.txt"
max_seq_length = 128
out_model_path = "bert-small"

print('Load tokenizer')
tokenizer = AutoTokenizer.from_pretrained("bencyc1129/bert-small", model_max_length=max_seq_length)
data_collator = DataCollatorForLanguageModeling(tokenizer=tokenizer, mlm=True, mlm_probability=0.2)
# train_dataset = LineByLineTextDataset(
#         tokenizer=tokenizer,
#         file_path=train_file,
#         block_size=max_seq_length,
#     )
# eval_dataset = LineByLineTextDataset(
#         tokenizer=tokenizer,
#         file_path=eval_file,
#         block_size=max_seq_length,
#     )
# print('Define training argument')

with open('train_corpus.txt', 'r') as f:
    raw_dataset = [l.strip() for l in f.readlines()]
with open('test_corpus.txt', 'r') as f:
    for l in f.readlines():
        raw_dataset.append(l.strip())

art_dataset = {'content': raw_dataset}
art_dataset = Dataset.from_dict(art_dataset)
# powershell_dataset = load_from_disk('../powershell')
# dataset = concatenate_datasets([powershell_dataset, art_dataset])
# dataset = dataset.train_test_split(test_size=0.2)
train_dataset = dataset['train'].map(tokenize_function, batched=True, num_proc=30)
eval_dataset = dataset['test'].map(tokenize_function, batched=True, num_proc=30)

training_args = TrainingArguments(
        output_dir=out_model_path,      # output directory to where save model checkpoint
        evaluation_strategy="steps",    # evaluate each `logging_steps` steps
        overwrite_output_dir=True,      
        num_train_epochs=10,            # number of training epochs, feel free to tweak
        per_device_train_batch_size=25, # the training batch size, put it as high as your GPU memory fits
        # gradient_accumulation_steps=8,  # accumulating the gradients before updating the weights
        per_device_eval_batch_size=25,  # evaluation batch size
        logging_steps=10000,               # evaluate, log and save model checkpoints every 1000 step
        save_steps=10000,
        load_best_model_at_end=True,  # whether to load the best model (in terms of loss) at the end of training
        save_total_limit=1,           # whether you don't have much space so you let only 3 model weights saved in the disk
    )

print('Load model')
config = BertConfig.from_pretrained('prajjwal1/bert-small')
config.vocab_size = tokenizer.vocab_size
model = AutoModelForMaskedLM.from_config(config)

print('Define trainer')
trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=train_dataset,
        eval_dataset=eval_dataset,
        data_collator=data_collator,
    )

print('Start training')

trainer.train()

trainer.save_model(out_model_path)
eval_results = trainer.evaluate()
print(f"Perplexity: {math.exp(eval_results['eval_loss']):.2f}")