# OSRSTracker
Thank you for checking out this early project build! New features to come and improvements to existing features will be made!

<!-- # Build website (Windows)
`make -C \OSRSTracker\src run` -->

# Build website (MacOS)
`make api_test USER=$USERNAMEHERE`
Clean and then populate the `skill_stats.json` file with a valid OSRS character name in `$USERNAMEHERE`.

`make run`
Build the website and open to the site at `http://localhost:8080/`.

`make clean`
Stop Docker from running and delete the existing `skill_stats.json` file.

# Features
Running the makefile with an existing OSRS Character name as an argument will populate the `skill_stats.json` file with their stats.

An economy feature is planned which will look up items and their market trends and price information relative to the date and time of lookup.

# Test Names
Use these usernames using the `api_test` make command as some examples.

Apple
Lelalt