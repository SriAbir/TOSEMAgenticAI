# agenticAI project

We simulated three-role agent interactions — a Designer (responsible for conceptual design and improvement) and a Programmer (responsible for implementation) and a Compiler (Solves Compilation Error)— across 19 model pair combinations and 8 Programming task

## Contents Explained
The content of each folder/file is explained as follows:

 Conversation Files- Annotated excel files containing agent conversation transcripts. Organized under two folfers i)WithCompiler ii) WithoutCompiler. Please access the files from https://drive.google.com/drive/folders/1fDeZz666-jmaIaNCXvFsdID4AAy7LOhU?usp=sharing

Folder: agenticAI-main- The framework and program used to generate the conversation along with instructions to replicate it

File: Appendix- Appendix File containing additional details to support the main paper

Folder: Metrics- i) roleAlignmentFinal.py - Python script to measure Role Alignment Score of conversation ii)TopicStability.py - Python script to measure Topic Stability Score of conversation iii) TopicStability - Python script to measure Loop Detection Score and Loop Repetition rate of conversation

## Using the key
If you want to use the OpenAI servers, or another server with the API KEY, please set the OPENAI_API_KEY environment variable, for example: export OPENAI_API_KEY="your_token_here" 
