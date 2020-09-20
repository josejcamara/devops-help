# Jenkins_infrastructure

Based on this excelent tutorial:
https://technology.riotgames.com/news/thinking-inside-container

It will create a Jenkins Master server accessible by a nginx reverse proxy.

## What can I find here

- How to use the offical Jenkins image
- How to create a custom image (debian/centos)
- How to use docker-compose
- How to set some Jenkins/Java properties
- How to pre-install plugins
- How to skip the install wizard and create a default admin user.

## How to Run

- Execute `make build`
- Execute `make run`
- Open your browser on `http://localhost/login`
- Get the admin password: `docker exec -it jenkins_jmaster_1 cat /var/jenkins_home/secrets/initialAdminPassword`
- Choose "Select plugins to install"
- Click on "None" (We have already pre-installed them)
- Continue the process by creating the admin user and confirming.

## How to configure your docker slave

We’re now ready to configure our Dockerhost and first ephemeral slave on Jenkins. On the Jenkins landing page do the following:

- Click on Manage Jenkins

- Click on Configure System

- Scroll down until you find Add new cloud as a drop down (comming from Jclouds plugin)

- Select Docker from the drop down

A new form pops. This form is the high level information you need to enter about your Dockerhost. Please note, you can create many Dockerhosts if you want. This is one way you can manage which build images run on which machines. For this tutorial, we’ll stick with one.
- In the Name field enter “LocalDockerHost”
-In the Docker Host URI field enter: “tcp://proxy1:2375”

- Click on Test Connection and you should get a response that shows Version and API version of your docker host.


If no response comes back or you get error text, something has gone wrong and Jenkins cannot talk to your Dockerhost. I’ve done my best to make sure this walkthrough “just works” but here’s a quick list of things that could be broken and affect this:

Your docker-compose file has a typo in it. Verify that there is an Alias for the proxy container set to “proxy1.”

Your docker proxy didn’t start for some reason. Check docker ps and verify you have a proxy container running.

For some reason your docker.sock file is not at /var/run/docker.sock. This tutorial assumes a default installation of Docker for Mac/Win. If you’ve reconfigured it then this won’t work.

Assuming you got a successful version response when testing the connection, we can proceed. We want to add our freshly minted build slave image as a potential build node candidate.

- Click the Enabled checkbox (by default this is off, this is a convenient way to disable a cloud provider for maintenance/etc in jenkins)

- Click on the Docker Agent templates... button

- Click on Add Docker Template button

- In the Labels field enter testslave

- Make sure the Enabled checkbox is selected (you can use this to disable specific images if they are causing problems)

- For the Docker Image field enter: jenkins_jslave

- For Remote Filing System Root enter /home/jenkins (this will be where the jenkins workspace goes in the container)

- For Usage select only build jobs with the label expressions matching this node

- Make sure the Connect Method is set to Attach Docker Container (this is the default and allows jenkins to attach/exec into the container, start the jenkins slave agent and point it back to your Jenkins server)

- For User enter jenkins

- Change pull strategy to Never pull (we make this image by building it, not pulling it from a repo)

- Click Save at the bottom of the configuration page


You have one last thing to do now. Make a build job to test this setup and confirm everything works.