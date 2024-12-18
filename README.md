![Web App CI/CD](https://github.com/software-students-fall2024/5-final-finalfour/actions/workflows/web_app.yml/badge.svg?branch=main)

![Bar Recs CI/CD](https://github.com/software-students-fall2024/5-final-finalfour/actions/workflows/bar_recs.yml/badge.svg?branch=main)

[![Event Logger CI/CD](https://github.com/software-students-fall2024/5-final-finalfour/actions/workflows/event-logger.yml/badge.svg)](https://github.com/software-students-fall2024/5-final-finalfour/actions/workflows/event-logger.yml)


# HOME-BREWED: NYC BAR RECOMMENDER SYSTEM

***Home-Brewed*** is a versatile web application designed to enhance the way users explore, manage, and discover their favorite bars. This platform offers a personalized experience, catering to individual tastes and preferences, while simplifying the process of tracking and finding bars.
 
***Purpose:*** Crafted for individuals passionate about discovering new bars and managing personal experiences. Whether for casual outings, date nights, or special occasions, this app empowers users to make informed decisions while keeping track of their favorite spots.

## TABLE OF CONTENTS

1. [Description](#description)
2. [Links to DockerHub Images](#dockerhub-images)
3. [Setup Steps](#setup-steps)
4. [Team Members](#team-members)

## DESCRIPTION

***Home-Brewed*** is a web application designed to help users manage and explore their favorite bars based on personalized preferences. It provides a seamless user experience for adding, searching, sorting, editing, and receiving bar recommendations.

### Key Features

1. ***User Authentication:*** Secure login and logout features to ensure user sessions are protected.

2. ***Intuitive Navigation:*** A clean and organized navigation bar allows users to seamlessly switch between the key functionalities Home, Add, Edit/Delete, Search, Sort, and Reccomendations.
   
3. ***Add New Bars:*** Users can contribute by adding their favorite bars to the database with the categories name, type, occasion, area, if reservation is needed, cost, and if user visited.

4. ***Edit/Delete Existing Bars:*** Easily modify or remove existing entries to keep the bar database up-to-date and accurate.

5. ***Search for Bars:*** Quickly find bars that match specific criteria or keywords.
  
6. ***Sort Bars:*** Organize bars based on any category like occasion, area, cost, or if the user visited.
  
7. ***Personalized Recommendations:*** Displays a curated list of bars with details tailored to user preferences based on the saved bars.

## DOCKERHUB IMAGES

### Web App

![DockerHub](https://img.shields.io/badge/DockerHub-WebApp-blue?logo=docker)

[DockerHub Image - Web App](https://hub.docker.com/repository/docker/emilyhuang19/web_app/general)

```
docker pull emilyhuang19/web_app:latest
```

### Bar Recs
![DockerHub](https://img.shields.io/badge/DockerHub-BarRecs-blue?logo=docker)

[DockerHub Image - Bar Recs](https://hub.docker.com/repository/docker/emilyhuang19/bar-recs/general)


```
docker pull emilyhuang19/bar-recs:latest
```

## SETUP STEPS

**1. Clone the Repository**

```
git clone <[repository-url](https://github.com/software-students-fall2024/5-final-finalfour)>
cd <5-final-finalfour>
```

**2. Verify MongoDB Connection:**

- *Download MongoDB:* download this extension onto your chosen source code editor
- *Connect to Database URL:* mongodb+srv://eh96:finalfour123@bars.ygsrg.mongodb.net/finalfour?retryWrites=true&w=majority&tlsAllowInvalidCertificates=true

**3. Confirm ENV Filepath:** Ensure the .env file is in the main repository

**4. Go to Correct Filepath:**

- _Mac:_

  ```
  cd Desktop/5-final-finalfour-main/web-app
  ```

- _Windows:_
  ```
  cd Desktop\5-final-finalfour-main\web-app
  ```

**5. Create a Virtual Environment:**

- _Mac:_

  ```
  python3 -m venv .venv
  source .venv/bin/activate
  ```

- _Windows:_
  ```
  python3 -m venv .venv
  .venv\Scripts\activate
  ```

**6. Install Dependencies:**

```
pip install opencv-python-headless
pip install pytest pytest-cov
pip install requests
pip install pymongo
pip install -r requirements.txt
```

**7. Install Docker-Compose:**

```
brew install docker-compose
```

**8. Integrate with Docker Compose:**

```
docker-compose down --volumes --remove-orphans
docker-compose up --build
```

**9. Get Drinking!:** Access our NYC Bars Recommender System [here](http://104.236.30.209:5000/)!

## TEAM MEMBERS

- [Wenli Shi](https://github.com/WenliShi2332)
- [Alex Hsu](https://github.com/hsualexotake)
- [Reese Burns](https://github.com/reeseburns)
- [Emily Huang](https://github.com/emilyjhuang)
