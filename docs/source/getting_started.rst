Getting Started
===============

Understanding Process Mining
----------------------------

.. raw:: html

    <iframe width="560" height="315" src="https://www.youtube.com/embed/XLHtvt36g6U" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>

In this section, we explain what process mining is all about. 
Note that this page describes the basics of process mining, i.e., it is not a full-fledged reference of every possible aspect of process mining. 
Therefore, for a more detailed overview of process mining, we recommend looking at the `Coursera MOOC on Process Mining <https://www.coursera.org/learn/process-mining>`_ and the `seminal book of Wil van der Aalst <https://www.springer.com/gp/book/9783662498507>`_. 
Furthermore, before you begin, please install PM4Py on your system, i.e., as described in the :doc:`install` section.

Processes in our Modern World
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
The vast majority of companies active in virtually any domain execute a process. 
Whether the core business of a company is to deliver a product, e.g., manufacture a car, cook a delicious pizza, etc., or provide a service, e.g., providing you with a mortgage to buy your dream house, paying back your insurance claim, etc., for efficient delivery of your product/service, processes are executed. 
Hence, a natural question is: “What is a process?”. 
In general, several notions of the concept of a process exist. 
However, in process mining, we typically assume the following conceptual definition:

"A **process** represents a **collection of activities** that we **execute** to achieve a **certain goal**."

For example, consider the burger restaurant just around the corner, which also delivers burgers.
When you call the restaurant to order your beloved burger, the first action taken by the employee, let’s call her **Lucy**, taking your call, is to *take your order*. 
Let’s assume you go for a tasty cheeseburger with a can of soda. 
After Lucy has *entered your order in the cash register*, she *asks for your address*, which she adds to the order. 
Finally, she *asks for your preferred means of payment*, after which she provides you with a rough estimate of the time until delivery. 
When Lucy finishes the call, she *prints your order* and hands it over to the chef, let’s call him **Luigi**. 
Since you’ve called relatively early, Luigi can start *preparing your burger* right away. 
At the same time, Lucy *takes a can of soda out of the refrigerator* and places it on the counter. 
A new call comes in from a different customer, which she handles roughly the same way as yours. 
When Luigi *finishes your burger*, he *slides it into a carton box* and hands the box over to Lucy. 
Lucy *wraps the order* in a bag. 
She then hands the bag with your burger and soda to **Mike**, which uses a fancy electrical bicycle to *bring your order to your home*.

In this small example, let’s assume that we are interested in the process, i.e., the collection of activities performed for your order. 
Based on the scenario we just presented, the steps look as follows:


1. **Lucy** *takes your order*
#. **Lucy** *notes down your address*
#. **Lucy** *notes down your preferred payment method*
#. **Luigi** *prepares your burger*
#. **Lucy** *grabs your can of soda*
#. **Luigi** *puts your burger in a box*
#. **Lucy** *wraps your order*
#. **Mike** *delivers your order*
