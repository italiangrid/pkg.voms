%global pom_version 3.3.2
%global base_release 0

%if 0%{?rhel} == 5
%define jdk_version 1.7.0
%define bcmail_package bouncycastle146-mail
%else
%define jdk_version 1.8.0
%define bcmail_package bouncycastle-mail
%endif

%if 0%{?rhel} >= 7 || 0%{?fedora} >= 21
%define maven maven
%else
%define maven apache-maven
%endif


%if %{?build_number:1}%{!?build_number:0}
%define release_version 0.build.%{build_number}
%else
%define release_version %{base_release}
%endif

%global jar_names  voms-clients bcprov-1.61 bcmail-1.61 canl voms-api-java3 commons-io

%global orig_name voms-clients
%global _varlib /var/lib

Name: voms-clients3
Version: 3.3.1
Release: %{release_version}%{?dist}
Summary: The Virtual Organisation Membership Service command line clients

Group: Applications/Internet
License: ASL 2.0
URL: https://github.com/italiangrid/voms-clients
Source: %{orig_name}-%{version}.tar.gz
BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)

BuildArch: noarch

BuildRequires: %{maven}
BuildRequires: jpackage-utils
BuildRequires: java-%{jdk_version}-openjdk-devel

Requires: java-%{jdk_version}-openjdk

Requires: jpackage-utils

Requires(post):         %{_sbindir}/update-alternatives
Requires(postun):       %{_sbindir}/update-alternatives

Provides:       voms-clients = %{version}
Conflicts:      voms-clients <= 2.0.11-1


%description
The Virtual Organization Membership Service (VOMS) is an attribute authority
which serves as central repository for VO user authorization information,
providing support for sorting users into group hierarchies, keeping track of
their roles and other attributes in order to issue trusted attribute
certificates and SAML assertions used in the Grid environment for
authorization purposes.

This package provides the command line clients for VOMS, voms-proxy-init, 
voms-proxy-destroy and voms-proxy-info. 

%prep
%setup -q -n %{orig_name}-%{version}

%build
mvn -DskipTests -U -Dvoms-clients.libs=%{_varlib}/%{name}/lib clean package

%install
rm -rf $RPM_BUILD_ROOT

install -dm 755 $RPM_BUILD_ROOT%{_javadir}
install -dm 755 $RPM_BUILD_ROOT%{_varlib}/%{name}/lib

tar -C $RPM_BUILD_ROOT/usr -xvzf target/%{orig_name}.tar.gz --strip 1 

