#!/bin/bash

hypercorn rest.service --certfile cert.pem --keyfile key.pem -b 0.0.0.0:5555