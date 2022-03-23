.. |docs_badge| image:: https://readthedocs.org/projects/hado-python3/badge/?version=latest

********************************
HA-DO - SIMPLE Clustering Engine
********************************

Intro
#####

The goal of this project is it to provide a **simple base-engine for building high-available systems**.

`CoroSync <https://github.com/corosync>`_, `Heartbeat <http://www.linux-ha.org/wiki/Heartbeat>`_ and `Pacemaker <http://www.linux-ha.org/wiki/Pacemaker>`_ build the probably most commonly used HA-clustering stack.

If you've ever had the *honor* of configuring such a cluster from scratch - you might have recognized that it's 'a little' complex to understand what is going on.

That proves especially important whenever you run into troubles.

There are some good resources (\*) out there, but after a few hours you might still wonder what is going wrong. (\*`CoroSync transport <https://people.redhat.com/ccaulfie/docs/KnetCorosync.pdf>`_,  `CoroSync quorum <https://people.redhat.com/ccaulfie/docs/Votequorum_Intro.pdf>`_)

It's logical that high-availability is no easy subject and it gains on complexity the more you think about it. But in my opinion there could be easier ways of achieving basic HA-setups.


**Let's give it a shot!**

----

Goals
#####

KEEP IT SIMPLE
**************

Admins should be able to understand and troubleshoot the system after a few minutes

Functionality can be added using plugins. Allowing for advanced usage without increasing the core engines complexity.


Functionality
*************

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

The core uses PLUGINS to achieve its functionality.

Keeping the footprint of the base-engine small - you can add plugins as needed.

**Example plugins**:

* Resource for systemd services

* Resource for ip-addresses

* Monitoring of a running process

* Monitoring if some remote port is reachable

  The structure of such a plugin should be logic.


Transparency
************

The functionality of the core should be logic and easily understandable and to troubleshoot.


Not really Goals
################

* Performance

  Python isn't the best performing language, but it does the job and is easy to read/write/understand.

  In the future we might write a GoLang implementation of this engine to achieve better performance, scalability and portability.

----

Documentation
#############

Documentation is very important to us as it enables it's usage.

|docs_badge|

You can find the documentation here: `Read the docs <https://hado.superstes.eu>`_
