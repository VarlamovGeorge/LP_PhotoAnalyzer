#!/bin/sh

cnn_host=localhost:5000

curl ${cnn_host}/version
echo '\n'

curl -X POST -F "image=@pics/cat_man.jpg" ${cnn_host}/cnn
echo '\n'

curl -X POST -F "image=@pics/food_man.jpg" ${cnn_host}/cnn
echo '\n'
