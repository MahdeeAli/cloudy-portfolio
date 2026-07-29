pipeline {
    agent any

    stages {
        stage('Checkout Code') {
            steps {
                // Jenkins pulls the latest code from GitHub
                checkout scm
            }
        }

        stage('Deploy Application') {
            steps {
                // Jenkins runs the Docker Compose commands on your EC2 server
                sh 'docker compose down -v'
                sh 'docker compose up -d --build'
            }
        }
    }
}