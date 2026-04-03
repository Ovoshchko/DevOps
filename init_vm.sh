terraform -chdir=terraform/yandex validate
terraform -chdir=terraform/yandex plan
terraform -chdir=terraform/yandex apply

IP=$(terraform -chdir=terraform/yandex output -raw external_ip)

echo "[servers]
vm ansible_host=$IP ansible_user=ubuntu" > ansible/inventory.ini

ansible-playbook ansible/install_docker.yml