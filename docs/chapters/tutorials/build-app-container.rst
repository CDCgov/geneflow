.. build-app-container

Build a Container for an App
============================

In this tutorial, we will build a custom container using Singularity. This tutorial will demonstrate basic concepts like how to choose a base image to build from, how to install a software package from github, how to install packages, and how to copy local files into the container. This is only an introduction. For more information on Singularity, check out the documentation at: https://sylabs.io/docs/ and use Google as usual.

Singularity Requirement
-----------------------

This tutorial is based on Singularity 2.6. It assumes that you have Singularity installed already and you have sufficient privileges to build an image (which may require sudo access). Check the Singularity documentation on how to install Singularity properly or with your system administrator.

A Container for RNA-Seq
-----------------------

In this tutorial, we will build a container with the following softwares:

1. STAR aligner (https://github.com/alexdobin/STAR)  
2. DESeq2 on Bioconductor/R (https://bioconductor.org/packages/release/bioc/html/DESeq2.html)
3. All dependencies required by the above 2 programs  

Singularity Recipe
------------------

A Singularity recipe is a set of instructions for building the Singularity image. The final Singularity recipe for building the image for the tutorial is below. I will breakdown what each section of the file does below. Meanwhile, copy it into a text file named `Singularity` using your favorite editor. The example here will use vi.

.. code-block:: text

    vi Singularity

Copy the following texts into the file and save it.

.. code-block:: text

    Bootstrap: docker
    From: r-base:3.6.0
    
    %files
    
      test.txt /opt/test.txt
    
    
    %environment

      TMPDIR=/opt
      export TMPDIR   
    

    %labels
    
       AUTHOR jyao
    
    
    %post
    
      #install STAR
      cd /opt/
      wget https://github.com/alexdobin/STAR/archive/2.7.2b.tar.gz
      tar -xzf 2.7.2b.tar.gz
      rm 2.7.2b.tar.gz
      ln -s /opt/STAR-2.7.2b/bin/Linux_x86_64/STAR /bin/STAR
    
      #Install dependencies packages
      apt-get update
      apt-get install -y libcurl4-openssl-dev
      apt-get install -y libxml2-dev
    
    
      #Install R packages
      export TMPDIR=/opt
      R --slave -e 'install.packages(c("BiocManager","docopt","stringi", "stringr"))'
      R --slave -e 'BiocManager::install(c("DESeq2"))'
    
    
    %runscript
      
      echo "the fruits of your success will be in direct ratio to the honesty and sincerity of your own effort in keeping your own records, doing your own thinking, and reaching your own conclusions. - Jesse Livermore"


Base Container
--------------

While it is possible to build a container from just a base operating system, it is often easier to start from images that already contain some of the software you want. In this case, we will start from the container image with R already installed. The image we will use is at https://hub.docker.com/_/r-base. The following code section in the recipe file tells Singularity to use this base image. The `Bootstrap:` options is set as "docker" to signify that we are building from a pre-existing docker image at the dockerhub. The `From:` options is set as "r-base:3.6.0" to signify that we want to use the r-base container tagged at 3.6.0. 

.. code-block:: text

    Bootstrap: docker
    From: r-base:3.6.0

Copy Files
----------

Although the image in this tutorial doesn't need any local files, you will often want to include some local files (a script for example) in your Singularity image. Therefore, we will copy a dummy file to demonstrate how to copy a file from the local directory into the docker container. Start by making a dummy file with the command:

.. code-block:: text

    echo "This is a test file" > test.txt


The section of the recipe file instructing Singularity to copy the file into the image is shown below. Under the `%file` section, specify the source and the destination separated by space. I generally copy files into the `/opt/` directory because most pre-built images have this directory. 

.. code-block:: text

    %files

      test.txt /opt/test.txt

Set Environmental Variables
---------------------------

The `%environment` section sets the environmental variables for your image at runtime (but not build time). I included an example of how to do this, but our image doesn't really need it.

.. code-block:: test

    %environment

      TMPDIR=/opt
      export TMPDIR

Metadata
--------

The `%labels` section contains all the metadata for the image. In this case, I put in my information as the author. 

.. code-block:: text

    %labels

       AUTHOR jyao

Install your software
---------------------

The `%post` section contains commands that are executed on top of the base image. This is where most of the setup is done. Our base image is an Ubuntu OS with R installed. Imagine we are running such a computer: what commands do we need to execute to install everything we want? 

In the first section of the code:   

1. We go to the /opt directory  
2. Download the STAR tarball  
3. Unzip the tarball to get the binary  
4. Remove the tarball  
5. Softlink the executable STAR binary into the /bin directory so we can execute it from the command line.  

In the second section of the code:   

1. We update the list of libraries for the Ubuntu OS  
2. Install the libcurl4-openssl-dev library  
3. Install the libxml2-dev library (both needed by R packages)  

In the final section of the code:

1. We export and set `TMPDIR` as "opt" because R will download and compile packages in the directory specified by the TMPDIR variable, and /tmp is often set as noexec.  
2. We install the R packages (including bioconductor).  
3. We install the Bioconductor package DESeq2.  


.. code-block:: text

    %post

      #install STAR
      cd /opt/
      wget https://github.com/alexdobin/STAR/archive/2.7.2b.tar.gz
      tar -xzf 2.7.2b.tar.gz
      rm 2.7.2b.tar.gz
      ln -s /opt/STAR-2.7.2b/bin/Linux_x86_64/STAR /bin/STAR

      #Install dependencies packages
      apt-get update
      apt-get install -y libcurl4-openssl-dev
      apt-get install -y libxml2-dev


      #Install R packages
      export TMPDIR=/opt
      R --slave -e 'install.packages(c("BiocManager","docopt","stringi", "stringr"))'
      R --slave -e 'BiocManager::install(c("DESeq2"))'

Container as an Executable
--------------------------

The `%runscript` section defines what commands are executed if the image is ran as an executable (see below). We echo a quote to demonstrate this function. 

.. code-block:: text

    %runscript

      echo "the fruits of your success will be in direct ratio to the honesty and sincerity of your own effort in keeping your own records, doing your own thinking, and reaching your own conclusions. - Jesse Livermore"


Build your image
----------------

Assuming you named your recipe file "Singularity", execute the following command to build your image ("STAR-DESeq2.img"). This will take some time and you will need to have sudo access.

.. code-block:: text

    sudo singularity build STAR-DESeq2.img Singularity


Working with your image
-----------------------

There are 3 main ways to interact with a Singularity image. Choose the method that best accomplish your goals. We will briefly explore all three.

Shell
~~~~~

You can interactively shell into your image using the following command. 

.. code-block:: text

    singularity shell STAR-DESeq2.img

Feel free to explore your virtual image. Try calling the manual of STAR with the following command:

.. code-block:: text

    STAR -h

Echo the environmental variable you set with the following command:

.. code-block:: text

    echo $TMPDIR

Check whether the test.txt got copied by going into the /opt directory:

.. code-block:: text

    cd /opt
    ls

Run R and check if DESeq2 is available with the following commands. Exit R with the `quit()` command.

.. code-block:: text 

    R
    library("DESeq2")

Exit the shell with `exit` when you are done exploring.


Run
~~~

The `singularity run` command executes the commands in the `%runscript%` section. Running the following command should echo the quote we put in our `%runscript%` section.

.. code-block:: text

    singularity run STAR-DESeq2.img

Exec
~~~~

The `singularity exec [IMAGE] [CMD]` command executes the command from the environment defined in the image. For example, the command below executes the STAR command from the STAR-DESeq2.img with the -h flag. 

.. code-block:: text

    singularity exec STAR-DESeq2.img STAR -h

Summary
-------

After this tutorial, you should know the basics of how to build and run a Singularity image. Note that building a complex image can be a frustrating experience because we take for granted the dependencies our programs need and are pre-installed on most computers. A container image will often require finding out every dependency (and their dependencies) and installing all of them. Try finding pre-existing containers whenever you can. A good resource for bioinformatic containers is https://quay.io/organization/biocontainers.
