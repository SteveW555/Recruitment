groq/llama-3.3-70b-versatile
groq/meta-llama/llama-4-scout-17b-16e-instruct
together_ai/openai/gpt-oss-20b
gemini/gemini-flash-latest

groq/llama-3.1-8b-instant

openai/gpt-5.1-chat-latest
anthropic/claude-sonnet-4-5-20250929
gemini/gemini-3-pro-preview


## ========================================================  
                      Baseline. 
## ========================================================

************************************************
                 INFERENCE
************************************************

**==============  Single  ==============**

**Single Baseline inference with file**
python ExampleBaseline/basic_dspy_query.py `
    -s "Extract names and hours. return *only* the required info formatted as name, hours" `
    -f All_Examples\examples\messy_0.csv `
    -m groq/meta-llama/llama-4-scout-17b-16e-instruct

**==============  Folder  ==============**

python ExampleBaseline/basic_batch.py -f All_Examples/examples_orig -m gemini/gemini-3-pro-preview -s "Extract names and hours. return *only* the required info formatted as name, hours"

**Folder Inference using Select Models file**
python ExampleBaseline\run_selected_models.py -l bestcheapmodels.txt -f All_Examples -s "Extract names and hours. return *only* the required info formatted as: name, hours"




## ========================================================  
##                      GEPA. 
## ========================================================

************************************************
                   TRAIN
************************************************
--auto heavy {light,medium,heavy}
--reflection-minibatch-size Number of examples per reflection step (default: 3)


# Specify student and teacher model
python gepa/gepa_train.py --student together_ai/openai/gpt-oss-20b --reflection-model gemini/gemini-3-pro-preview --examples-folder All_Examples/ 

//--- Add Options ---
python gepa/gepa_train.py --student together_ai/openai/gpt-oss-20b --reflection-model gemini/gemini-3-pro-preview --examples-folder All_Examples/ --auto heavy --reflection-minibatch-size 5



************************************************
                 INFERENCE
************************************************
   
**==============  Single  ==============**

**Single Inference**
python gepa/gepa_inference.py --input All_Examples\examples\messy_0.csv --model groq/meta-llama/llama-4-scout-17b-16e-instruct
**==============  Folder  ==============**

**Folder Inference**
python gepa/gepa_inference.py --input All_Examples/ --model groq/meta-llama/llama-4-scout-17b-16e-instruct
    