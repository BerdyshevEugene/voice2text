pipeline {
    agent any
    parameters {
        string(name: 'DEPLOY_ENV', defaultValue: 'prod', description: 'Среда деплоя')
    }
    triggers {
        pollSCM('H/3 * * * *')
    }
    environment {
        BOT_TOKEN = credentials('bot_token')
        CHAT_ID = credentials('chat_id')
        MESSAGE_THREAD_ID = credentials('message_thread_id')
        FTP_CREDS = credentials('ftp_credentials')
        DOCKER_HUB = credentials('docker-hub-cred')
        SSH_DOCKER_SERVER = credentials('ssh-docker-server')
        MAJOR_VERSION = '0'
        MINOR_VERSION = '0'
        PATCH_VERSION = "${BUILD_NUMBER}"
        FULL_VERSION = "${MAJOR_VERSION}.${MINOR_VERSION}.${PATCH_VERSION}"
    }
    stages {
        stage('Start') {
          steps {
            script {
              String message = """
                ℹ Pipeline Start
                BUILD TAG: `${BUILD_TAG}`
                URL: `${BUILD_URL}`
                NODE NAME: `${NODE_NAME}`
                WORKSPACE: `${WORKSPACE}`
              """.stripIndent()
              sh("""
                curl -s -X POST https://api.telegram.org/bot${BOT_TOKEN}/sendMessage \
                -d chat_id=${CHAT_ID} \
                -d message_thread_id=${MESSAGE_THREAD_ID} \
                -d parse_mode=markdown \
                -d text='${message}'
              """)
            }
          }
        }
        stage('Build') {
          steps {
            sh '''
              wget --ftp-user=$FTP_CREDS_USR \
              --ftp-password=$FTP_CREDS_PSW \
              -r ftp://nas01.gmed.group/DevOpsInfra/jenkins_assets/voice2text/vosk/ -nH --cut-dirs=3
            '''
            sh 'docker login -u="$DOCKER_HUB_USR" -p="$DOCKER_HUB_PSW"'
            sh 'docker build -t gsssupport/voice2text:$FULL_VERSION .'
            sh 'docker tag gsssupport/voice2text:$FULL_VERSION gsssupport/voice2text:latest'
            sh 'docker push gsssupport/voice2text:$FULL_VERSION'
            sh 'docker push gsssupport/voice2text:latest'
          }
        }
        stage('Deploy') {
          steps {
            configFileProvider([
              configFile(fileId: 'voice2text.env', variable: 'ENV_FILE'),
              configFile(fileId: 'voice2text_inventory', variable: 'INVENTORY')
            ]) {
              withCredentials([sshUserPrivateKey(
                        credentialsId: 'ssh-docker-server-key',
                        keyFileVariable: 'SSH_KEY',
                        usernameVariable: 'SSH_USER'
              )]) {
              sh 'cp $ENV_FILE .env'
              sh 'cp $INVENTORY inventory.ini'
              sh 'cp $SSH_KEY ssh_key_docker_jenkins'
              sh 'chmod 600 ssh_key_docker_jenkins'
              sh '''
              ansible-playbook playbook.yml \
              --extra-vars "docker_user=${DOCKER_HUB_USR} docker_password=${DOCKER_HUB_PSW}"
              '''
              }
            }
          }
        }
    }
    post {
        success {
          script {
            String message = """
              ✅ Pipeline Success
              BUILD TAG: `${BUILD_TAG}`
              URL: `${BUILD_URL}`
              NODE NAME: `${NODE_NAME}`
              WORKSPACE: `${WORKSPACE}`
            """.stripIndent()
            sh("""
              curl -s -X POST https://api.telegram.org/bot${BOT_TOKEN}/sendMessage \
              -d chat_id=${CHAT_ID} \
              -d message_thread_id=${MESSAGE_THREAD_ID} \
              -d parse_mode=markdown \
              -d text='${message}'
            """)
          }
        }
        aborted {
          script {
            String message = """
              ⚠ Pipeline Aborted
              BUILD TAG: `${BUILD_TAG}`
              URL: `${BUILD_URL}`
              NODE NAME: `${NODE_NAME}`
              WORKSPACE: `${WORKSPACE}`
            """.stripIndent()
            sh("""
              curl -s -X POST https://api.telegram.org/bot${BOT_TOKEN}/sendMessage \
              -d chat_id=${CHAT_ID} \
              -d message_thread_id=${MESSAGE_THREAD_ID} \
              -d parse_mode=markdown \
              -d text='${message}'
            """)
          }
        }
        failure  {
          script {
            String message = """
              ❌ Pipeline Failure
              BUILD TAG: `${BUILD_TAG}`
              URL: `${BUILD_URL}`
              NODE NAME: `${NODE_NAME}`
              WORKSPACE: `${WORKSPACE}`
            """.stripIndent()
            sh("""
              curl -s -X POST https://api.telegram.org/bot${BOT_TOKEN}/sendMessage \
              -d chat_id=${CHAT_ID} \
              -d message_thread_id=${MESSAGE_THREAD_ID} \
              -d parse_mode=markdown \
              -d text='${message}'
            """)
          }
        }
    }
}
