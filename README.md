# Dance Partner Tracker
## Overview
Simple script that will help you parse, track and keep notes about various dance partners in yaml format.

Currently support only dancesport.ru source.

PartnerFinder.search_url - contains hard coded search URL (query string with following parameters):
```yaml
    Country: Russia
    City: Moscow
    Birth year: from 1989 to 1996
    Body height: from 165 to 177
    Class: Latin A,S
```

## Roadmap
- [ ] migrate load_from_web functionality to separate proxy/adapter class for dancesport
- [ ] chane STATE var to more robust and easy for debugging class
- [ ] break into several modules
- [ ] add logging and debugging capabilities
- [ ] add terminaltables output
- [ ] add tests
- [ ] build interactive cli menu with specialized module
- [ ] add interactive workflow