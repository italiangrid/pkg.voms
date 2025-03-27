%global base_version 2.1.2
%global base_release 1

%if %{?build_number:1}%{!?build_number:0}
%define release_version 0.build.%{build_number}
%else
%define release_version %{base_release}
%endif

Name: voms
Version: %{base_version}
Release: %{release_version}%{?dist}
Summary: The Virtual Organisation Membership Service C++ APIs

Group:          System Environment/Libraries
License:        ASL 2.0
URL: https://twiki.cnaf.infn.it/twiki/bin/view/VOMS
Source: %{name}-%{version}.tar.gz

BuildRequires: libtool
BuildRequires: expat-devel
BuildRequires: pkgconfig
BuildRequires: openssl-devel%{?_isa}
BuildRequires: gsoap-devel
BuildRequires: libxslt
BuildRequires: docbook-style-xsl
BuildRequires: doxygen
BuildRequires: bison

Requires: expat
Requires: openssl

BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)

Packager: Andrea Ceccanti <andrea.ceccanti@cnaf.infn.it>

%description
The Virtual Organization Membership Service (VOMS) is an attribute authority
which serves as central repository for VO user authorization information,
providing support for sorting users into group hierarchies, keeping track of
their roles and other attributes in order to issue trusted attribute
certificates and SAML assertions used in the Grid environment for
authorization purposes.

This package provides libraries that applications using the VOMS functionality
will bind to.

%package devel
Summary:	Virtual Organization Membership Service Development Files
Group:		Development/Libraries
Requires:	%{name}%{?_isa} = %{version}-%{release}
Requires:	openssl-devel%{?_isa}
Requires:	automake

%description devel
The Virtual Organization Membership Service (VOMS) is an attribute authority
which serves as central repository for VO user authorization information,
providing support for sorting users into group hierarchies, keeping track of
their roles and other attributes in order to issue trusted attribute
certificates and SAML assertions used in the Grid environment for
authorization purposes.

This package provides header files for programming with the VOMS libraries.

%package doc
Summary:	Virtual Organization Membership Service Documentation
Group:		Documentation
%if %{?fedora}%{!?fedora:0} >= 10 || %{?rhel}%{!?rhel:0} >= 6
BuildArch:	noarch
%endif
Requires:	%{name} = %{version}-%{release}

%description doc
Documentation for the Virtual Organization Membership Service.

%package clients
Summary:	Virtual Organization Membership Service Clients
Group:		Applications/Internet

Requires:	%{name}%{?_isa} = %{version}-%{release}
Conflicts: voms-clients3 <= 3.0.4

Requires(post):         %{_sbindir}/update-alternatives
Requires(postun):       %{_sbindir}/update-alternatives

%description clients
The Virtual Organization Membership Service (VOMS) is an attribute authority
which serves as central repository for VO user authorization information,
providing support for sorting users into group hierarchies, keeping track of
their roles and other attributes in order to issue trusted attribute
certificates and SAML assertions used in the Grid environment for
authorization purposes.

This package provides command line applications to access the VOMS
services.

%package server
Summary:	Virtual Organization Membership Service Server
Group:		Applications/Internet
Requires:	%{name}%{?_isa} = %{version}-%{release}
Requires:	gsoap

Requires(pre):		shadow-utils
Requires(post):		chkconfig
Requires(preun):	chkconfig

%description server
The Virtual Organization Membership Service (VOMS) is an attribute authority
which serves as central repository for VO user authorization information,
providing support for sorting users into group hierarchies, keeping track of
their roles and other attributes in order to issue trusted attribute
certificates and SAML assertions used in the Grid environment for
authorization purposes.

This package provides the VOMS service.

%prep
%setup -q

# Fix bad permissions (which otherwise end up in the debuginfo package)
find . '(' -name '*.h' -o -name '*.c' -o -name '*.cpp' -o \
        -name '*.cc' -o -name '*.java' ')' -exec chmod a-x {} ';'
./autogen.sh

%build

%configure --disable-static --enable-docs --disable-parser-gen

make %{?_smp_mflags}

%install

rm -rf $RPM_BUILD_ROOT
make install DESTDIR=$RPM_BUILD_ROOT

