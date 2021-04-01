Name: voms-mysql-mp
Version: 1.0.0
Release: 0%{?dist}
Summary: Virtual Organization Mebership Service (MySQL metapackage)

Group:          System Environment/Libraries
License:        ASL 2.0
URL: http://italiangrid.github.com/voms

Requires: voms-admin-server
Requires: voms-admin-client
Requires: glite-info-provider-service
Requires: fetch-crl
Requires: voms-server
Requires: voms-mysql-plugin
Requires: bdii
Requires: mysql-server

BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)
BuildArch: noarch

Packager: Andrea Ceccanti <andrea.ceccanti@cnaf.infn.it>
Source : voms-mp.tar.gz

%description
The Virtual Organization Membership Service (VOMS) is an attribute authority
which serves as central repository for VO user authorization information,
providing support for sorting users into group hierarchies, keeping track of
their roles and other attributes in order to issue trusted attribute
certificates and SAML assertions used in the Grid environment for
authorization purposes.

This is a metapackage for a MySQL-based VOMS server installation.

%prep
%setup -c

%build

%install
rm -rf $RPM_BUILD_ROOT
mkdir -p $RPM_BUILD_ROOT

%clean
rm -rf $RPM_BUILD_ROOT

%files
%defattr(-,root,root)


%changelog
* Thu Apr 1 2021 Andrea Ceccanti <andrea.ceccanti at cnaf.infn.it> - 1.0.0
- Yet another packaging for the VOMS MySQL metapackage
