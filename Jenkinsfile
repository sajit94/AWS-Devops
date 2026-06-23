pipeline {
    agent any

    environment {
        // Target EC2 private IPs
        NGINX_HOST  = "172.31.21.151"
        PYTHON_HOST = "172.31.8.214"

        // GitHub repo paths
        FRONTEND_FILE     = "frontend/index.html"
        BACKEND_FILE      = "backend/app.py"
        REQUIREMENTS_FILE = "backend/requirements.txt"
        NGINX_CONF_FILE   = "nginx/testapp.conf"

        // Target server paths
        REMOTE_FRONTEND_DIR = "/usr/share/nginx/html"
        REMOTE_BACKEND_DIR  = "/opt/testapp"
        REMOTE_NGINX_CONF   = "/etc/nginx/conf.d/testapp.conf"

        // Backend service name
        BACKEND_SERVICE = "gunicorn"

        // Smoke test URL
        SMOKE_TEST_URL = "http://172.31.21.151/api/person/Sajith"
    }

    stages {
        stage('Checkout Code') {
            steps {
                echo 'Pulling latest code from GitHub...'
                checkout scm
            }
        }

        stage('Validate Files') {
            steps {
                sh '''
                echo "Validating required files..."

                test -f ${FRONTEND_FILE}
                test -f ${BACKEND_FILE}
                test -f ${REQUIREMENTS_FILE}
                test -f ${NGINX_CONF_FILE}

                echo "All required files are present."
                '''
            }
        }

        stage('List Deployment Files') {
            steps {
                sh '''
                echo "Current workspace:"
                pwd

                echo "Deployment files:"
                ls -l ${FRONTEND_FILE}
                ls -l ${BACKEND_FILE}
                ls -l ${REQUIREMENTS_FILE}
                ls -l ${NGINX_CONF_FILE}
                '''
            }
        }

        stage('Backup Current Frontend') {
            steps {
                sshagent(['nginx-ec2-key']) {
                    sh '''
                    echo "Taking backup of current frontend..."

                    ssh -o StrictHostKeyChecking=no ec2-user@${NGINX_HOST} "
                        sudo mkdir -p /backup/nginx-frontend &&
                        if [ -d ${REMOTE_FRONTEND_DIR} ]; then
                            sudo cp -r ${REMOTE_FRONTEND_DIR} /backup/nginx-frontend/html-$(date +%Y%m%d%H%M%S)
                        fi
                    "
                    '''
                }
            }
        }

        stage('Deploy Frontend and Nginx Config') {
            steps {
                sshagent(['nginx-ec2-key']) {
                    sh '''
                    echo "Copying frontend and Nginx config to Nginx EC2..."

                    scp -o StrictHostKeyChecking=no ${FRONTEND_FILE} ec2-user@${NGINX_HOST}:/tmp/index.html
                    scp -o StrictHostKeyChecking=no ${NGINX_CONF_FILE} ec2-user@${NGINX_HOST}:/tmp/testapp.conf

                    ssh -o StrictHostKeyChecking=no ec2-user@${NGINX_HOST} "
                        sudo cp /tmp/index.html ${REMOTE_FRONTEND_DIR}/index.html &&
                        sudo cp /tmp/testapp.conf ${REMOTE_NGINX_CONF} &&
                        sudo nginx -t &&
                        sudo systemctl reload nginx
                    "

                    echo "Frontend and Nginx config deployment completed."
                    '''
                }
            }
        }

        stage('Backup Current Backend') {
            steps {
                sshagent(['python-ec2-key']) {
                    sh '''
                    echo "Taking backup of current backend..."

                    ssh -o StrictHostKeyChecking=no ec2-user@${PYTHON_HOST} "
                        sudo mkdir -p /backup/python-backend &&
                        if [ -d ${REMOTE_BACKEND_DIR} ]; then
                            sudo cp -r ${REMOTE_BACKEND_DIR} /backup/python-backend/testapp-$(date +%Y%m%d%H%M%S)
                        fi
                    "
                    '''
                }
            }
        }

        stage('Deploy Backend') {
            steps {
                sshagent(['python-ec2-key']) {
                    sh '''
                    echo "Copying backend files to Python EC2..."

                    ssh -o StrictHostKeyChecking=no ec2-user@${PYTHON_HOST} "
                        sudo mkdir -p ${REMOTE_BACKEND_DIR}
                    "

                    scp -o StrictHostKeyChecking=no ${BACKEND_FILE} ec2-user@${PYTHON_HOST}:/tmp/app.py
                    scp -o StrictHostKeyChecking=no ${REQUIREMENTS_FILE} ec2-user@${PYTHON_HOST}:/tmp/requirements.txt

                    ssh -o StrictHostKeyChecking=no ec2-user@${PYTHON_HOST} "
                        sudo cp /tmp/app.py ${REMOTE_BACKEND_DIR}/app.py &&
                        sudo cp /tmp/requirements.txt ${REMOTE_BACKEND_DIR}/requirements.txt &&
                        cd ${REMOTE_BACKEND_DIR} &&
                        sudo python3 -m pip install -r requirements.txt
                    "

                    echo "Backend deployment completed."
                    '''
                }
            }
        }

        stage('Restart Backend Service') {
            steps {
                sshagent(['python-ec2-key']) {
                    sh '''
                    echo "Restarting backend service..."

                    ssh -o StrictHostKeyChecking=no ec2-user@${PYTHON_HOST} "
                        sudo systemctl restart ${BACKEND_SERVICE} &&
                        sudo systemctl status ${BACKEND_SERVICE} --no-pager
                    "
                    '''
                }
            }
        }

        stage('Smoke Test') {
            steps {
                sh '''
                echo "Running smoke test..."
                curl -f ${SMOKE_TEST_URL}
                echo ""
                echo "Smoke test passed."
                '''
            }
        }
    }

    post {
        success {
            echo 'Application upgrade completed successfully.'
        }

        failure {
            echo 'Application upgrade failed. Check Jenkins console output.'
        }
    }
}