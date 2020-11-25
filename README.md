# Message_Screener

This project was part of the DSI 2020 which was voted the best project in Module 3. Find the certification [here](https://drive.google.com/file/d/13HCegnHzkxRR_nCBpMfZeNRZ0g-b7gQZ/view?usp=sharing). The aim of the project is to create a tool that analyses a user's message before sending. This will enable social media users to be more mindful of their posts to avoid unnecessary controvercy by flagging words, tone and topics that might be considered sensitive. This repo contains code for the following product features:        
1. Feature 1: Profanity Screener (with blacklist)   
2. Feature 2: Sentiment analyser   
3. Feature 3: Topic Identifier    
4. Feature 4: Database functionity    
5. Feature 5: GUI (with requirements for Streamlit web deployment)   
The product is deployed at https://share.streamlit.io/malcolmrite-dsi/message_screener-1/main/Message_GUI.py 

## Summary

 [Getting Started](#getting-started)
 [Deployment](#deployment)
 [Challenges](#Challenges)
 [Authors](#authors)
 [License](#license)

 [Acknowledgments](#acknowledgments)


 ### Getting Started
 To get this project up and running in your machine, follow the steps below:

 - Clone this repository to your local machine by opening your terminal and typing:
 ```
 git clone https://github.com/CateGitau/Message_Screener
 ```

 - install the required packages:
 ```
 pip3 install -r requirements.txt
 ```

 - Run the Message_GUI.py file to get the project running in your local machine using Streamlit
 ```
 Streamlit run Message_GUI.py
 ```

 ### Deployment
 We used [streamlit sharing](https://www.streamlit.io/sharing) to deploy the application all you have to do is request and invite to start sharing the app then follow the instructions given.

 ### Challenges
 One of the challenges we faced while deploying is that the Sentiment Analyser model was too large and we had to use Github Large File Storage(LFS) and streamlit does not support git LFS. Try using another sentiment model and try and deploy that instead. But it works great on the local machine.

 ### Authors
 [Martin Page](https://github.com/malcolmrite-dsi)
 [Catherine Gitau](https://github.com/CateGitau)
 [Malcom Wright](https://github.com/malcolmrite-dsi)
 [Fanamby](https://github.com/FanambyH)

 ### License

 ### Acknowledgements

 We'd like to thank [Emile Lochner](https://www.linkedin.com/in/emile-lochner-94013914b/?originalSubdomain=za) who was our Tutor for the duration of this project.


