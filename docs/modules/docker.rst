Docker
======
Bend the Docker modules to your will.


Port mapping
------------




Advanced Docker commands
------------------------

------------------------
Docker install
------------------------
It is best to follow the `official Docker instructions <https://docs.docker.com/install/#supported-platforms>`_ for installation.

^^^^^^^^^^^^^^^^^
Ubuntu
^^^^^^^^^^^^^^^^^
Direct links:

* Docker install: https://docs.docker.com/install/linux/docker-ce/ubuntu/
* Docker compose: https://docs.docker.com/compose/install/
* https://docs.docker.com/install/linux/linux-postinstall/
* https://docs.docker.com/compose/completion/

**Warning**: Check first what every command does before executing. Commands might be outdated.

Add current user to group docker on Linux systems. This prevents the need of typing ``sudo``
before every docker command.

.. code-block:: bash

   sudo usermod -a -G docker $USER

Docker machine (ip):

.. code-block:: bash

   base=https://github.com/docker/machine/releases/download/v0.16.0 &&
     curl -L $base/docker-machine-$(uname -s)-$(uname -m) >/tmp/docker-machine &&
     sudo install /tmp/docker-machine /usr/local/bin/docker-machine

Docker machine bash completion:

.. code-block:: bash

   base=https://raw.githubusercontent.com/docker/machine/v0.16.0
     for i in docker-machine-prompt.bash docker-machine-wrapper.bash docker-machine.bash
     do
       sudo wget "$base/contrib/completion/bash/${i}" -P /etc/bash_completion.d
     done



-------------------------
Useful Docker commands
-------------------------

.. code-block:: bash

   sudo usermod -a -G docker $USER  # add current user to group docker on Linux systems (Ubuntu)

   docker build . -t foo/bar  # build docker image
   docker run -it foo/bar  # run build docker image and enter interactive mode
   docker run -p 5550:5550 -it foo/bar  # same as above with mapping Docker port to host
   docker-compose up  # run docker-compose.yml
   docker-compose build / docker-compose up --build  # rebuild images in docker-compose.yml

   docker image ls  # show docker images
   docker container ls  # show docker containers
   docker exec -it pyzmq-docker_pub_1  # enter bash in container
   docker attach pyzmq-docker_sub_1  # get
   docker inspect -f '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' pyzmq-docker_sub_1  # get ip of container

   To detach the tty without exiting the shell, use the escape sequence Ctrl+p + Ctrl+q

   docker stop $(docker ps -a -q)  # stop all CONTAINERS
   docker rm $(docker ps -a -q)  # remove all CONTAINERS
   docker rm $(docker images -q)  # remove all IMAGES