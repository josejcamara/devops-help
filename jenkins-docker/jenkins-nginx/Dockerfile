FROM centos:centos7
# https://technology.riotgames.com/news/jenkins-docker-proxies-and-compose

# Install NGINX
RUN yum -y update; yum clean all
RUN yum -y install http://nginx.org/packages/centos/7/noarch/RPMS/nginx-release-centos-7-0.el7.ngx.noarch.rpm; yum -y makecache
RUN yum -y install nginx-1.18.0

# Clean up the default config
RUN rm /etc/nginx/conf.d/default.conf

# Add our config files
COPY config/jenkins.conf /etc/nginx/conf.d/jenkins.conf
COPY config/nginx.conf /etc/nginx/nginx.conf

EXPOSE 80
CMD ["nginx"]