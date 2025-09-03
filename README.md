# agenticai-business-analytics-chatbot
An Agentic AI solution to ask business/market share/finance related question to an AI ChatBot and get answeres in concise bullet points and illsutrative chart. Developed on Google's ADK and Streamlit UI.

The solution is based on Google's Agent Development Kit (ADK). The UI is powered by Streamlit.
This is a 4 agent based backend where the user query is first analysed and broken down into sub parts and confirms if the question is within its scope. Questions that are not finance related are politely declined.
Then another agent fetches content from the internet.
Followed by another agent gathering company's data from Yahoo Finance and creates an echarts option.
Lastly, the final agent, with all the information gathered from previous agents, creates an concise reponse with illustrative chart.

Screenshots of app:
<img width="1366" height="638" alt="image" src="https://github.com/user-attachments/assets/f7e69483-a790-4933-ae88-1b426d634bd5" />
<img width="1365" height="639" alt="image" src="https://github.com/user-attachments/assets/0ab681d7-ceed-401f-859e-646f481d140e" />
<img width="1366" height="640" alt="image" src="https://github.com/user-attachments/assets/fb3f73fa-785d-4bab-b3b5-6347fdfb685f" />

