# old-frontend

This was a basic frontend to be served by an apache2/php installation on the Pis themselves. I've left the code here for now, and I plan to reuse most of it for the actual site hosted on the main webserver, that aggregates data from the individual units in the field. It could still be useful at some point to have the individual units host their own webserver on a local network for low-latency/high res streaming, setup, etc., so I am not scrapping this part of the project just yet.

<!--
## Backend HTTP Server Setup
An HTTP server such as [apache2](https://httpd.apache.org/) should be configured to run php, and have it's document root configured to be the `/site` directory of this repository. Then, the data directory, which stores videos and metadata, should been created, either manually or by running `backend/sensors.py`. Once created (the default location is for the data directory /data, which is gitignored), this directory should be symlinked to `/site/data` (which is also gitignored) to make it accessible to the HTTP server. This can be achieved by running something like the following:
```
$ ln -s ../data site/data
```
(The paths are relative to the location of the symbolic link - without the `../`, we would end up with a broken link that links to itself).
-->

