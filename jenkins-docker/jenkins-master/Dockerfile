FROM jenkins/jenkins:2.249.1

# Executors config
COPY config/executors.groovy /usr/share/jenkins/ref/init.groovy.d/executors.groovy

# Log config
USER root
RUN mkdir /var/log/jenkins
RUN mkdir /var/cache/jenkins
RUN chown -R jenkins:jenkins /var/log/jenkins
RUN chown -R jenkins:jenkins /var/cache/jenkins
USER jenkins
COPY config/log.properties /var/jenkins_home/log.properties

## https://www.jenkins.io/doc/book/managing/system-properties/
# ENV JAVA_OPTS="-Djenkins.install.runSetupWizard=false \
ENV JAVA_OPTS="-Djava.util.logging.config.file=/var/jenkins_home/log.properties \
-Xmx2048m"
ENV JENKINS_OPTS=" --handlerCountMax=100 \
--logfile=/var/log/jenkins/jenkins.log \
--webroot=/var/cache/jenkins/war"

# Skip install wizard, but still configure a secure Jenkins by creating the admin user
# COPY config/secureAdminUser.groovy /usr/share/jenkins/ref/init.groovy.d/security.groovy

# Install this list of plugins
COPY config/plugins.txt /usr/share/jenkins/ref/plugins.txt
RUN /usr/local/bin/install-plugins.sh < /usr/share/jenkins/ref/plugins.txt