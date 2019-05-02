rsync -avz --exclude "__history" --exclude "*~" --exclude "*.gif" --exclude "*.JPG" -e ssh . pi@198.0.0.221:/home/pi/filodometer
