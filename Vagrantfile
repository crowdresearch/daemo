# -*- mode: ruby -*-
# vi: set ft=ruby :

# All Vagrant configuration is done below. The "2" in Vagrant.configure
# configures the configuration version (we support older styles for
# backwards compatibility). Please don't change it unless you know what
# you're doing.
Vagrant.configure(2) do |config|
  # The most common configuration options are documented and commented below.
  # For a complete reference, please see the online documentation at
  # https://docs.vagrantup.com.

  # Every Vagrant development environment requires a box. You can search for
  # boxes at https://atlas.hashicorp.com/search.
  # config.vm.box = "base"
  config.vm.box = "ubuntu/vivid32"

  # Disable automatic box update checking. If you disable this, then
  # boxes will only be checked for updates when the user runs
  # `vagrant box outdated`. This is not recommended.
  # config.vm.box_check_update = false

  # Create a forwarded port mapping which allows access to a specific port
  # within the machine from a port on the host machine. In the example below,
  # accessing "localhost:8080" will access port 80 on the guest machine.
  config.vm.network "forwarded_port", guest: 8080, host: 8080
  config.vm.network "forwarded_port", guest: 8000, host: 8000

  # Create a private network, which allows host-only access to the machine
  # using a specific IP.
  # config.vm.network "private_network", ip: "192.168.33.10"

  # Create a public network, which generally matched to bridged network.
  # Bridged networks make the machine appear as another physical device on
  # your network.
  # config.vm.network "public_network"

  # Share an additional folder to the guest VM. The first argument is
  # the path on the host to the actual folder. The second argument is
  # the path on the guest to mount the folder. And the optional third
  # argument is a set of non-required options.
  # config.vm.synced_folder "../data", "/vagrant_data"

  # Provider-specific configuration so you can fine-tune various
  # backing providers for Vagrant. These expose provider-specific options.
  # Example for VirtualBox:
  #
  config.vm.provider "virtualbox" do |vb|
    vb.gui = true
  #   vb.memory = "1024"
  end
  #
  # View the documentation for the provider you are using for more
  # information on available options.

  # Define a Vagrant Push strategy for pushing to Atlas. Other push strategies
  # such as FTP and Heroku are also available. See the documentation at
  # https://docs.vagrantup.com/v2/push/atlas.html for more information.
  # config.push.define "atlas" do |push|
  #   push.app = "YOUR_ATLAS_USERNAME/YOUR_APPLICATION_NAME"
  # end

  # Enable provisioning with a shell script. Additional provisioners such as
  # Puppet, Chef, Ansible, Salt, and Docker are also available. Please see the
  # documentation for more information about their specific syntax and use.
  config.vm.provision "shell", inline: <<-SHELL
     export LANGUAGE="en_US.UTF-8"
     export LC_ALL="en_US.UTF-8"
     export LANG="en_US.UTF-8"
     sudo localedef -v -c -i en_US -f UTF-8 en_US.UTF-8
     sudo apt-get update
     sudo apt-get install -y git nodejs nodejs-legacy npm python-pip python-dev postgresql-client postgresql postgresql-contrib postgresql-server-dev-all libffi-dev
     sudo npm install -g bower
     sudo -u postgres psql postgres -c "CREATE USER vagrant;"
     sudo -u postgres psql postgres -c "ALTER USER vagrant SUPERUSER;"
     sudo -u postgres psql postgres -c "CREATE DATABASE crowdsource_dev ENCODING 'UTF8';"
     sudo -u postgres psql postgres -c "CREATE DATABASE vagrant ENCODING 'UTF8';"
     sudo -u postgres psql postgres -c 'GRANT ALL PRIVILEGES ON DATABASE "crowdsource_dev" to vagrant;'
     sudo -u postgres psql postgres -c 'GRANT ALL PRIVILEGES ON DATABASE "vagrant" to vagrant;'
     cd /vagrant
     sudo pip install -r requirements.txt
  SHELL
  config.vm.provision "shell", privileged: false, inline: <<-SHELL
     cd /home/vagrant
     if [ ! -d "crowdsource-platform" ]; then
       ln -s /vagrant crowdsource-platform
     fi
     cd crowdsource-platform
     echo "cd crowdsource-platform" >> /home/vagrant/.bashrc
     if [ ! -f "local_settings.py" ]; then
       cp local_settings_default.py local_settings.py
     fi
     python manage.py makemigrations oauth2_provider
     python manage.py migrate
     python manage.py makemigrations
     python manage.py migrate
     bower install --config.interactive=false
  SHELL
end
