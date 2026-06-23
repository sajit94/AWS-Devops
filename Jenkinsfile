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

        // Smoke test URL through Nginx
        SMOKE_TEST_URL = "http://172.31.21.151/api/person/Sajith"
    }

    stages {
        stage('Checkout Code') {
            steps {
                echo 'Pulling latest code from GitHub...'
                checkout scm
            }
        }

        stage('Detect Changed Files') {
            steps {
                script {
                    def changedFiles = sh(
                        script: '''
                        echo "Detecting changed files..."

                        if [ -n "$GIT_PREVIOUS_SUCCESSFUL_COMMIT" ] && git cat-file -e "$GIT_PREVIOUS_SUCCESSFUL_COMMIT^{commit}" 2>/dev/null; then
                            git diff --name-only $GIT_PREVIOUS_SUCCESSFUL_COMMIT $GIT_COMMIT
                        elif git rev-parse HEAD~1 >/dev/null 2>&1; then
                            git diff --name-only HEAD~1 HEAD
                        else
                            git ls-files
                        fi
                        ''',
                        returnStdout: true
                    ).trim()

                    echo "Changed files:"
                    echo changedFiles

                    env.DEPLOY_FRONTEND = "false"
                    env.DEPLOY_BACKEND  = "false"
                    env.DEPLOY_NGINX    = "false"

                    if (changedFiles.contains("frontend/")) {
                        env.DEPLOY_FRONTEND = "true"
                    }

                    if (changedFiles.contains("backend/")) {
                        env.DEPLOY_BACKEND = "true"
                    }

                    if (changedFiles.contains("nginx/")) {
                        env.DEPLOY_NGINX = "true"
                    }

                    echo "DEPLOY_FRONTEND = ${env.DEPLOY_FRONTEND}"
                    echo "DEPLOY_BACKEND  = ${env.DEPLOY_BACKEND}"
                    echo "DEPLOY_NGINX    = ${env.DEPLOY_NGINX}"
                }
            }
        }

        stage('Validate Required Files') {
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
                echo "Current Jenkins workspace:"
                pwd

                echo ""
                echo "Deployment files:"
                ls -l ${FRONTEND_FILE}
                ls -l ${BACKEND_FILE}
                ls -l ${REQUIREMENTS_FILE}
                ls -l ${NGINX_CONF_FILE}
                '''
            }
        }

        stage('Backup Current Frontend') {
            when {
                expression {
                    env.DEPLOY_FRONTEND == "true" || env.DEPLOY_NGINX == "true"
                }
            }
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

        stage('Deploy Frontend') {
            when {
                expression {
                    env.DEPLOY_FRONTEND == "true"
                }
            }
            steps {
                sshagent(['nginx-ec2-key']) {
                    sh '''
                    echo "Deploying frontend to Nginx EC2..."

                    scp -o StrictHostKeyChecking=no ${FRONTEND_FILE} ec2-user@${NGINX_HOST}:/tmp/index.html

                    ssh -o StrictHostKeyChecking=no ec2-user@${NGINX_HOST} "
                        sudo cp /tmp/index.html ${REMOTE_FRONTEND_DIR}/index.html
                    "

                    echo "Frontend deployment completed."
                    '''
                }
            }
        }

        stage('Deploy Nginx Config') {
            when {
                expression {
                    env.DEPLOY_NGINX == "true"
                }
            }
            steps {
                sshagent(['nginx-ec2-key']) {
                    sh '''
                    echo "Deploying Nginx config..."

                    scp -o StrictHostKeyChecking=no ${NGINX_CONF_FILE} ec2-user@${NGINX_HOST}:/tmp/testapp.conf

                    ssh -o StrictHostKeyChecking=no ec2-user@${NGINX_HOST} "
                        sudo cp /tmp/testapp.conf ${REMOTE_NGINX_CONF} &&
                        sudo nginx -t &&
                        sudo systemctl reload nginx
                    "

                    echo "Nginx config deployment completed."
                    '''
                }
            }
        }

        stage('Backup Current Backend') {
            when {
                expression {
                    env.DEPLOY_BACKEND == "true"
                }
            }
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
            when {
                expression {
                    env.DEPLOY_BACKEND == "true"
                }
            }
            steps {
                sshagent(['python-ec2-key']) {
                    sh '''
                    echo "Deploying backend to Python EC2..."

                    ssh -o StrictHostKeyChecking=no ec2-user@${PYTHON_HOST} "
                        sudo mkdir -p ${REMOTE_BACKEND_DIR}
                    "

                    scp -o StrictHostKeyChecking=no ${BACKEND_FILE} ec2-user@${PYTHON_HOST}:/tmp/app.py
                    scp -o StrictHostKeyChecking=no ${REQUIREMENTS_FILE} ec2-user@${PYTHON_HOST}:/tmp/requirements.txt

                    ssh -o StrictHostKeyChecking=no ec2-user@${PYTHON_HOST} "
                        sudo cp /tmp/app.py ${REMOTE_BACKEND_DIR}/app.py &&
                        sudo cp /tmp/requirements.txt ${REMOTE_BACKEND_DIR}/requirements.txt &&
                        sudo chown -R ec2-user:ec2-user ${REMOTE_BACKEND_DIR} &&
                        cd ${REMOTE_BACKEND_DIR} &&
                        python3 -m pip install -r requirements.txt --user
                    "

                    echo "Backend deployment completed."
                    '''
                }
            }
        }

        stage('Restart Backend Python App') {
            when {
                expression {
                    env.DEPLOY_BACKEND == "true"
                }
            }
            steps {
                sshagent(['python-ec2-key']) {
                    sh '''
                    echo "Restarting backend Python app..."

                    ssh -o StrictHostKeyChecking=no ec2-user@${PYTHON_HOST} "
                        echo 'Stopping existing Python backend process...'

                        pkill -f 'python3 app.py' || true
                        pkill -f '/opt/testapp/app.py' || true

                        echo 'Starting Python backend...'

                        cd ${REMOTE_BACKEND_DIR}
                        nohup python3 app.py > app.log 2>&1 &

                        sleep 5

                        echo 'Running process:'
                        ps -ef | grep '[p]ython3 app.py'

                        echo ''
                        echo 'Listening port check:'
                        ss -ltnp | grep 8000 || true

                        echo 'Backend Python app restarted.'
                    "
                    '''
                }
            }
        }

        stage('No Application Changes Detected') {
            when {
                expression {
                    env.DEPLOY_FRONTEND == "false" &&
                    env.DEPLOY_BACKEND == "false" &&
                    env.DEPLOY_NGINX == "false"
                }
            }
            steps {
                echo 'No frontend, backend, or nginx changes detected. Skipping deployment stages.'
            }
        }

        stage('Smoke Test') {
            steps {
                sh '''
                echo "Running smoke test through Nginx..."
                curl -f ${SMOKE_TEST_URL}
                echo ""
                echo "Smoke test passed."
                '''
            }
        }
    }

    post {
        success {
            echo 'Application pipeline completed successfully.'
        }

        failure {
            echo 'Application pipeline failed. Check Jenkins console output.'
        }
    }
}