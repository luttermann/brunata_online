brunata-online documentation
============================

Used for accessing the API behind the userpages at `Brunata Online <https://online.brunata.com/>`__


Usage example
-------------

.. code-block:: python
   :linenos:

   with open('.token.json', 'r') as f:
     td = TokenData(**json.load(f))

   client = BrunataOnlineClient(td)

   us = BrunataUser(client)
   user_information = us.get_user()

   print(user_information)





.. toctree::
   :maxdepth: 2
   :caption: Contents:

