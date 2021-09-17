INTRO
    # This is the solution for the TraceLabs / OriginTrail task 
    # The web application is written in Python with Django framework
    # Used libraries: Pandas, Web3

SETUP 

    1. Clone github repository

    2. Run script 'run.sh'

    3. Open browser at given address 
        (default is http://127.0.0.1:8000/)

APP USAGE

    # Searching takes some time, do not refresh page.

    # Progress for each search can be seen in cmd/Terminal
    
FUTURE VERSIONS

    # Add database to store data and speed up searches
    # since the blockchain is immutable.
    
    # The database would approximately consist of the following table:
    
      Table name: Tx                     
                   From                
                   To                  
                   Amount              
                   Block    
           
    # Balance would not be stored since it is not time and memmory consuming
    # and has a low probability of searching multiple times
    
           
