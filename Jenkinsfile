pipeline {
    agent any

    environment {
        NGINX_HOST  = "172.31.21.151"
        PYTHON_HOST = "172.31.8.214"
    }

    stages {
        stage('Check Nginx EC2 Utilization') {
            steps {
                sshagent(['nginx-ec2-key']) {
                    sh """
ssh -o StrictHostKeyChecking=no ec2-user@${NGINX_HOST} 'bash -s' <<'EOF'
echo "======================================"
echo " NGINX EC2 UTILIZATION REPORT"
echo "======================================"
echo "Hostname:"
hostname

echo ""
echo "Date:"
date

echo ""
echo "Uptime / Load Average:"
uptime

echo ""
echo "CPU Usage:"
top -bn1 | grep "Cpu"

echo ""
echo "Memory Usage:"
free -h

echo ""
echo "Disk Usage:"
df -h /

echo ""
echo "Top 10 CPU consuming processes:"
ps -eo pid,user,comm,%cpu,%mem --sort=-%cpu | head -11

echo ""
echo "Top 10 Memory consuming processes:"
ps -eo pid,user,comm,%cpu,%mem --sort=-%mem | head -11
EOF
                    """
                }
            }
        }

        stage('Check Python EC2 Utilization') {
            steps {
                sshagent(['python-ec2-key']) {
                    sh """
ssh -o StrictHostKeyChecking=no ec2-user@${PYTHON_HOST} 'bash -s' <<'EOF'
echo "======================================"
echo " PYTHON EC2 UTILIZATION REPORT"
echo "======================================"
echo "Hostname:"
hostname

echo ""
echo "Date:"
date

echo ""
echo "Uptime / Load Average:"
uptime

echo ""
echo "CPU Usage:"
top -bn1 | grep "Cpu"

echo ""
echo "Memory Usage:"
free -h

echo ""
echo "Disk Usage:"
df -h /

echo ""
echo "Top 10 CPU consuming processes:"
ps -eo pid,user,comm,%cpu,%mem --sort=-%cpu | head -11

echo ""
echo "Top 10 Memory consuming processes:"
ps -eo pid,user,comm,%cpu,%mem --sort=-%mem | head -11
EOF
                    """
                }
            }
        }
    }
}