mv $RPM_BUILD_ROOT%{_javadir}/%{orig_name}/*.jar $RPM_BUILD_ROOT%{_varlib}/%{name}/lib

ln -s %{_varlib}/%{name}/lib/%{orig_name}-%{pom_version}.jar $RPM_BUILD_ROOT%{_javadir}/%{orig_name}.jar
ln -s %{_varlib}/%{name}/lib/%{orig_name}-%{pom_version}.jar $RPM_BUILD_ROOT%{_javadir}/%{name}.jar

# Rename to voms-proxy-*3 to avoid clashes with old C clients
mv $RPM_BUILD_ROOT/%{_bindir}/voms-proxy-init $RPM_BUILD_ROOT/%{_bindir}/voms-proxy-init3
mv $RPM_BUILD_ROOT/%{_bindir}/voms-proxy-info $RPM_BUILD_ROOT/%{_bindir}/voms-proxy-info3
mv $RPM_BUILD_ROOT/%{_bindir}/voms-proxy-destroy $RPM_BUILD_ROOT/%{_bindir}/voms-proxy-destroy3

# Rename manpages
mv $RPM_BUILD_ROOT/%{_mandir}/man1/voms-proxy-init.1 $RPM_BUILD_ROOT/%{_mandir}/man1/voms-proxy-init3.1
mv $RPM_BUILD_ROOT/%{_mandir}/man1/voms-proxy-info.1 $RPM_BUILD_ROOT/%{_mandir}/man1/voms-proxy-info3.1
mv $RPM_BUILD_ROOT/%{_mandir}/man1/voms-proxy-destroy.1 $RPM_BUILD_ROOT/%{_mandir}/man1/voms-proxy-destroy3.1

# Needed by alternatives. See http://fedoraproject.org/wiki/Packaging:Alternatives
touch $RPM_BUILD_ROOT/%{_bindir}/voms-proxy-init
touch $RPM_BUILD_ROOT/%{_bindir}/voms-proxy-info
touch $RPM_BUILD_ROOT/%{_bindir}/voms-proxy-destroy

%clean
rm -rf $RPM_BUILD_ROOT

%files
%defattr(-,root,root,-)

%ghost %{_bindir}/voms-proxy-init
%ghost %{_bindir}/voms-proxy-info
%ghost %{_bindir}/voms-proxy-destroy

%{_bindir}/voms-proxy-init3
%{_bindir}/voms-proxy-info3
%{_bindir}/voms-proxy-destroy3

%{_mandir}/man1/voms-proxy-init3.1.gz
%{_mandir}/man1/voms-proxy-info3.1.gz
%{_mandir}/man1/voms-proxy-destroy3.1.gz
%{_mandir}/man5/vomses.5.gz
%{_mandir}/man5/vomsdir.5.gz

%{_javadir}/%{name}.jar
%{_javadir}/%{orig_name}.jar

%dir %{_varlib}/%{name}/lib
%{_varlib}/%{name}/lib/*.jar

%pre

if [ $1 -eq 2 ] ; then
  ## Package upgrade, cleanup embedded dependencies
  if [ -d "%{_varlib}/%{name}/lib" ]; then
    rm -f %{_varlib}/%{name}/lib/*.jar
  fi

  ## Remove scripts if not managed with alternatives (pre v. 3.0.5)
  for c in voms-proxy-init voms-proxy-info voms-proxy-destroy; do
    if [[ -x %{_bindir}/$c && ! -L %{_bindir}/$c ]]; then
      rm -f %{_bindir}/$c
    fi
  done
fi

%preun

if [ $1 -eq 0 ] ; then
    rm -f %{_varlib}/%{name}/lib/*.jar
    rm -rf %{_varlib}/%{name}
fi

%post

# jar_names="voms-clients bcprov-1.46 bcmail-1.46 canl voms-api-java3 commons-io"

#for jarname in ${jar_names}; do
#    [ -f %{_javadir}/$jarname.jar ] ||  ( echo "$jarname not found in %{_javadir}" && exit 1 )
#    ln -fs %{_javadir}/$jarname.jar %{_varlib}/%{name}/lib
#done

%{_sbindir}/update-alternatives --install %{_bindir}/voms-proxy-init \
   voms-proxy-init %{_bindir}/voms-proxy-init3 90 \
   --slave %{_mandir}/man1/voms-proxy-init.1.gz voms-proxy-init-man %{_mandir}/man1/voms-proxy-init3.1.gz

%{_sbindir}/update-alternatives --install %{_bindir}/voms-proxy-info \
   voms-proxy-info %{_bindir}/voms-proxy-info3 90 \
   --slave %{_mandir}/man1/voms-proxy-info.1.gz voms-proxy-info-man %{_mandir}/man1/voms-proxy-info3.1.gz 

%{_sbindir}/update-alternatives --install %{_bindir}/voms-proxy-destroy \
   voms-proxy-destroy %{_bindir}/voms-proxy-destroy3 90 \
   --slave %{_mandir}/man1/voms-proxy-destroy.1.gz voms-proxy-destroy-man %{_mandir}/man1/voms-proxy-destroy3.1.gz 

%postun

if [ $1 -eq 0 ] ; then
    %{_sbindir}/update-alternatives  --remove voms-proxy-init %{_bindir}/voms-proxy-init3
    %{_sbindir}/update-alternatives  --remove voms-proxy-info %{_bindir}/voms-proxy-info3
    %{_sbindir}/update-alternatives  --remove voms-proxy-destroy %{_bindir}/voms-proxy-destroy3
fi

%changelog
* Fri Mar 9 2018 Andrea Ceccanti <andrea.ceccanti at cnaf.infn.it> - 3.3.2-0
- Packaging 3.3.2 version

* Mon Dec 4 2017 Andrea Ceccanti <andrea.ceccanti at cnaf.infn.it> - 3.3.0-0
- Packaging 3.3.0 version

* Wed Sep 7 2016 Andrea Ceccanti <andrea.ceccanti at cnaf.infn.it> - 3.0.7-1
- Packaging 3.0.7 version

* Tue Dec 10 2014 Andrea Ceccanti <andrea.ceccanti at cnaf.infn.it> - 3.0.6-1
- Packaging 3.0.6 version

* Mon Jan 27 2014 Andrea Ceccanti <andrea.ceccanti at cnaf.infn.it> - 3.0.5-1
- Fix for https://issues.infn.it/jira/browse/VOMS-495. New packaging installable
  together with with voms-clients 2.x package.

* Thu Sep 26 2013 Andrea Ceccanti <andrea.ceccanti at cnaf.infn.it> - 3.0.4-1
- Fix for https://issues.infn.it/jira/browse/VOMS-423
- Move to VOMS Java APIs v. 3.0.2

* Thu Jul 11 2013 Andrea Ceccanti <andrea.ceccanti at cnaf.infn.it> - 3.0.3-1
- Fix for https://issues.infn.it/jira/browse/VOMS-361

* Tue Jul 2 2013 Valerio Venturi <valerio.venturi at cnaf.infn.it> - 3.0.2-1
- Fix for https://issues.infn.it/jira/browse/VOMS-307
- Fix for https://issues.infn.it/jira/browse/VOMS-296

* Thu Apr 11 2013 Andrea Ceccanti <andrea.ceccanti at cnaf.infn.it> - 3.0.1-1
- Fix for https://issues.infn.it/browse/VOMS-256

* Wed Nov 14 2012 Valerio Venturi <valerio.venturi at cnaf.infn.it> - 3.0.0-1
- New version of VOMS command line clients
