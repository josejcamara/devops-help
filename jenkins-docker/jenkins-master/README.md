# Dockerfile-Jenkins
Creates a Jenkins Master using the jenkins official docker image.
https://hub.docker.com/r/jenkins/jenkins/

# Dockerfile-CentOS
Creates a Jenkins Master controlling your own image based on CentOS7

https://github.com/jenkinsci/docker

# Dockerfile
Creates a Jenkins Master controlling your own image based on Debian9(stretch)

https://github.com/jenkinsci/docker


# Notes

For the custom image we got a copy of these files from the Cloudbees Jenkins Dockerfile Github repo. (*utility-files* folder)

1. init.groovy
1. install-plugins.sh
1. plugins.sh
1. jenkins.sh  
1. jenkins-support

You technically don’t have to keep these, but before you decide not to use them here’s a quick rundown of what they do:

1. init.groovy - This file is run when Jenkins starts, and as a groovy file it runs with context inside the Java WAR that is Jenkins. In this case it’s taking the environment variable set for the Slave agents (50000) and making sure that is the port Jenkins uses. You can do a lot more with this groovy file to guarantee Jenkins starts with the same configuration settings, even on a fresh installation.

1. Install-plugins.sh - This is a handy file that can be run to auto-download a list of plugins from a plugins text file. Including a list of plugins to install is something you’ll have to do yourself but in a future blog post I’ll use this to make sure things like the necessary Docker plugins are always installed.  

1. plugins.sh - This is a legacy version of install-plugins.sh and is deprecated. Cloudbees seems to include this as a favor to legacy users. You can probably not install this and be fine.

1. jenkins.sh - This is a shell script that starts Jenkins using the JAVA_OPTS and JENKINS_OPTS environment variables we set.  You should probably keep this one.

1. jenkins-support  - A utility script that gathers support data for cloudbees.

A downside to having our own Dockerfile like this is that if Cloudbees chooses to update these in the future, you won’t get automatic updates. It will pay to keep apprised of any changes Cloudbees makes in case you want to take advantage of them.