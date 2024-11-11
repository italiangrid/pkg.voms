#!/usr/bin/env groovy

def pkg_build_number() {
    now = new Date().format("yyyyMMddHHmmss")
    return "${env.BUILD_NUMBER}.${now}"
}

def platform2Dir = [
  "centos7" : 'rpm',
  "centos7java8" : 'rpm',
  "centos7java11": 'rpm',
  "centos7java17": 'rpm',
  "centos9" : 'rpm',
  "almalinux8java8": 'rpm',
  "almalinux9java8": 'rpm',
  "almalinux9java11": 'rpm',
  "almalinux9java17": 'rpm',
]

def buildPackages(platform, platform2Dir, includeBuildNumber) {
  return {
    unstash "source"

    def platformDir = platform2Dir[platform]

    if (!platformDir) {
      error("Unknown platform: ${platform}")
    }

    def includeEnv = ""
    if (includeBuildNumber) {
      includeEnv = "INCLUDE_BUILD_NUMBER=1"
    }

    dir(platformDir) {
      sh "PLATFORM=${platform} ${includeEnv} pkg-build.sh"
    }
  }
}

pipeline {
  agent {
    label 'docker'
  }

  options {
    timeout(time: 1, unit: 'HOURS')
    buildDiscarder(logRotator(numToKeepStr: '5'))
  }

  triggers {
    cron('@daily')
  }

  parameters {
    booleanParam(name: 'INCLUDE_BUILD_NUMBER', defaultValue: false, description: 'Include build number into rpm name')
  }

  environment {
    PKG_TAG = "${env.BRANCH_NAME}"
    DOCKER_REGISTRY_HOST = "${env.DOCKER_REGISTRY_HOST}"
    PLATFORMS = "almalinux8java8 almalinux9java8 centos7java8"
    PACKAGES_VOLUME = "pkg-vol-${env.BUILD_TAG}"
    STAGE_AREA_VOLUME = "sa-vol-${env.BUILD_TAG}"
    PKG_BUILD_NUMBER = "${pkg_build_number()}"
    DOCKER_ARGS = "--rm -v /opt/cnafsd/helper-scripts/scripts/:/usr/local/bin "
  }

  stages{
    stage('checkout') {
      steps {
        deleteDir()
        checkout scm
        stash name: "source", includes: "**"
      }
    }

    stage('setup-volumes') {
      steps {
        sh 'pwd && ls -lR'
        sh 'rm -rf artifacts && mkdir -p artifacts'
        sh './setup-volumes.sh'
      }
    }

    stage('package') {
      steps {
        script {
          def buildStages = PLATFORMS.split(' ').collectEntries {
            [ "${it} build packages" : buildPackages(it, platform2Dir, params.INCLUDE_BUILD_NUMBER) ]
          }
          parallel buildStages
        }
      }
    }

    stage('archive-artifacts') {
      steps {
        sh 'pkg-copy-artifacts.sh'
        archiveArtifacts "artifacts/**"
      }
    }

    stage('cleanup') {
      steps {
          sh 'docker volume rm ${PACKAGES_VOLUME} ${STAGE_AREA_VOLUME} || echo Volume removal failed'
      }
    }
  }
}