rm $RPM_BUILD_ROOT%{_libdir}/*.la

mkdir -p $RPM_BUILD_ROOT%{_sysconfdir}/grid-security/vomsdir
mkdir -p $RPM_BUILD_ROOT%{_sysconfdir}/grid-security/%{name}
mkdir -p $RPM_BUILD_ROOT%{_localstatedir}/log/%{name}
mkdir -p $RPM_BUILD_ROOT%{_sysconfdir}/%{name}

mkdir -p $RPM_BUILD_ROOT%{_exec_prefix}/lib/systemd/system
cp systemd/%{name}@.service $RPM_BUILD_ROOT%{_exec_prefix}/lib/systemd/system/%{name}@.service
rm -rf $RPM_BUILD_ROOT%{_initrddir}/%{name}

mkdir -p $RPM_BUILD_ROOT%{_docdir}/%{name}-%{version}
install -m 644 -p LICENSE AUTHORS $RPM_BUILD_ROOT%{_docdir}/%{name}-%{version}

## C API documentation
mkdir -p $RPM_BUILD_ROOT%{_docdir}/%{name}-%{version}/VOMS_C_API
cp -pr  doc/apidoc/api/VOMS_C_API/html \
	$RPM_BUILD_ROOT%{_docdir}/%{name}-%{version}/VOMS_C_API
rm -f $RPM_BUILD_ROOT%{_docdir}/%{name}-%{version}/VOMS_C_API/html/installdox

mkdir -p $RPM_BUILD_ROOT%{_docdir}/%{name}-%{version}/VOMS_CC_API
cp -pr  doc/apidoc/api/VOMS_CC_API/html \
	$RPM_BUILD_ROOT%{_docdir}/%{name}-%{version}/VOMS_CC_API
rm -f $RPM_BUILD_ROOT%{_docdir}/%{name}-%{version}/VOMS_CC_API/html/installdox

for b in voms-proxy-init voms-proxy-info voms-proxy-destroy; do
  ## Rename client binaries 
  mv $RPM_BUILD_ROOT%{_bindir}/${b} $RPM_BUILD_ROOT%{_bindir}/${b}2

  ## and man pages
  mv $RPM_BUILD_ROOT%{_mandir}/man1/${b}.1 $RPM_BUILD_ROOT%{_mandir}/man1/${b}2.1

  # Needed by alternatives. See http://fedoraproject.org/wiki/Packaging:Alternatives
  touch $RPM_BUILD_ROOT/%{_bindir}/${b}
done

%clean

rm -rf $RPM_BUILD_ROOT

%post -p /sbin/ldconfig
%postun -p /sbin/ldconfig

%posttrans
# Recover /etc/vomses...
if [ -r %{_sysconfdir}/vomses.rpmsave -a ! -r %{_sysconfdir}/vomses ] ; then
   mv %{_sysconfdir}/vomses.rpmsave %{_sysconfdir}/vomses
fi

%pre server
getent group %{name} >/dev/null || groupadd -r %{name}
getent passwd %{name} >/dev/null || useradd -r -g %{name} \
    -d %{_sysconfdir}/%{name} -s /sbin/nologin -c "VOMS Server Account" %{name}
exit 0

%post server

if [ $1 -eq 2 ]; then
    chown -R %{name} /var/log/voms
    chown -R %{name} /etc/voms
fi

%preun server

%postun server

if [ "$1" = "0" ] ; then
  rm -f %{_exec_prefix}/lib/systemd/system/%{name}@.service
fi

%pre clients

if [ $1 -eq 2 ]; then 
  for c in voms-proxy-init voms-proxy-info voms-proxy-destroy; do
    if [[ -x %{_bindir}/$c && ! -L %{_bindir}/$c ]]; then
      rm -f %{_bindir}/$c
    fi
  done
fi

%post clients

%{_sbindir}/update-alternatives --install %{_bindir}/voms-proxy-init \
    voms-proxy-init %{_bindir}/voms-proxy-init2 50 \
    --slave %{_mandir}/man1/voms-proxy-init.1.gz voms-proxy-init-man %{_mandir}/man1/voms-proxy-init2.1.gz 

%{_sbindir}/update-alternatives --install %{_bindir}/voms-proxy-info \
    voms-proxy-info %{_bindir}/voms-proxy-info2 50 \
    --slave %{_mandir}/man1/voms-proxy-info.1.gz voms-proxy-info-man %{_mandir}/man1/voms-proxy-info2.1.gz

%{_sbindir}/update-alternatives --install %{_bindir}/voms-proxy-destroy \
    voms-proxy-destroy %{_bindir}/voms-proxy-destroy2 50 \
    --slave %{_mandir}/man1/voms-proxy-destroy.1.gz voms-proxy-destroy-man %{_mandir}/man1/voms-proxy-destroy2.1.gz

%postun clients

if [ $1 -eq 0 ] ; then
  %{_sbindir}/update-alternatives  --remove voms-proxy-init %{_bindir}/voms-proxy-init2
  %{_sbindir}/update-alternatives  --remove voms-proxy-info %{_bindir}/voms-proxy-info2
  %{_sbindir}/update-alternatives  --remove voms-proxy-destroy %{_bindir}/voms-proxy-destroy2
fi

%files
%defattr(-,root,root,-)
%{_libdir}/libvomsapi.so.1*
%dir %{_sysconfdir}/grid-security
%dir %{_sysconfdir}/grid-security/vomsdir
%dir %{_datadir}/%{name}
%{_datadir}/%{name}/vomses.template
%doc %dir %{_docdir}/%{name}-%{version}
%doc %{_docdir}/%{name}-%{version}/AUTHORS
%doc %{_docdir}/%{name}-%{version}/LICENSE

%files devel
%defattr(-,root,root,-)
%{_libdir}/libvomsapi.so
%{_includedir}/%{name}
%{_libdir}/pkgconfig/%{name}-2.0.pc
%{_datadir}/aclocal/%{name}.m4
%{_mandir}/man3/*

%files doc
%defattr(-,root,root,-)
%doc %{_docdir}/%{name}-%{version}/VOMS_C_API
%doc %{_docdir}/%{name}-%{version}/VOMS_CC_API

%files clients
%defattr(-,root,root,-)

%ghost %{_bindir}/voms-proxy-destroy
%ghost %{_bindir}/voms-proxy-info
%ghost %{_bindir}/voms-proxy-init

%{_bindir}/voms-proxy-destroy2
%{_bindir}/voms-proxy-info2
%{_bindir}/voms-proxy-init2
%{_bindir}/voms-proxy-fake
%{_bindir}/voms-proxy-list
%{_bindir}/voms-verify

%{_mandir}/man1/voms-proxy-destroy2.1.gz
%{_mandir}/man1/voms-proxy-info2.1.gz
%{_mandir}/man1/voms-proxy-init2.1.gz
%{_mandir}/man1/voms-proxy-fake.1.gz
%{_mandir}/man1/voms-proxy-list.1.gz

%files server
%defattr(-,root,root,-)
%{_sbindir}/%{name}

%{_exec_prefix}/lib/systemd/system/%{name}@.service

%config(noreplace) %{_sysconfdir}/sysconfig/%{name}
%dir %{_sysconfdir}/%{name}
%dir %{_sysconfdir}/grid-security/%{name}
%attr(-,voms,voms) %dir %{_localstatedir}/log/%{name}
%{_datadir}/%{name}/mysql2oracle
%{_datadir}/%{name}/upgrade1to2
%{_datadir}/%{name}/voms.data
%{_datadir}/%{name}/voms_install_db
%{_datadir}/%{name}/voms-ping
%{_datadir}/%{name}/voms_replica_master_setup.sh
%{_datadir}/%{name}/voms_replica_slave_setup.sh
%{_mandir}/man8/voms.8*

%changelog
* Thu Mar 27 2025 Enrico Vianello <enrico.vianello at cnaf.infn.it> - 2.1.2-1
- Packaging for 2.1.2-1
* Thu Jun 27 2024 Enrico Vianello <enrico.vianello at cnaf.infn.it> - 2.1.0-1
- Packaging for 2.1.0-1
* Sat Apr 10 2021 Andrea Ceccanti <andrea.ceccanti at cnaf.infn.it> - 2.1.0-0
- Packaging for 2.1.0-0
* Wed Dec 2 2020 Andrea Ceccanti <andrea.ceccanti at cnaf.infn.it> - 2.0.16-0
- Packaging for 2.0.16
* Thu Sep 24 2020 Andrea Ceccanti <andrea.ceccanti at cnaf.infn.it> - 2.0.15-1
- Packaging for 2.0.15
