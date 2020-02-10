# Agilecraft Automation Application

This is a small python script written to help out the QA team when creating defects, since a large part of the process is very repetitive.
It is dependent on XPaths manually taken from the website, as well as a list of names associated with a carrier and a platform. The XPaths are stored in code,
due to the fact that if the website were ever to change, they need to be easily accessible for future updates. However, all other data (including the user's credentials)
is stored in a JSON file within a resources folder inside the application.

## Building the application

To build the application for deployment, [fbs](https://build-system.fman.io/) was used.
To build yourself, create a virtual environment and install [Python3](https://www.python.org/downloads/), [PyQt5](https://pypi.org/project/PyQt5/), fbs, and all of their dependencies.
Start the virtual environemnt and from the git root run `fbs run`. This will build the application from source, and allows for testing during development. Once you are ready to deploy, follow the instructions for building the application from the [fbs](https://build-system.fman.io/). 
