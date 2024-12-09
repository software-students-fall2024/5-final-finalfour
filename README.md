[![Web App CI/CD](https://github.com/software-students-fall2024/5-final-finalfour/actions/workflows/web_app.yml/badge.svg)](https://github.com/<your-username>/<your-repo>/actions/workflows/web_app.yml)
[![Bar Recs CI/CD](https://github.com/software-students-fall2024/5-final-finalfour/actions/workflows/bar_recs.yml/badge.svg)](https://github.com/<your-username>/<your-repo>/actions/workflows/bar_recs.yml)
[![Event Logger CI/CD](https://github.com/software-students-fall2024/5-final-finalfour/actions/workflows/event-logger.yml/badge.svg)](https://github.com/<your-username>/<your-repo>/actions/workflows/event-logger.yml)


# NYC BAR RECOMMENDER SYSTEM

## TABLE OF CONTENTS

1. [Description](#description)
2. [DockerHub Images](#dockerhub-images)
2. [Links to Container Images](#container-images)
3. [Setup Steps](#setup-steps)
4. [Team Members](#team-members)


## Project Description

This project consists of three main subsystems:
- **Web App**: A Flask-based web application for managing and recommending bars.
- **Bar Recs**: A recommendation engine for bars based on user preferences.
- **Event Logger**: A logging system for tracking application events.

Each subsystem is containerized using Docker, deployed on DigitalOcean, and uses CI/CD pipelines to ensure automated builds, tests, and deployments.

## DockerHub Images

### Web App
The Docker image for the Web App is available on DockerHub:
[![DockerHub](https://img.shields.io/badge/DockerHub-WebApp-blue?logo=docker)](https://hub.docker.com/r/emilyhuang19/web_app)

Pull the image:

```
docker pull emilyhuang19/web_app:latest
```

### Bar Recs
[![DockerHub](https://img.shields.io/badge/DockerHub-WebApp-blue?logo=docker)](https://hub.docker.com/repository/docker/emilyhuang19/bar-recs/general)

## DESCRIPTION
Home-Brewed Web Application

Home-Brewed is a web application designed to help users manage and explore their favorite bars based on personalized preferences. It provides a seamless user experience for adding, searching, sorting, editing, and receiving bar recommendations.

### Key Features

1. **User Authentication**
	-  Secure login and logout features to ensure user sessions are protected.
2. **Intuitive Navigation**
	- A clean and organized navigation bar allows users to seamlessly switch between key functionalities, including: Home, Add, Edit/Delete, Search, Sort, and Reccomendations
   
3. **Add New Bars**
	- Users can contribute by adding their favorite bars to the database with details such as: Name, Type, Occasion, Location, Reservation Availability, and ost 
4. **Edit/Delete Existing Bars**
	- Easily modify or remove existing entries to keep the data up-to-date and accurate.
5. **Search for Bars**
   - Quickly find bars that match specific criteria or keywords.
6. **Sort Bars**
   - Organize bars based on user preferences such as: Cost, Type, and Ocassion
7. **Personalized Recommendations**
   - Displays a curated list of bars tailored to user preferences, including: Type, Occasion, Area, Reservation status, Cost, Type, Occasion

## DockerHub Images

### Web App

[![DockerHub](https://img.shields.io/badge/DockerHub-WebApp-blue?logo=docker)]([https://hub.docker.com/r/emilyhuang19/web_app](https://hub.docker.com/repository/docker/emilyhuang19/web_app/general))

Pull the image:

```
docker pull emilyhuang19/web_app:latest
```

### Bar Recs
[![DockerHub](https://img.shields.io/badge/DockerHub-BarRecs-blue?logo=docker)](https://hub.docker.com/repository/docker/emilyhuang19/bar-recs/general)

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

- _Download MongoDB:_ download this extension onto your chosen source code editor
- _Connect to Database URL:_ mongodb://mongodb:27017/

**3. Ensure you have the .env file loaded!**

**3. Go to Correct Filepath:**

- _Mac:_

  ```
  cd Desktop/5-final-finalfour-main/web-app
  ```

- _Windows:_
  ```
  cd Desktop\5-final-finalfour-main\web-app
  ```

**4. Create a Virtual Environment:**

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

**5. Install Dependencies:**

```
pip install opencv-python-headless
pip install pytest pytest-cov
pip install requests
pip install pymongo
pip install -r requirements.txt
```

**6. Build the Docker Images**

for bar recs:

```
docker build -t emilyhuang19/bar-recs:latest ./bar_recs
docker push emilyhuang19/bar-recs:latest

```

for web app:

```

docker buildx create --use

docker buildx build --platform linux/amd64 -t emilyhuang19/web_app:latest ./web_app --push
```


**7. Run the Docker Containers:**

```
docker run -d --name web-app -p 5000:5000 emilyhuang19/web_app:latest

docker run -d --name bar-recs -p 5001:5001 emilyhuang19/bar-recs:latest

```

**8. Get Drinking!:** Access our NYC Bars Recommender System [here](http://104.236.30.209/:5000)!

## TEAM MEMBERS

- [Wenli Shi](https://github.com/WenliShi2332)
- [Alex Hsu](https://github.com/hsualexotake)
- [Reese Burns](https://github.com/reeseburns)
- [Emily Huang](https://github.com/emilyjhuang)
