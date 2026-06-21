pipeline {
    agent any

    stages {
        stage('Checkout') {
            steps {
                echo 'Code pulled from GitHub successfully'
                checkout scm
            }
        }

        stage('List Files') {
            steps {
                sh 'pwd'
                sh 'ls -la'
                sh 'find . -maxdepth 3 -type f'
            }
        }

        stage('Check Tools') {
            steps {
                sh 'whoami'
                sh 'git --version'
                sh 'aws --version'
                sh 'terraform version'
            }
        }

        stage('Check AWS Access') {
            steps {
                sh 'aws sts get-caller-identity'
            }
        }
    }
}
