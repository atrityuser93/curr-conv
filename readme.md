# Currency Converter 

## Objectives:
- Test ability of developer to design, test and implement a given project within a given deadline using the necessary tools
- Ability to design and implement a project in Python

## Project Scope:
- Develop an application in Python that can convert any(pre-defined set) input currency to any(pre-defined set) output currency
- Use data available on the web to ascertain conversion rates between currencies on any given day
- Develop an API and/or a web interface (to be decided during implementation) for the application

## Milestones and Deadlines:
- Daily updates and August 18, 2023

## Frameworks and Implementation:
- Python 3.11
- Django-Ninja (for API only)
- Django for web application backend
- HTML, CSS and js as part of Bootstrap V5 for application frontend (for Web GUI only)

## August 12, 2023
- use `requests` package to perform `GET` requests to any foreign exchange data server API to get country names and symbols
- use `requests` package to perform `GET` requests to any foreign exchange server API to get current conversion rates (once per day)
- Build Django application with function-based views (not class-based views) to support Django-Ninja with a GUI front-end (HTML, CSS and JS)
- use Django-Ninja for APIs on function-based views in Django

## August 14, 2023
- Complete use of `requests` to obtain and store currency symbols in local database (SQLlite) from [Fixer API](http://data.fixer.io)
- Use `requests` to obtain current conversion rate using [Fixer API](http://data.fixer.io)
- Complete conversion logic based on input -> USD -> output
- Debugging in progress
- APIs pending

## August 15, 2023
- Completed and Working backend for currency converter
- Data fetching is supposed to occur only once per week (to minimize API calls), so if conversion uses existing data from db, rates will be outdated
- Display of final result can be made better (front-end)
- API implementation pending


