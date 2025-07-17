## Introduction
<div style="font-size: 15px;">
This project is tailored for the eHealth Questionnaire to assess the Intrinsic Capacity Score (IC Score) and provide patient recommendations.

The system is now adapted for English and Traditional Chinese.
</div>


## QUICKSTART
```
streamlit run frontend_display_result.py --server.port 8080
```

## Project Structure
<div style="font-size: 14px;">
<pre>
chatbot_frontend/  
├── images/  
│   └── scales/  
│       ├── 0.png  
│       ├── 0_gray.png  
│       └── ...              # Other scale images  
├── pages/    
│   └── Test_Result.py       # Streamlit page for test results
├── Questionnaire/    
│   ├── eHealth_questionnaire_en.yaml       # eHealth Questionnaire (Eng)
│   └── eHealth_questionnaire_zh.yaml       
├── Rubric/    
│   ├── eHealth_icscore_rubric_en.yaml       # eHealth IC Score Rubric (Eng)
│   └── eHealth_icscore_rubric_zh.yaml       
├── test/    
│   ├── answers.json       # test patient answer
│   └── ic_score.json      # test patient IC Score
├── frontend_display_result.py       # Main Page
├── translation.py       # Common Translation
├── requirements.txt     # Python Packages

</pre>
</div>

<br>

## todos
- [x] Added Test Result Page to demonstrate the Questionnaire Test Result
- [x] Added IC Scores on the Test Result Page. [Update on 2025.05.12: Added scales with different colored images for better demonstration and intuitive understanding.]
- [x] Added Recommendations, and Videos and Resources Tabs n Test Result Page
- [x] Added Traditional Chinese Questionnaire, Rubric, and Common Translations
- [ ] Link each question in the Questionnaire to the database using a unique ID instead of the question itself
- [ ] Finalize the wording of questions and answers, including the schema for each answer’s data type

<br>



## Frontend Preview
<div style="font-size: 18px;">
Main Page

![preview home page](./assets/preview_homepage.png)


Test Result  
</div>






