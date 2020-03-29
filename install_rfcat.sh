sudo apt install -y ipython python-pip python3-pip
git clone https://github.com/atlas0fd00m/rfcat.git $HOME/rfcat
cd $HOME/rfcat
sudo python setup.py build
sudo python setup.py install
sudo pip install -e .
