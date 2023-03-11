# DEV environments 

In order to keep clean your computer, without installing dozen of tools or versions, 
Visual Studio Code lets you use a container as a full-featured development environment.

For more details visit the [offical page](https://code.visualstudio.com/docs/devcontainers/containers), 
but the main steps are described below and also provided a demo container ready to work with Terraform and AWS.

1. Install Docker Engine or Desktop ([link](https://docs.docker.com/engine/install/ubuntu/)).
1. Set Docker for non-root users ([link](https://docs.docker.com/engine/install/linux-postinstall/)).
1. Restart (or apply changes in group and kill VSCode server process)
1. In your working folder, copy the `.devcontainer` folder provided in this repo. This container contains git, aws, terraform and a few more useful tools.
1. Open the folder in VSCode, you'll be asked for "open in container"
1. The first time you'll need to configure your tools:
    1. Configure git
    1. Configure aws
1. Enjoy

If you want to create your own container, with your own tools, follow the steps detailed [here](https://code.visualstudio.com/docs/devcontainers/containers#_create-a-devcontainerjson-file).



