## Source
https://technology.riotgames.com/news/jenkins-ephemeral-docker-tutorial

We need to add one more container to your Jenkins ecosystem. The problem we need to solve is that Jenkins,
once configured, will want to talk to a Docker Host to provision slaves on as part of it’s configuration 
for the Docker Plugin. The only Docker Host we have is your development environment running Docker for 
Mac/Linux or Docker for Windows.

By default Docker for Mac/Linux and Docker for Windows don’t expose the common public port 2375 for 
Docker. While Docker for Windows let’s you enable this as a feature, Docker for Mac/Linux does not 
for security reasons. In the absence of a solution that works the same way on both platforms, the 
simplest solution for Docker for Windows is to enable exposing the port, which I’ll walk through at 
the end of this section). If you’re using Docker for Mac/Linux you’ll need to do a bit more work. 
The good news is you’ll have this solved in no time with your newfound docker-compose and Dockerfile powers.

