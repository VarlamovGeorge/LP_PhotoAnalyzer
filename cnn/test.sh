#!/bin/sh

curl -X POST -F "image=@pics/cat_man.jpg" localhost:8080/cnn
echo '\n'

curl -X POST -F "image=@pics/food_man.jpg" localhost:8080/cnn
echo '\n'
