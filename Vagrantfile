Vagrant.require_version ">= 2.1.0"

Vagrant.configure("2") do |config|
  config.vm.box = "ubuntu/focal64"

  config.vm.boot_timeout = 1000

  # Django HTTP port
  config.vm.network "forwarded_port", guest: 8000, host: 8000, host_ip: "127.0.0.1"

  # Define the VM and set up some things
  config.vm.hostname = "photomanager-vm"
  config.vm.define "photomanager-vagrant" do |v|
  end
  config.vm.provider "virtualbox" do |vb|
    vb.customize ["modifyvm", :id, "--natdnshostresolver1", "on"]
    vb.customize ["modifyvm", :id, "--natdnsproxy1", "on"]
    vb.customize ["modifyvm", :id, "--nictype1", "virtio"]
    vb.name = "photomanager-vagrant"
    vb.memory = 4096
  end

  # Sync this repo to /home/vagrant/photomanager
  config.vm.synced_folder ".", "/home/vagrant/photomanager", SharedFoldersEnableSymlinksCreate: false

  # Provision from a script
  config.vm.provision "shell", path: "scripts/vagrant-config/provision.sh"

  # Set SSH username
  config.ssh.username = "vagrant"
end
