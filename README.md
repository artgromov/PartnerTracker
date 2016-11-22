# Partner Tracker command line utility
## Overview
Interactive tool that will help you keep notes about dance partners and track updates from various sources.

**Implemented source providers and searches:**
- dancesport.ru
    - Currently doesnt support search parameter interactive customization and parameters changing.
    - Following parameters are hard coded in "partner_tracker.searchers.search_on_dancesport.query_url":

        ```yaml
        Country: Russia
        City: Moscow
        Birth year: from 1989 to 1996
        Body height: from 165 to 177
        Class: Latin B, A, S
        Sex: female
        ```

**Requirements**
- requests
- bs4
- cli (my module for command line interactive loop: https://github.com/artgromov/cli)

## Status
Project closed
