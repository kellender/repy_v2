"""
   Author: Justin Cappos

   Start Date: 29 June 2008

   Description:

   Timer functions for the sandbox.   This does sleep as well as setting and
   cancelling timers.
"""

import threading
import thread # Armon: this is to catch thread.error
import nanny
import idhelper

# This is to use do_sleep
import misc

# for printing exceptions
import tracebackrepy

# for harshexit
import harshexit

# Import the exception hierarchy
from exception_hierarchy import *

##### Constants

# Armon: Prefix for use with event handles
EVENT_PREFIX = "_EVENT:"


##### Internal Functions

# Generates a valid event handle
def generate_eventhandle():
  """
  <Purpose>
    Generates a string event handle that can be used to uniquely identify an event.
    It is formatted so that cursory verification can be performed.

  <Returns>
    A string event handle.
  """
  # Get a unique handle from idhelper
  uniqueh = idhelper.getuniqueid()

  # Return the unique handle prefixed with EVENT_PREFIX
  return (EVENT_PREFIX + uniqueh)


# Helps validate an event handle
def is_valid_eventhandle(eventhandle):
  """
  <Purpose>
    Determines if a given event handle is valid.
    This does not guarantee validity, just proper form.

  <Arguments>
    eventhandle:
      The event handle to be checked.

  <Returns>
    True if valid, False otherwise.
  """
  # The handle must be a string, check type first
  if type(eventhandle) != str:
    return False

  # Check if the handle has the correct prefix
  return eventhandle.startswith(EVENT_PREFIX)


##### Public Functions

def sleep(seconds):
  """
   <Purpose>
      Allow the current event to pause execution (similar to time.sleep()).
      This function will not return early for any reason

   <Arguments>
      seconds:
         The number of seconds to sleep.   This can be a floating point value

   <Exceptions>
      None.

   <Side Effects>
      None.

   <Returns>
      None.
  """
  # Use the do_sleep implementation in misc
  misc.do_sleep(seconds)


def createthread(function):
  """
  <Purpose>
    Creates a new thread of execution.

  <Arguments>
    function:
      The function to invoke on entering the new thread.

  <Exceptions>
    RepyArgumentError is raised if the function is not callable.
    ResourceExhaustedError is raised if there are no available events.

  <Side Effects>
    Launches a new thread.

  <Resource Consumption>
    Consumes an event.

  <Returns>
    None
  """
  # Check if the function is callable
  if not callable(function):
    raise RepyArgumentError, "Provided function is not callable!"

  # Generate a unique handle and see if there are resources available
  eventhandle = generate_eventhandle()
  nanny.tattle_add_item('events', eventhandle)

  # Wrap the provided function
  def wrapped_func():
    try:
      function()
    except:
      # Exit if they throw an uncaught exception
      tracebackrepy.handle_exception()
      harshexit.harshexit(30)
    
    # Remove the event before I exit
    nanny.tattle_remove_item('events',eventhandle)

  # Create a thread object
  tobj = threading.Thread(target=wrapped_func, name=idhelper.get_new_thread_name(EVENT_PREFIX))

  # Check if we get an exception trying to create a new thread
  try:
    tobj.start()
  except thread.error, exp:
    # Set exit code 56, which stands for a Threading Error
    # The Node manager will detect this and handle it
    harshexit.harshexit(56)
 