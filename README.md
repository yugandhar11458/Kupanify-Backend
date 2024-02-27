
# Kupanify Backend

The following are the instructions to run the Frontend:
    

## Run Locally

Clone the project

```bash
git clone https://github.com/yugandhar11458/Kupanify-Backend.git
```

Install dependencies

```bash
pip install -r requirements.txt
```

Go to the project directory

```bash
cd Coupons
```

Apply Database Migrations 
```bash
python manage.py makemigrations
python manage.py migrate 
```

Run the Django Development Server 
```bash
python manage.py runserver 
```

## Deployment

  1. Create AWS EC2 instance with Amazon Linux of minimum tier of t2.medium.
  2. Connect to the AWS EC2 instance terminal.
  3. Install github
```bash
  sudo yum install git 
```
 4. Install docker
```bash
 sudo yum install -y docker 
 sudo service docker start 
 sudo docker –version 
```

 5. Install docker compose
```bash
  sudo curl -L "https://github.com/docker/compose/releases/download/1.29.2/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
  sudo chmod +x /usr/local/bin/docker-compose
  sudo docker-compose --version 
```

6. Pull MySQL image and run the container

7. Install Jenkins
  ```bash
  sudo wget -O /etc/yum.repos.d/jenkins.repo \ 
  https://pkg.jenkins.io/redhat-stable/jenkins.repo 
```
```bash
 sudo dnf install java-11-amazon-corretto –y 
 sudo yum install jenkins –y 
 sudo systemctl enable jenkins 
 sudo systemctl start jenkins 
 sudo systemctl status jenkins     
```

Make sure to add the CORS_Headers in Settings.py with the updated frontend url/IpAddresss.

8. Jenkins 
  - Create jenkins user account and create new item.
  - Give the github url of the project in Project   URL and Source Code Management and add credentials
  - Add the following build steps
    ```bash
    docker build -t django-image:latest .
    docker-compose -f backend.yaml up -d 
    ```
  - Build the item.

9. Now the backend is live on port 8000 .ie., IpAddresss:8000.
