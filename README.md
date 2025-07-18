## Quickstart Intro


This project integrates a Flask server with a Streamlit frontend, using Redis as a backend cache for session management and content delivery. The system allows sending various types of content (videos, questions, plain text) via APIs and controlling video playback. Follow the steps below to get started quickly.

<br>

### Step 1: Start the Redis Server
Open a terminal and run the following command to start the Redis server:
```
redis-server
```
<br>

### Step 2: Start the Flask Server
In a new terminal, navigate to the project directory and run:
```
python flask_test.py
```

<br>

### Step 3: Run the Streamlit Frontend Server
In another terminal, navigate to the project directory and run:
```
streamlit run Streamlit.py
```
This launches the Streamlit web interface.

<br> 

### Step 4: Configure the Streamlit Frontend
- Once the Streamlit app is running, open it in your browser. In the interface:

- Input the Session ID (e.g., "10").
Input the Flask Server domain (e.g., http://localhost:5000 if running locally).

<br>

## JSON Content Templates for Flask APIs
Use the following APIs to interact with the system. All endpoints are hosted on the Flask server.

### API 1: Sending Content to the Streamlit Frontend Server
Endpoint: 
```
http://<Flask_server_ip>/post_message
```

Method: POST

Purpose: Send different types of content (video, scale questions, yes/no questions, or plain text) to a specific session.

<br>

#### Case 1: Video
```
{
    "session_id": "10", 
    "type": "video",
    "message": "https://www.youtube.com/watch?v=_kGESn8ArrU&ab_channel=GlobalTriathlonNetwork"
}
```


#### Case 2: Scale Question
```
{
    "session_id": "10",
    "type": "text",
    "language": "en",     // en or zh
    "question_format": "scale",
    "order": "descending",     // ascending or descending
    "MIN": 0,
    "MAX": 6,
    "message": "Do you see things clearly? (With wearing glasses or contact lens, if any)(0-5, 0 = very good to 5 = very poor)"
    // "message": "你看東西清晰嗎? (連同戴眼鏡或隱形眼鏡), 0= 看得很好 至 6 = 幾乎/完全看不到"
}
```


#### Case 3: Yes/No Question
```
{
    "session_id": "10",
    "type": "text",
    "language": "en",     // en or zh
    "question_format": "yes_no",
    "message": "Do you have more than 5% weight loss within the past 6 months?"
    // "message": "過去6個月，體重有沒有出現明顯下降（大約 5%）？"
}
```


#### Case 4: Plain Text
```
{
    "session_id": "10",
    "type": "text",
    "language": "en",     // en or zh
    "question_format": "plain", // or null
    "message": "Hello, this is testing message"
    // "message": "你好，這是測試信息"
}
```


<br>

### API 2: Control Start or Stop of Video Content
Endpoint: 
```
http://<flask_server_ip>/post_video_command
```

Method: POST

Purpose: Start/resume or pause video playback for a session.

```
{
    "session_id": "10",
    "start_or_stop": true   // true to start or resume video, false to pause video
}
```


<br>

### API 3: Pass Session ID to the Streamlit Frontend Server (Instead of Manual Input)
Endpoint: 
```
http://<flask_server_ip>/post_session_id
```

Method: POST

Purpose: Programmatically set the session ID on the frontend, bypassing manual input.

```
{
    "session_id": "10"
}
```

<br>

## Troubleshooting
### Question 1: The Streamlit Frontend Loads the Previous Redis Cache (Last Session ID and Content)


**Answer:** Clean the Redis server to remove historical content and reset the cache.


**Step 1:** Ensure the Redis server is running. If not, start it with:
```
redis-server
```

**Step 2:** Open a terminal and connect to the Redis CLI:
```
redis-cli
```

**Step 3:** Run the following command to delete all keys from all databases:
```
flushall
```

<br>

### Question 2: Play OR Stop Command is not allow / does not work via the API `http://<flask_server_ip>/post_video_command`

**Answer:** This issue occurs due to the **browser's autoplay policy**, which requires a high level of user engagement to allow video playback. We recommend using Firefox, as it permits autoplay (e.g., playing a video via the API) after adjusting specific browser settings.


#### If You Are Using Chrome (Some Features Are Limited):
>**Tradeoff 1**: You can pass the Session ID through the API `http://<flask_server_ip>/post_session_id`. However, you may not be able to play the video via the API `http://<flask_server_ip>/post_video_command`. 
> <br>
>
>Chrome will block autoplay, causing the video stream to start and pause immediately. You will need to resume the video manually. After that, you can use the Video Control API without issues.
>
>**OR**
>
>**Tradeoff 2**: If you manually input the Session ID on the frontend, the API http://<flask_server_ip>/post_video_command should work without any issues.



#### If You Are Using `Firefox`:

> To enable autoplay for media with audio or video, follow these steps:
>
>**Step 1:** In the `Menu` bar at the top of the screen, click `Firefox` and then select `Preferences or Settings`, depending on your macOS version.
>
>**Step 2:** Select the `Privacy & Security` panel and go down to the `Permissions` section
(or enter autoplay in the Find in Settings search box).
>
>**Reference Link:** https://support.mozilla.org/en-US/kb/block-autoplay

