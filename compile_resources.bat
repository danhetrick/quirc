
del ./quirc/resources.py

cd resources

python build_resources.py > resources.qrc

pyrcc5 -o resources.py resources.qrc
move /Y resources.py ../quirc/resources.py

del resources.qrc

cd ..
