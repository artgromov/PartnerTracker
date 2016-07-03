# Partner Tracker command line utility
## Overview
Interactive tool that will help you keep notes about dance partners and track updates from various sources.

**Currently implemented source providers and searches:**
- dancesport.ru
    - Currently doesnt support search parameter interactive customization and parameters changing.
    - Following parameters are hard coded in "partner_tracker.searchers.SearcherDancesportRu.query_url":
        ```yaml
        Country: Russia
        City: Moscow
        Birth year: from 1989 to 1996
        Body height: from 165 to 177
        Class: Latin A,S
        ```

**Requirements**
- requests
- BeautifulSoup
- cli (my module, link will be later)

## Roadmap
- [x] migrate load_from_web functionality to separate proxy/adapter class for dancesport
- [x] chane STATE var to more robust and easy for debugging class
- [x] break into several modules
- [x] add logging and debugging capabilities
- [x] build interactive cli menu with specialized module
- [ ] add interactive workflow
- [ ] add timezone support
- [ ] migrate data storage from pickle to ORM
- [ ] add searcher initialization with capability to set custom search parameters
- [ ] add tests

