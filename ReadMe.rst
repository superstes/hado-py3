.. |badge_docs| image:: https://readthedocs.org/projects/hado-py3/badge/?version=latest
.. |badge_test| image:: https://github.com/superstes/hado-py3/actions/workflows/tests/badge.svg

********************************
HA-DO - SIMPLE Clustering Engine
********************************

|badge_test| | |badge_docs|

Work-in-progress
################

This project is not yet in a stable state.

If you want to help building this HA-Engine => feel free to start discussions and open bugs/pr's!

----

Intro
#####

The goal of this project is it to provide a **simple base-engine for building high-available systems**.

`CoroSync <https://github.com/corosync>`_, `Heartbeat <http://www.linux-ha.org/wiki/Heartbeat>`_ and `Pacemaker <http://www.linux-ha.org/wiki/Pacemaker>`_ build the probably most commonly used HA-clustering stack.

I want to code an alternative to it.


----

Goals
#####

1. KEEP IT SIMPLE
*****************

Admins should be able to understand and troubleshoot the system after a few minutes.

Functionality can be added using `plugins <https://github.com/superstes/hado-python3/blob/main/Plugins.rst>`_. Allowing for advanced usage without increasing the core engines complexity.

2. Platform
***********

Initially this solution will only target **systems that use systemd** as init.


3. Functionality
****************

CORE
====

**MONITORING**

Checking the local-systems and peer states

**RESOURCES**

Interact with a resource needed by your HA-APP (*start, stop, promote, demote, alive, other*)

**STATE-API**

Lightweight http server to publish it's state

Used to exchange state-info between nodes.

Also - allows easy:

* monitoring

* debugging (*by simply reading the json output in your browser*)

Modular extensibility
=====================

The core uses `PLUGINS <https://github.com/superstes/hado-python3/blob/main/Plugins.rst>`_ to achieve its functionality.

Keeping the footprint of the base-engine small - you can add plugins as needed.

**Example plugins**:

* Resource for systemd services

* Resource for ip-addresses

* Monitoring of a running process

* Monitoring if some remote port is reachable

  The structure of such a plugin should be logic.

4. Transparency
***************

The functionality of the core should be logic and easily understandable and to troubleshoot.

----

Not really Goals
################

* Performance

  Python isn't the best performing language, but it does the job and is easy to read/write/understand.

  In the future we might write a GoLang implementation of this engine to achieve better performance, scalability and portability.

----

Documentation
#############

Documentation is very important to us as it enables it's usage.

|badge_docs|

You can find the documentation here: `Read the docs <https://hado.superstes.eu>`_
