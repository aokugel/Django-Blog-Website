# My Django Blog

### Overview

This is my django code repository for anthonykugel.com.  The website is written using the django web framework.  Frontend assets are written in html, css, and javascript.  The website itself is running on AWS.  The web server is running on nginx on an ec2 instance, the database is on Postgresql running on AWS RDS.  I registered the domain using aws route 53.

### Features

- Dynamic Post content
- Intricate Comment System
- A sleek and modern design
- REST Api integration

### Usage & Details
The website runs all on aws.  The web layer runs on nginx, which is running in an ec2 instance running ubuntu.  Nginx communiates with django via a unix socket running on gunicorn.
The database is running on postgresql running on aws rds.  This is a diagram of the architecture:
![Architecture diagram](https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/images/con-VPC-sec-grp.png)

### ChangeLog & Roadmap
I might eventually incorporate a Dashboard using plotly.  This would be a good way to utilize python's data visualization capabilities.

### Credits
I would not have been able to make this website with the help of djangocentral.com.  Frontend css and javascript leveraged with https://getbootstrap.com/ and https://bootswatch.com/.
