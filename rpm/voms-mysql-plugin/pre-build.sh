
. /etc/os-release

packages=

if [ "${ID}" = "centos" ] && [ "${VERSION_ID}" < "8" ]; then
  packages="${packages} mysql-devel"
else
  packages="${packages} mariadb-connector-c-devel"
fi

yum install -y ${packages}
